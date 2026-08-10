# Day 9 Lab - ALB-Backed Auto Scaling

Build the cost-controlled `1/1/2` classroom architecture and validate behavior,
not only resource creation.

## Resources

| Resource | Name or setting |
|---|---|
| Region | `ap-south-1` |
| ALB Security Group | `cloudadhar-day9-alb-sg` |
| Web Security Group | `cloudadhar-day9-web-sg` |
| Launch Template | `cloudadhar-day9-lt` |
| Target Group | `cloudadhar-day9-tg` |
| Application Load Balancer | `cloudadhar-day9-alb` |
| Auto Scaling group | `cloudadhar-day9-asg` |
| Target tracking policy | `cloudadhar-day9-cpu50-policy` |
| EC2 Name tag | `cloudadhar-day9-web-instance` |

Add `Project=AWS-Zero-To-Hero`, `Day=09`, `Environment=Training`,
`Owner=CloudAdhar`, and `DataClassification=Training-Only`. Configure ASG tags
to propagate to new instances.

## 1. Network Controls

Select two subnets in different Availability Zones.

- Allow inbound HTTP `80` from `0.0.0.0/0` on the ALB Security Group.
- Allow inbound HTTP `80` from the ALB Security Group on the web Security
  Group.
- If direct classroom SSH is required, allow port `22` only from your IP and
  remove the rule after use. Prefer Session Manager.

## 2. Launch Template

Create version `v1-nginx-imdsv2` with:

- a currently verified Amazon Linux 2023 x86_64 AMI;
- `t3.micro`;
- the web Security Group and an SSM-capable instance profile;
- an encrypted 8 GiB gp3 root volume;
- detailed monitoring for one-minute CPU evidence;
- metadata tokens required and hop limit `1` for this direct EC2 workload;
- public IPv4 only when the classroom access method requires it; and
- User Data that installs nginx, writes an instance-identity page and creates
  `/health.html`.

The User Data must use IMDSv2 to read instance ID, instance type, Availability
Zone, and private IP. Log output to a dedicated file and
`/var/log/cloud-init-output.log`. Validate `nginx -t`, service state, port `80`,
the local home page, and the health path.

Use this validated bootstrap:

```bash
#!/bin/bash
set -euxo pipefail
exec > >(tee /var/log/cloudadhar-day9-user-data.log \
  | logger -t cloudadhar-day9-user-data -s 2>/dev/console) 2>&1

dnf install -y nginx
systemctl enable --now nginx

TOKEN=$(curl -sS --retry 5 --retry-delay 2 -X PUT \
  http://169.254.169.254/latest/api/token \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
INSTANCE_ID=$(curl -sS -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/instance-id)
INSTANCE_TYPE=$(curl -sS -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/instance-type)
AZ=$(curl -sS -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/placement/availability-zone)
PRIVATE_IP=$(curl -sS -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/local-ipv4)

cat > /usr/share/nginx/html/index.html <<EOF
<!DOCTYPE html>
<html><body style="font-family:Arial;text-align:center;padding-top:50px">
<h1>CloudAdhar Auto Scaling Lab</h1>
<h2>Application Load Balancer + Auto Scaling Group</h2>
<p>Instance ID: $INSTANCE_ID</p>
<p>Instance Type: $INSTANCE_TYPE</p>
<p>Availability Zone: $AZ</p>
<p>Private IP: $PRIVATE_IP</p>
<p>Hostname: $(hostname)</p>
</body></html>
EOF

echo "healthy" > /usr/share/nginx/html/health.html
nginx -t
systemctl restart nginx
curl -fsS http://localhost/health.html
```

Never place credentials in User Data. Create a new Launch Template version for
every change, verify it, and explicitly update the ASG to the tested version.

## 3. Target Group and ALB

Create an instance target group using HTTP `80` and:

| Health setting | Classroom value |
|---|---|
| Path | `/health.html` |
| Success code | `200` |
| Interval | 15 seconds |
| Healthy threshold | 2 |
| Unhealthy threshold | 2 |

Create an internet-facing IPv4 ALB in the same two AZs used by the ASG. Attach
the ALB Security Group and forward HTTP `80` to the target group.

## 4. Auto Scaling Group

Create the ASG from the tested Launch Template version.

- Use the same two subnets/AZs as the ALB.
- Attach the existing target group; do not manually register ASG instances.
- Enable EC2 and ELB health checks.
- Set grace period to 300 seconds and default warmup to 120 seconds.
- Set minimum `1`, desired `1`, and maximum `2`.
- Keep default termination policy and no scale-in protection for this lab.
- Add the required tags and enable propagation.

Wait for one `InService` instance, one `Healthy` target, and a working ALB page.

## 5. Target Tracking and Scale-Out

Create `cloudadhar-day9-cpu50-policy` using average ASG CPU utilization, target
`50`, default warmup 120 seconds, and scale-in enabled.

On the active instance, install and run a bounded CPU test:

```bash
sudo dnf install -y stress-ng
nohup stress-ng --cpu 2 --cpu-load 95 --timeout 10m \
  > /tmp/stress-ng.log 2>&1 &
pgrep -af stress-ng
```

Observe and capture:

1. CPU approaching the expected high range.
2. The managed high alarm entering `ALARM` after enough datapoints.
3. Desired capacity changing from `1` to `2` in ASG Activity.
4. Two `InService` instances after warmup.
5. The second target moving from `Initial` to `Healthy` automatically.
6. The ALB returning two distinct instance IDs across repeated requests.

## 6. Scale-In

Stop stress on every remaining instance and verify it is gone:

```bash
sudo pkill stress-ng || true
pgrep -af stress-ng
```

Wait for the managed low alarm and the conservative scale-in evaluation.
Capture desired capacity returning from `2` to `1` and the removed target
entering `Draining`. Do not treat a delayed scale-in as failure before checking
the alarm evaluation period, warmup, and deregistration delay.

## 7. Self-Healing and Refresh

With stable desired capacity, stop nginx on one instance. Observe the target
become unhealthy while EC2 is still running and confirm that ELB health checks
allow the ASG to replace it. Alternatively, terminate one ASG-managed instance
and watch desired capacity recover. Verify the replacement uses the expected
Launch Template version and becomes healthy.

Optional: create a harmless new Launch Template version, update desired
configuration, and use Instance Refresh with health safeguards. Keep a
known-good version for rollback.

## Troubleshooting Order

1. Region, account, and resource state
2. Launch Template version and ASG Activity reason
3. VPC, subnet, AZ, route, and Security Groups
4. Target group association, listener action, and health reason
5. User Data and application logs
6. CloudWatch metrics, alarms, warmup, and capacity limits
7. Quotas, instance-type capacity, and cost

An `Unused` target often means its AZ is not enabled on the ALB. A health-check
timeout commonly means the target Security Group, nginx listener, port, or path
is wrong. If manual termination triggers recreation, the ASG is correctly
maintaining desired capacity.

## Evidence

- Launch Template version and IMDSv2 setting
- ASG capacity, AZ, health, target group, and propagated tags
- Healthy target and working ALB page
- High alarm, scale-out Activity, and two instance IDs
- Stopped load, low-alarm observation, and scale-in Activity
- One controlled application failure and replacement result
- One troubleshooting lesson with root cause and fix
