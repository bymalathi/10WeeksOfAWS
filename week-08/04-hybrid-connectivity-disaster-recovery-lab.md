# Day 16 Lab - Cross-Region EC2 Backup and Disaster Recovery

Build a disposable Mumbai workload, protect it with AWS Backup, copy its
recovery point to N. Virginia, restore a new instance, and validate the
recovered application. Use only your AWS account and synthetic data.

## Scope and Cost Guardrails

Mandatory: EC2, encrypted EBS, two backup vaults, cross-Region recovery-point
copy, restore, and validation.

Optional: private hosted zone, S3 gateway endpoint, and Route 53 DR failover.

Explain only: Site-to-Site VPN, Direct Connect, Transit Gateway, Resolver
endpoints, interface endpoints, and PrivateLink. Do not create these billable
connectivity resources just for evidence.

Choose the same learner prefix used on Day 15:

| Placeholder | Example | Rule |
|---|---|---|
| `<LEARNER>` | `sanket` | Short lowercase name or GitHub username |
| `<PREFIX>` | `sanket-w8` | Unique learner prefix; never use instructor names |
| `<SOURCE-PUBLIC-IP>` | Runtime value | Keep private and mask in evidence |
| `<RESTORED-PUBLIC-IP>` | Runtime value | Keep private and mask in evidence |

| Purpose | Region | Name |
|---|---|---|
| Source EC2 | `ap-south-1` | `<PREFIX>-day16-primary` |
| Source SG | `ap-south-1` | `<PREFIX>-day16-primary-sg` |
| Source vault | `ap-south-1` | `<PREFIX>-day16-primary-vault` |
| Destination KMS alias | `us-east-1` | `alias/<PREFIX>-day16-dr-backup-key` |
| Destination vault | `us-east-1` | `<PREFIX>-day16-dr-vault` |
| Destination SG | `us-east-1` | `<PREFIX>-day16-dr-sg` |
| Restored EC2 | `us-east-1` | `<PREFIX>-day16-dr-restored` |

Do not use root. Confirm both Regions have suitable VPCs/subnets and enough EC2
quota. EC2, EBS snapshots, public IPv4, backup storage/copy, and a
customer-managed KMS key can generate charges.

## Part A - Record the Recovery Design

Before building, state:

```text
Chosen workload RTO: ______________________
Chosen workload RPO: ______________________
DR strategy: Backup and restore
Reason this strategy fits: ________________
Target-Region quotas checked: _____________
Dependencies required after restore: ______
```

Explain why a completed backup alone does not prove the RTO.

## Part B - Launch the Mumbai Workload

### Create the source Security Group

1. Select **Asia Pacific (Mumbai), `ap-south-1`**.
2. Open **EC2 → Security Groups → Create security group**.
3. Name it `<PREFIX>-day16-primary-sg` and select the default or approved VPC.
4. Allow HTTP TCP 80 only from your current public IP `/32` where practical.
5. Keep default outbound access for package installation.
6. Do not open SSH globally. Use Session Manager or a temporary My-IP rule.

If you later perform the optional public Route 53 health-check exercise,
temporarily allow the documented Route 53 health-checker source ranges or
another approved narrowly scoped rule.

### Launch the source instance

Open **EC2 → Instances → Launch instances** and configure:

Launch a small Amazon Linux 2023 instance:

| Setting | Value |
|---|---|
| Name | `<PREFIX>-day16-primary` |
| Network | Public subnet in the selected VPC |
| Public IPv4 | Enabled only for this lab |
| Security Group | `<PREFIX>-day16-primary-sg` |
| Root volume | 8 GiB `gp3`, encrypted |
| Tag | `Backup=Day16` |

Select an approved key-pair/administration method. Under **Advanced details →
User data**, paste:

User data:

```bash
#!/bin/bash
set -euxo pipefail

LEARNER_NAME="Sanket" # Aliya can use "Aliya"; replace with your own name.
dnf install -y nginx

cat > /usr/local/bin/render-day16-page.sh <<SCRIPT
#!/bin/bash
set -eu
TOKEN=\$(curl -fsS -X PUT \
  -H 'X-aws-ec2-metadata-token-ttl-seconds: 21600' \
  http://169.254.169.254/latest/api/token)
INSTANCE_ID=\$(curl -fsS \
  -H "X-aws-ec2-metadata-token: \${TOKEN}" \
  http://169.254.169.254/latest/meta-data/instance-id)
REGION=\$(curl -fsS \
  -H "X-aws-ec2-metadata-token: \${TOKEN}" \
  http://169.254.169.254/latest/meta-data/placement/region)

case "\${REGION}" in
  ap-south-1) LOCATION="Mumbai"; STATUS="Production" ;;
  us-east-1) LOCATION="N. Virginia"; STATUS="DR Recovery Successful" ;;
  *) LOCATION="Recovered workload"; STATUS="Validate this Region" ;;
esac

cat > /usr/share/nginx/html/index.html <<HTML
<!doctype html><html><body style="font-family:Arial;text-align:center;padding:80px">
<h1>${LEARNER_NAME} - \${STATUS}</h1>
<h2>\${LOCATION} - \${REGION}</h2>
<p>Instance ID: \${INSTANCE_ID}</p>
<p>Protected and restored using AWS Backup</p>
<p id="marker">Synthetic recovery marker: DAY16</p>
</body></html>
HTML
printf 'healthy\n' > /usr/share/nginx/html/health
SCRIPT
chmod 755 /usr/local/bin/render-day16-page.sh

cat > /etc/systemd/system/render-day16-page.service <<'UNIT'
[Unit]
Description=Render Day 16 page from IMDSv2 metadata
Wants=network-online.target
After=network-online.target
Before=nginx.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/render-day16-page.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable render-day16-page.service nginx.service
systemctl start render-day16-page.service
systemctl start nginx.service
```

Replace `Sanket` with your own name. For example, Sanket might use a domain such
as `sanketlab.example` later, while Aliya uses her own purchased domain. Do not
copy another learner's real domain or place secrets in user data.

The render script uses IMDSv2 to discover the instance's current Region and ID.
Its systemd unit is stored on the protected EBS volume and runs at every boot.
AWS Backup does not restore EC2 launch user data as launch configuration; after
the DR instance boots, the restored unit re-renders the page using the new
instance's metadata.

Wait for both EC2 status checks. Validate `http://<SOURCE-PUBLIC-IP>/` and from
inside the instance:

```bash
sudo systemctl status nginx --no-pager
sudo ss -ltnp | grep ':80'
curl -I http://localhost
curl http://localhost/health
curl http://localhost | grep 'Synthetic recovery marker: DAY16'
curl http://localhost | grep -E 'Mumbai|ap-south-1|Instance ID'
```

Expect HTTP `200`, the exact response `healthy`, Mumbai/`ap-south-1`, and the
source instance ID shown on the page.

Record privately the instance, VPC, subnet, private IP, public IP, AMI,
architecture, IAM profile, and SG. Open the root volume details and confirm
**Encrypted = Yes** before creating a backup.

## Part C - Prepare the N. Virginia Recovery Region

In `us-east-1`:

### Check recovery capacity first

1. Open **Service Quotas → AWS services → Amazon Elastic Compute Cloud**.
2. Inspect the On-Demand vCPU quota for the planned instance family.
3. Open **VPC** and confirm the target VPC, public subnet, route table, internet
   gateway, available CIDR addresses, and Network ACL behavior.
4. Record whether public IPv4 assignment is automatic or must be configured.
5. Confirm the Region supports the source AMI architecture and planned instance
   type.

### Create the destination KMS key

1. Open **KMS → Customer managed keys → Create key**.
2. Choose **Symmetric**, **Encrypt and decrypt**, and KMS key material generated
   by KMS.
3. Configure approved key administrators and usage permissions.
4. Set alias `alias/<PREFIX>-day16-dr-backup-key` and enable rotation.
5. Do not schedule deletion while any destination recovery point uses the key.

### Create the destination vault

1. Open **AWS Backup → Backup vaults → Add backup vault**.
2. Name it `<PREFIX>-day16-dr-vault`.
3. Select the customer-managed KMS key created above.
4. Create the vault and confirm its encryption key.
5. Do not enable Backup Vault Lock for this disposable challenge.

### Prepare destination network access

1. Create `<PREFIX>-day16-dr-sg` in the target VPC.
2. Allow temporary HTTP TCP 80 from your current public IP `/32` where
   practical.
3. Select the intended public subnet and confirm its route table reaches an
   internet gateway.
4. Record the VPC ID, subnet ID, SG ID, and public-IP behavior privately for the
   restore form.

Do not enable Vault Lock for this disposable lab. Preserve the KMS permissions
required by AWS Backup and the restore role.

## Part D - Create the Source Recovery Point

Return to Mumbai.

1. Open **IAM → Roles → `AWSBackupDefaultServiceRole`**. Confirm it has
   `AWSBackupServiceRolePolicyForBackup` and
   `AWSBackupServiceRolePolicyForRestores`, or use an approved least-privilege
   equivalent. If the default role does not exist yet, select **Default role**
   in the on-demand backup form; AWS Backup can create it after you grant the
   requested IAM permission. Then return to IAM and verify both policies before
   relying on the role. Do not attach `AdministratorAccess` to make the lab
   work. The destination KMS key policy must also permit the approved backup and
   restore path.
2. Open **AWS Backup → Settings → Service opt-in** and ensure EC2 resource
   protection is enabled for the account/Region.
3. Open **Backup vaults → Add backup vault**.
4. Create `<PREFIX>-day16-primary-vault` with the default or approved encryption
   key. Do not enable Vault Lock.
5. Choose **Protected resources → Create on-demand backup**.
6. Configure:

```text
Resource type:       EC2
Instance ID:         exact <PREFIX>-day16-primary instance
Backup window:       Create backup now
Backup vault:        <PREFIX>-day16-primary-vault
IAM role:            Default AWS Backup role or approved existing role
Lifecycle/retention: short deliberate lab value allowed by policy
```

7. Choose **Create on-demand backup** once; do not repeatedly click while the
   job is starting.
8. Open **Jobs → Backup jobs**, select the job, and monitor until **Completed**.
9. Open the source vault and confirm the EC2 recovery point is visible.

Record the backup job ID, completion time, recovery-point ARN suffix, resource
ID, vault, and expiry. A running or completed-with-issues job is not acceptable
evidence.

## Part E - Copy the Recovery Point Cross-Region

From the completed source recovery point:

1. Open **AWS Backup → Backup vaults → `<PREFIX>-day16-primary-vault>`**.
2. Select the completed EC2 recovery point and choose **Copy**.
3. Configure:

```text
Destination Region: US East (N. Virginia), us-east-1
Destination vault:  <PREFIX>-day16-dr-vault
IAM role:            Default copy role or approved existing role
Retention:           deliberate disposable-lab value
```

4. Start the copy once.
5. Monitor **Jobs → Copy jobs** until **Completed**.
6. Switch the console Region to `us-east-1`, open the destination vault, and
   confirm the copied EC2 recovery point exists and uses the intended
   destination encryption.

Record the copy job ID, source/destination Regions and vaults, completion time,
and destination recovery point. Cross-Region copy contributes to RPO only after
the copy is complete.

## Part F - Simulate Failure Safely

Do not terminate the source yet. Simulate application failure by stopping Nginx
through Session Manager/Instance Connect:

```bash
sudo systemctl stop nginx
curl --max-time 5 http://localhost/health || true
```

Confirm the public HTTP request fails. This preserves the instance for safe
comparison and avoids making a destructive assumption before recovery succeeds.
Record the incident, detection, and recovery-declaration times in UTC. Do not
start the restore until the declaration timestamp has been recorded.

## Part G - Restore in N. Virginia

In `us-east-1`, open the copied recovery point and choose **Restore**.

Configure the restore explicitly rather than accepting unknown source defaults:

- a compatible small instance type;
- the selected target VPC and public subnet;
- `<PREFIX>-day16-dr-sg`;
- an approved IAM instance profile or none if the app does not require it;
- the default AWS Backup restore role or an approved restore role; and
- the source key-pair behavior and an approved management path.

AWS Backup restores the same EC2 key-pair association used by the protected
instance; the restore workflow does not let you select a different key pair.
Ensure that key still exists if it is required, or use an approved Systems
Manager path. AWS Backup also does not back up and restore launch user data.
The Nginx files, render script, and enabled systemd unit are recovered because
they are on the backed-up EBS volume. The original user-data script does not
rerun; the restored unit runs during the new instance's boot and obtains fresh
Region and instance-ID values through IMDSv2.

Start the restore and monitor **Restore jobs** until **Completed**. Restore
creates a new EC2 instance and volumes; it does not move or overwrite the
source.

Console sequence:

1. Open **AWS Backup → Backup vaults → `<PREFIX>-day16-dr-vault>`**.
2. Select the copied EC2 recovery point and choose **Restore**.
3. Select the compatible instance type.
4. Choose the planned destination VPC, subnet, and
   `<PREFIX>-day16-dr-sg`—not a source-Region identifier.
5. Review IAM instance profile, termination protection, shutdown behavior,
   monitoring, key pair, and user-data behavior.
6. Select the default AWS Backup restore role or approved equivalent.
7. Choose **Restore backup** once and record the restore job ID/start time.
8. Open **Jobs → Restore jobs**, select the job, and wait for **Completed**.

Tag the new instance `Name=<PREFIX>-day16-dr-restored`. If it has no public
IPv4, assign one only through an approved target-subnet/launch configuration or
validate privately from a managed client. Do not confuse an AWS Backup restore
success with application readiness.

## Part H - Validate the Recovered Workload

Using the timestamps recorded before recovery, confirm:

1. EC2 instance and system status checks pass.
2. The restored EBS volume is encrypted.
3. `render-day16-page.service` completed and Nginx is running.
4. The restored endpoint returns HTTP `200` and `/health` returns `healthy`.
5. The page displays **DR Recovery Successful**, N. Virginia, `us-east-1`, the
   new instance ID, and the exact synthetic recovery marker.
6. IMDSv2 independently reports `us-east-1` and the same restored instance ID.
7. Source and restored instance IDs differ.
8. Region, VPC, subnet, SG, public/private IP, IAM, and monitoring settings are
   reviewed for the DR environment.
9. Backup, copy, restore, application, and metadata proof are captured.

Run on the restored instance:

```bash
curl -I http://localhost
curl http://localhost/health
curl http://localhost | grep -E 'DR Recovery Successful|N. Virginia|us-east-1|Instance ID|DAY16'
TOKEN=$(curl -fsS -X PUT -H 'X-aws-ec2-metadata-token-ttl-seconds: 21600' \
  http://169.254.169.254/latest/api/token)
curl -fsS -H "X-aws-ec2-metadata-token: ${TOKEN}" \
  http://169.254.169.254/latest/meta-data/placement/region
curl -fsS -H "X-aws-ec2-metadata-token: ${TOKEN}" \
  http://169.254.169.254/latest/meta-data/instance-id
```

Calculate achieved objectives from recorded UTC timestamps:

```text
Achieved RTO = detection + declaration + orchestration + restore
               + configuration + validation + DNS cutover (if used)
Achieved RPO = incident time - latest usable copied recovery-point time
```

Detection is not recovery, a completed restore is not application validation,
and validation is not traffic cutover. Record each milestone separately.

Only after successful validation may you terminate the disposable source during
cleanup.

## Optional Part I - Private DNS and S3 Gateway Endpoint

For private DNS:

1. Open **Route 53 → Hosted zones → Create hosted zone**.
2. Enter `<LEARNER>.internal`, choose **Private hosted zone**, and associate the
   intended Mumbai VPC.
3. Create `app.<LEARNER>.internal` as an `A` record containing the source private
   IP.
4. From an EC2 instance inside the associated VPC, run:

```bash
getent hosts app.<LEARNER>.internal
curl "http://app.<LEARNER>.internal/"
```

5. Confirm it does not resolve from a normal public-internet client.

For S3 private routing:

1. Open **VPC → Endpoints → Create endpoint**.
2. Select **AWS services** and the Regional S3 service whose type is **Gateway**.
3. Select the intended VPC and route table used by the test instance.
4. Use Full access only for the short lab or an approved constrained endpoint
   policy.
5. Create the endpoint and inspect the route table for the S3 managed prefix
   list targeting the endpoint.
6. Test S3 access from the workload. An endpoint route alone does not prove the
   instance avoided another egress path; document how flow logs, routing, and
   removal of NAT/public egress could prove it.

## Optional Part J - Route 53 DR Failover

If you control a public hosted zone, use a learner-owned name such as
`dr.<LAB-ZONE>` and create a health check whose path is `/health`. For a
backup-and-restore design, follow this order:

1. Detect the failure and declare the recovery event.
2. Restore and configure the N. Virginia instance.
3. Validate HTTP, `/health`, page metadata, and the new instance ID.
4. Create or update the secondary failover record with the validated endpoint.
5. Query a Route 53 authoritative name server and perform the planned DNS
   cutover/failover test.
6. Restart the source only for an intentional failback test and wait for health
   status and DNS caches to converge.

A backup-and-restore secondary endpoint does not exist until recovery is
performed. A continuously available secondary is warm standby or another DR
strategy. For a production design, prefer Regional load balancers with Route 53
alias records; public EC2 IP records are only a classroom simplification.
Explain why DNS failover does not perform backup, restore, configuration, or
application validation. Remove temporary health-check ingress immediately.

Use the Day 15 domain/provider instructions. Do not create records under an
instructor's domain. The restored endpoint must pass application validation
before it becomes a failover target.

## Required Decision Notes

Complete these without creating the services:

| Scenario | Your choice and reason |
|---|---|
| Rapid encrypted hybrid connection | Site-to-Site VPN / other |
| Predictable high bandwidth | Direct Connect / other |
| Many VPC and VPN attachments | Transit Gateway / other |
| On-prem resolves AWS private names | Resolver inbound endpoint / other |
| VPC forwards a domain to on-prem DNS | Resolver outbound endpoint / other |
| Private S3 access | Gateway endpoint / other |
| Private access to a supported AWS API | Interface endpoint / other |
| Lowest-cost relaxed DR | Backup and restore / other |
| Core services always running | Pilot light / other |
| Reduced complete environment | Warm standby / other |
| Both Regions serve traffic | Active-active / other |

## Design-Only Console Walkthroughs

Inspect these console areas and complete the worksheets without choosing the
final **Create** button. These services can incur hourly, attachment, endpoint,
port-hour, query, or data-processing charges.

### Site-to-Site VPN form

Open **VPC → Customer gateways → Create customer gateway** and identify:

- the on-premises router's stable public IP;
- BGP ASN for dynamic routing or the static-routing decision;
- device/certificate-based authentication options where available; and
- the difference between the AWS customer-gateway resource and the physical
  customer device.

Then inspect **Virtual private gateways** or the Transit Gateway attachment
path. Finally open **Site-to-Site VPN connections → Create VPN connection** and
record:

```text
Target gateway type: VGW or TGW
Customer gateway:    learner's design value
Routing:             dynamic BGP or static prefixes
Tunnel options:      two tunnels, inside CIDRs, IKE/IPsec choices
```

Do not create the VPN without a real or instructor-approved customer gateway.
A resilient design configures and monitors both AWS-managed tunnels and avoids
overlapping CIDRs.

### Direct Connect form

Open **Direct Connect → Connections → Create a connection** and identify the
location, port speed, service-provider/hosted-connection path, and lead time.
Do not order a circuit.

Open **Virtual interfaces** and compare:

| VIF | Reaches | Gateway relationship |
|---|---|---|
| Private VIF | VPC private addresses | VGW or Direct Connect gateway |
| Public VIF | AWS public service prefixes | Direct Connect gateway optional |
| Transit VIF | One or more Transit Gateways | Direct Connect gateway required |

Document that Direct Connect is private connectivity but not end-to-end IPsec
encryption by default. A design that needs encryption can run VPN over Direct
Connect where supported and appropriate.

### Transit Gateway form and route tables

Open **VPC → Transit Gateways**, **Transit Gateway attachments**, and **Transit
Gateway route tables**. Without creating resources, map:

1. a Mumbai VPC attachment;
2. a DR VPC attachment to a separate `us-east-1` TGW;
3. a VPN or Direct Connect gateway path;
4. the one TGW route-table association used for ingress lookup by each
   attachment;
5. the route tables into which each attachment propagates routes;
6. any deliberate static or blackhole route; and
7. an inter-Region TGW peering attachment and its required static TGW routes;
   and
8. the matching subnet/VPC route-table entries required on both sides.

Association, propagation, VPC routes, and on-premises routes are different
configuration layers. Transit Gateway is Regional. Inter-Region peering provides
network reachability only, uses static routes, and does not copy application
data, EBS volumes, backups, or DNS records. AWS Backup cross-Region copy does not
require TGW peering. A TGW attachment alone does not create end-to-end
reachability.

### Route 53 Resolver forms

Open **Route 53 Resolver → Inbound endpoints** and identify two subnets in
different AZs, Security Group UDP/TCP 53 rules from the on-premises resolver,
and the endpoint IPs to which on-premises DNS would forward AWS-private zones.

Open **Outbound endpoints** and **Rules**. Record the on-premises target DNS IPs,
domain suffix, UDP/TCP 53 path, VPC rule associations, and sharing decision.

```text
On premises -> inbound endpoint -> VPC Resolver -> private hosted zone
VPC Resolver -> outbound rule/endpoint -> on-premises DNS
```

Do not create Resolver endpoints for screenshots; each endpoint uses multiple
ENIs/IPs and can incur ongoing charges.

### Interface endpoint and PrivateLink forms

Open **VPC → Endpoints → Create endpoint** and compare:

- Gateway endpoint: S3/DynamoDB route-table target; no endpoint ENI.
- Interface endpoint: private ENIs, subnet/AZ selection, Security Groups,
  private DNS, hourly and data-processing considerations.
- Endpoint service/PrivateLink: privately publish a provider service behind a
  supported load balancer to consumer interface endpoints.

Do not create an interface endpoint solely for evidence.

## Service-Quota Evidence

Record a sanitized yes/no readiness table for both Regions:

| Dependency | Mumbai sufficient? | N. Virginia sufficient? | Remediation/lead time |
|---|---|---|---|
| EC2 On-Demand vCPUs |  |  |  |
| EBS capacity, IOPS, and throughput |  |  |  |
| VPCs/subnets/routes/SGs |  |  |  |
| ENIs and subnet IP availability |  |  |  |
| Public IPv4/EIP need |  |  |  |
| AWS Backup copy/restore concurrency |  |  |  |
| KMS key and permissions |  |  |  |
| TGW/VPN/DX quotas if selected |  |  |  |
| Resolver endpoints/rules if selected |  |  |  |

Do not publish quota values that reveal sensitive account capacity. The
evidence should show that the dependency was checked and whether action is
required.

## Troubleshooting Order

### Source webpage does not open

Check both EC2 status checks, Nginx status, TCP 80 listener, user-data logs,
Security Group source, subnet route table, public IPv4, and Network ACL.

### Backup job remains Pending or fails

Confirm EC2 service opt-in, exact Region, AWS Backup service role, source
instance state, KMS permissions, and the job's Status message. Do not delete the
source while the backup is incomplete.

### Cross-Region copy fails

Check destination Region/vault, KMS key state and policy, AWS Backup role,
recovery-point state, and whether the source encryption/key arrangement
supports the copy. Read the copy job's Status message before retrying.

### Restore job is Completed but no webpage is reachable

1. Find the new EC2 instance from the restore job's resource link.
2. Confirm the target VPC, subnet, SG, and public/private IP behavior.
3. Confirm both EC2 status checks.
4. Use an approved management path to inspect Nginx and port 80.
5. Remember that restore does not automatically adapt page text, DNS, secrets,
   or configuration to the new Region.

### Restored instance has no public IPv4

This can be valid. Validate privately from a managed client, or deliberately
associate an approved public endpoint/EIP path for the lab. Do not replace the
Security Group with an unrestricted one merely to make the page reachable.

### Destination vault or KMS key cannot be deleted

Delete only lab recovery points through AWS Backup, wait for deletion, confirm
the vault is empty, remove all dependencies, and schedule KMS deletion last.
Never delete a key needed by a retained recovery point.

## Official References

- [AWS Backup cross-Region copies](https://docs.aws.amazon.com/aws-backup/latest/devguide/cross-region-backup.html)
- [Restore an EC2 instance with AWS Backup](https://docs.aws.amazon.com/aws-backup/latest/devguide/restoring-ec2.html)
- [AWS Backup service opt-in](https://docs.aws.amazon.com/aws-backup/latest/devguide/assigning-resources.html)
- [Route 53 private hosted zones](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/hosted-zones-private.html)
- [VPC gateway endpoints](https://docs.aws.amazon.com/vpc/latest/privatelink/gateway-endpoints.html)
- [Disaster recovery strategies](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html)
- [Centralized deployment model for Transit Gateway](https://docs.aws.amazon.com/prescriptive-guidance/latest/integrating-third-party-firewall-appliances/centralized-deployment-model.html)
- [Hybrid DNS with Route 53 Resolver](https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/set-up-dns-resolution-for-hybrid-networks-in-a-multi-account-aws-environment.html)
- [Automate inter-Region Transit Gateway peering](https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/automate-aws-transit-gateway-peering-attachments-in-a-multi-region-organization.html)
- [AWS Backup restore testing](https://docs.aws.amazon.com/aws-backup/latest/devguide/restore-testing.html)

## Validation Checklist

- [ ] Source page, `/health`, IMDSv2 metadata, marker, and encryption are proven
- [ ] Target-Region network, quota, KMS, and SG dependencies are checked
- [ ] Source recovery point is Completed
- [ ] Cross-Region copy job is Completed
- [ ] Destination vault contains the encrypted copied recovery point
- [ ] Restore job is Completed and creates a different EC2 instance
- [ ] Restored page shows `us-east-1`, its new instance ID, and the marker
- [ ] Restored `/health` returns `healthy`
- [ ] Achieved RTO and RPO are calculated from recorded UTC milestones
- [ ] Hybrid and DR strategy decisions are completed
- [ ] Cleanup is completed in Mumbai and N. Virginia

Continue with [Week 8 cleanup](./06-cleanup.md).
