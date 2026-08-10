# Week 5 Architecture Exercise

Draw one production-oriented architecture that improves the classroom labs.

## Required Components

- Route 53 or client entry point
- Internet-facing ALB across two public subnets
- Application targets in private subnets across at least two AZs
- Auto Scaling group with minimum and desired capacity at least two
- Versioned Launch Template with IMDSv2, encrypted storage, and an IAM role
- Target group with a dedicated health endpoint
- Target tracking and CloudWatch alarms
- NAT or a Golden AMI strategy for package/bootstrap dependencies
- Central logs, metrics, and notifications
- Optional WAF and HTTPS certificate
- Optional Blue/Green weighted target groups
- Optional NLB or GWLB path only when the requirements justify one

## Decision Table

Complete in your own words:

| Decision | Classroom choice | Production choice | Reason |
|---|---|---|---|
| Instance subnets | Public |  |  |
| ASG capacity | `1/1/2` |  |  |
| Launch Template reference | Tested version |  |  |
| Scaling metric | Average CPU 50% |  |  |
| Health sources | EC2 and ELB |  |  |
| Listener | HTTP `80` |  |  |
| Release method | Manual 80/20 |  |  |
| Session state |  |  |  |
| Load balancer type |  |  |  |

## Failure Review

Explain the expected response to:

1. One application process failing while EC2 remains running.
2. One Availability Zone becoming unavailable.
3. A bad Launch Template version.
4. Green targets becoming unhealthy during a weighted release.
5. A scale-in event while requests are still active.
6. A Spot interruption in a Mixed Instances group.

## Architecture Explanation

Write 250-400 words covering requirement, choice, reason, failure behavior,
security, observability, rollback, and cost. Include why ALB, NLB, or GWLB is
the correct choice rather than naming all three without a requirement.
