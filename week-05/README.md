# Week 5 - Auto Scaling and Elastic Load Balancing

AWS Zero To Hero - CloudAdhar x TrainWithShubham<br>
Sessions: Aug 1-2, 2026<br>
Course sessions: Day 9-10<br>
Exam focus: SAA-C03 Domains 1-4<br>
Main pillars: Security, Reliability, Performance Efficiency, and Cost Optimization

Week 5 builds an elastic, health-checked EC2 application. Day 9 creates a
versioned Launch Template and an ALB-backed Auto Scaling group, then proves
scale-out, scale-in, and self-healing. Day 10 compares ALB, NLB, and GWLB and
validates Layer 7 routing, weighted releases, stickiness, health, draining, and
Layer 4 load balancing. Use the Day 9 and Day 10 Student Guides for detailed
classroom support and Mini-Mock 1.

## Start Here

| Seq | Session | Focus | File |
|---:|---|---|---|
| 01 | Day 9 | Launch Templates, ASGs, health, and scaling policies | [01-auto-scaling-launch-templates.md](./01-auto-scaling-launch-templates.md) |
| 02 | Day 9 | Build and validate an ALB-backed Auto Scaling group | [02-auto-scaling-alb-lab.md](./02-auto-scaling-alb-lab.md) |
| 03 | Day 10 | Select and operate ALB, NLB, and GWLB | [03-elastic-load-balancing.md](./03-elastic-load-balancing.md) |
| 04 | Day 10 | Build Blue/Green ALB routing and an NLB | [04-elb-routing-lab.md](./04-elb-routing-lab.md) |
| 05 | Both | Document the elastic architecture and decisions | [05-architecture-exercise.md](./05-architecture-exercise.md) |
| 06 | End | Remove all billable resources | [06-cleanup.md](./06-cleanup.md) |
| 07 | End | Submit Week 5 evidence | [07-submission-format.md](./07-submission-format.md) |
| 08 | Daily | Share learning progress | [08-linkedin-post.md](./08-linkedin-post.md) |
| 09 | Review | Revise the key decisions and Mini-Mock themes | [09-quick-revision.md](./09-quick-revision.md) |

## Required Outcomes

- Create and verify a versioned Launch Template with encrypted gp3 storage,
  an IAM role, User Data, and IMDSv2 required.
- Explain how minimum, desired, and maximum capacity differ.
- Align an ASG and ALB across two Availability Zones.
- Allow backend HTTP only from the load balancer Security Group.
- Use EC2 and ELB health checks to detect infrastructure and application
  failure separately.
- Use target tracking to scale from one to two instances and back to one.
- Prove that ASG instances register with and deregister from the target group
  automatically.
- Explain step, scheduled, and predictive scaling; lifecycle hooks; warm
  pools; termination policies; instance refresh; and Mixed Instances groups.
- Select ALB, NLB, or GWLB from protocol and architecture requirements.
- Validate ALB host, path, and weighted Blue/Green routing.
- Explain target-group and target stickiness and prefer stateless sessions.
- Observe health failure, recovery, and connection draining.
- Validate NLB TCP forwarding and explain static zonal IP, TLS, and UDP choices.
- Explain GWLB appliance insertion, GENEVE UDP `6081`, and symmetric routing.

## Lab Architecture

```text
Day 9
Internet
   |
   v
cloudadhar-day9-alb (two public subnets)
   |
   v
cloudadhar-day9-tg (HTTP 80, health /health.html)
   |
   v
cloudadhar-day9-asg (min 1, desired 1, max 2)
   |-- EC2 in ap-south-1a
   `-- EC2 in ap-south-1c after scale-out

Day 10
Internet
   |
   v
cloudadhar-day10-alb
   |-- default or /app1/* -> Blue
   |-- Host api.cloudadhar.local or /app2/* -> Green
   `-- /release/* -> Blue 80 / Green 20

Blue EC2 and Green EC2 are also targets of cloudadhar-day10-nlb on TCP 80.
```

Use `ap-south-1` and two subnets in different Availability Zones. The
cost-controlled classroom ASG uses `1/1/2`; a highly available production
baseline normally uses private application subnets and at least two instances.

## Minimum Submission

- Launch Template version and secure settings
- ASG capacity, subnet, target group, health-check, and propagated-tag settings
- Healthy Day 9 target and working ALB page
- CloudWatch high alarm, ASG Activity, and `1 -> 2` scale-out evidence
- Two different Day 9 instance IDs returned through the ALB
- Stopped load, low-alarm observation, and `2 -> 1` scale-in evidence
- One controlled self-healing or troubleshooting result
- Healthy Blue and Green Day 10 targets in separate AZs
- Host, path, and approximate `80/20` weighted-routing results
- Stickiness, application-health, and draining observations
- Healthy NLB targets and TCP test
- ALB/NLB/GWLB decision table, architecture diagram, cleanup proof, and public
  learning post

## Cost and Safety

- Prefer Session Manager; do not leave SSH open to `0.0.0.0/0`.
- Never place credentials in User Data, Launch Templates, pages, or screenshots.
- Production targets belong in private subnets without public IPv4 addresses.
- Stop `stress-ng` on every instance after the scaling test.
- Delete warm pools, scaling schedules, optional listeners, EIPs, load
  balancers, target groups, public IPv4 addresses, instances, and EBS volumes.
- Do not build a fake GWLB lab with nginx; GWLB requires compatible appliances.
- Mask account IDs, ARNs, resource IDs, IPs, DNS names where sensitive,
  cookies, tokens, certificates, and billing data.

<div align="center">

[Week 4](../week-04/) | [Home](../README.md)

</div>
