# Day 10 Lab - ALB Blue/Green Routing and NLB

Build two distinct nginx targets, route HTTP traffic by content through an ALB,
validate a weighted release and draining, then reuse the targets behind an NLB.

## Resources

| Resource | Name |
|---|---|
| ALB Security Group | `cloudadhar-day10-alb-sg` |
| NLB Security Group | `cloudadhar-day10-nlb-sg` |
| Web Security Group | `cloudadhar-day10-web-sg` |
| Blue EC2 | `cloudadhar-day10-blue-ec2` |
| Green EC2 | `cloudadhar-day10-green-ec2` |
| Blue Target Group | `cloudadhar-day10-blue-tg` |
| Green Target Group | `cloudadhar-day10-green-tg` |
| Optional Sticky Target Group | `cloudadhar-day10-sticky-tg` |
| Application Load Balancer | `cloudadhar-day10-alb` |
| NLB Target Group | `cloudadhar-day10-nlb-tg` |
| Network Load Balancer | `cloudadhar-day10-nlb` |

Use `Project=AWS-Zero-To-Hero`, `Day=10`, `Module=Elastic-Load-Balancing`,
`Environment=Training`, `Owner=CloudAdhar`, and
`DataClassification=Training-Only` tags.

## 1. Security Groups and Targets

- ALB SG: HTTP `80` from `0.0.0.0/0` for the classroom. Production normally
  redirects HTTP to HTTPS `443`.
- NLB SG: TCP `80` from intended clients. Add TLS or UDP ports only during an
  optional test.
- Web SG: HTTP `80` from the ALB SG and NLB SG. Add HTTPS `443` from the NLB SG
  only for a TLS pass-through test. If required, allow SSH only from your IP.

Launch Blue in one `ap-south-1` AZ and Green in another. Use a verified Amazon
Linux 2023 AMI, `t3.micro`, IMDSv2 required, the web SG, and public IPv4 only
for classroom troubleshooting. Production targets belong in private subnets.

User Data on both instances must install and enable nginx, obtain instance ID
and AZ with IMDSv2, create `/health.html`, and write pages under `/`, `/app1/`,
`/app2/`, `/release/`, `/sticky/`, and `/drain/`. Blue pages must clearly say
`BLUE VERSION`; Green pages must say `GREEN VERSION`. Create a disposable
large file under `/drain/` for the slow-download test.

Use this template twice. Set `VERSION=BLUE` and `COLOR=#1565c0` for Blue; set
`VERSION=GREEN` and `COLOR=#2e7d32` for Green.

```bash
#!/bin/bash
set -euxo pipefail
exec > >(tee /var/log/cloudadhar-day10-user-data.log \
  | logger -t cloudadhar-day10-user-data -s 2>/dev/console) 2>&1

VERSION=BLUE
COLOR=#1565c0

dnf install -y nginx
systemctl enable nginx
for path in app1 app2 release sticky drain; do
  mkdir -p "/usr/share/nginx/html/$path"
done

TOKEN=$(curl -sS --retry 5 --retry-delay 2 -X PUT \
  http://169.254.169.254/latest/api/token \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
INSTANCE_ID=$(curl -sS -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/instance-id)
AZ=$(curl -sS -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/placement/availability-zone)

cat > /tmp/page.html <<EOF
<!DOCTYPE html>
<html><body style="font-family:Arial;text-align:center;padding-top:50px">
<h1 style="color:$COLOR">$VERSION VERSION</h1>
<h2>CloudAdhar Day 10 Load Balancing Lab</h2>
<p>Instance ID: $INSTANCE_ID</p>
<p>Availability Zone: $AZ</p>
</body></html>
EOF

cp /tmp/page.html /usr/share/nginx/html/index.html
for path in app1 app2 release sticky drain; do
  cp /tmp/page.html "/usr/share/nginx/html/$path/index.html"
done
echo "healthy" > /usr/share/nginx/html/health.html
dd if=/dev/zero of=/usr/share/nginx/html/drain/largefile.bin \
  bs=1M count=20
systemctl start nginx
curl -fsS http://localhost/health.html
```

Validate service state, local home page, and local health path on both targets.

## 2. Target Groups and ALB

Create Blue and Green instance target groups on HTTP `80`, using health path
`/health.html` and success code `200`. Register the matching instance in each.

Create `cloudadhar-day10-alb` as internet-facing IPv4 in the two public subnets,
attach the ALB SG, and make HTTP `80` forward to Blue by default. Wait for both
targets to become healthy and verify the default Blue page.

## 3. Host and Path Routing

Create rules in this order:

| Priority | Condition | Action |
|---:|---|---|
| 5 | Host is `api.cloudadhar.local` | Forward to Green |
| 10 | Path is `/app1/*` | Forward to Blue |
| 20 | Path is `/app2/*` | Forward to Green |
| 30 | Path is `/release/*` | Blue weight 80, Green weight 20 |
| Default | No earlier match | Forward to Blue |

Validate without creating a DNS record:

```bash
curl -H "Host: api.cloudadhar.local" http://ALB-DNS-NAME/
curl http://ALB-DNS-NAME/app1/
curl http://ALB-DNS-NAME/app2/
```

If routing is wrong, inspect priority, exact path and trailing slash, the Host
header sent by the client, and the default action.

## 4. Weighted Release and Stickiness

Run at least 50 independent requests to `/release/`, count Blue and Green, and
explain why the observed split is approximate.

```bash
for i in $(seq 1 50); do
  curl -s http://ALB-DNS-NAME/release/ |
    grep -oE "BLUE VERSION|GREEN VERSION"
done | sort | uniq -c
```

Enable target-group stickiness on the weighted action for 300 seconds. Use a
cookie jar for repeated requests and verify that one client stays with the
selected target group. Disable stickiness after the demonstration.

```bash
rm -f cloudadhar-cookies.txt
for i in $(seq 1 10); do
  curl -s -c cloudadhar-cookies.txt -b cloudadhar-cookies.txt \
    http://ALB-DNS-NAME/release/ |
    grep -oE "BLUE VERSION|GREEN VERSION"
done
```

## 5. Health and Connection Draining

Stop nginx on Green. Observe it become unhealthy and confirm that `/app2/`
cannot succeed when its matched target group has no healthy target. Restart
nginx and wait for `Initial -> Healthy`.

Set the Blue target group's deregistration delay to 30 seconds. Start a slow
download, deregister Blue, and observe `Healthy -> Draining -> Unused`. Register
it again after the demonstration.

```bash
curl --limit-rate 200k -o /tmp/cloudadhar-largefile.bin \
  http://ALB-DNS-NAME/drain/largefile.bin
```

## 6. NLB TCP Validation

Create `cloudadhar-day10-nlb-tg` with instance targets, TCP `80`, and HTTP
health path `/health.html`. Register Blue and Green.

Create an internet-facing IPv4 NLB in the same two AZs. Attach
`cloudadhar-day10-nlb-sg` during creation and forward TCP `80` to the NLB target
group. Wait for both targets to become healthy.

```bash
dig +short NLB-DNS-NAME
for i in $(seq 1 10); do
  curl -s http://NLB-DNS-NAME/ |
    grep -oE "BLUE VERSION|GREEN VERSION"
done
```

Record the static zonal addresses and explain why repeated requests need not
alternate evenly due to flow hashing and connection reuse. Enable cross-zone
only after considering zonal distribution and transfer cost.

## 7. Optional TLS, UDP, and GWLB Review

- TLS termination: NLB TLS `443` holds the certificate.
- TLS pass-through: NLB TCP `443` forwards encrypted bytes to an HTTPS backend.
- UDP: run a real UDP service and use a UDP listener, target group, Security
  Group rules, and UDP client. HTTP `curl` does not validate UDP.
- GWLB: review compatible appliance targets, GENEVE UDP `6081`, endpoint
  service, GWLB endpoint, and symmetric route-table insertion. Do not register
  nginx as a fake appliance.

## Evidence

- Blue and Green instances in different AZs with IMDSv2 required
- Healthy target groups and default Blue page
- Host rule, both path rules, and approximate weighted result
- Cookie-based stickiness result
- Unhealthy and recovered Green target
- Blue draining observation
- Healthy NLB targets, zonal IP resolution, and TCP responses
- ALB/NLB/GWLB selection notes and one troubleshooting lesson
