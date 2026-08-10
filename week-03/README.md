# Week 3 - VPC Foundations, Security, NAT, and Endpoints

AWS Zero To Hero - CloudAdhar x TrainWithShubham<br>
Sessions: Jul 18-19, 2026<br>
Course sessions: Day 5-6<br>
Exam focus: SAA-C03 Domains 1-4<br>
Main pillars: Security, Reliability, Performance, and Cost Optimization

Week 3 builds and validates a two-VPC AWS network. Learners create a cost-safe private egress path, prove stateful and stateless filtering, connect VPCs privately, add private S3 access, and use VPC Flow Logs as troubleshooting evidence.

The repository provides challenge outcomes and evidence requirements. Use the course Student Guide for detailed implementation support.

## Start Here

| Seq | Session | Focus | File |
|---:|---|---|---|
| 01 | Day 5 | VPC, CIDR, subnets, and routing | [01-vpc-cidr-subnets-routing.md](./01-vpc-cidr-subnets-routing.md) |
| 02 | Day 5 | Build the VPC-A foundation | [02-vpc-part-1-lab.md](./02-vpc-part-1-lab.md) |
| 03 | Day 6 | NAT, SGs, NACLs, endpoints, peering, and Flow Logs | [03-vpc-security-and-connectivity.md](./03-vpc-security-and-connectivity.md) |
| 04 | Day 6 | Complete the VPC-A/VPC-B validation challenge | [04-vpc-part-2-lab.md](./04-vpc-part-2-lab.md) |
| 05 | Both | Document the final architecture | [05-architecture-exercise.md](./05-architecture-exercise.md) |
| 06 | End | Remove billable resources safely | [06-cleanup.md](./06-cleanup.md) |
| 07 | End | Submit evidence | [07-submission-format.md](./07-submission-format.md) |
| 08 | Daily | Share learning progress | [08-linkedin-post.md](./08-linkedin-post.md) |
| 09 | Review | Revise the key decisions | [09-quick-revision.md](./09-quick-revision.md) |

## Updated Classroom Standard

This CIDR plan supersedes earlier Week 3 drafts. Resource IDs, AMI IDs, account IDs, endpoint IDs, ENI IDs, and public/private host addresses must be discovered dynamically.

| Resource | CIDR | Purpose |
|---|---|---|
| VPC-A | `10.10.0.0/20` | Primary lab VPC |
| VPC-A-Public-Subnet-A | `10.10.1.0/24` | NAT Gateway in AZ A |
| VPC-A-Public-Subnet-B | `10.10.2.0/24` | Public tier in AZ B |
| VPC-A-Private-Subnet-A | `10.10.12.0/24` | Private EC2 in AZ A |
| VPC-A-Private-Subnet-B | `10.10.11.0/24` | Private tier in AZ B |
| VPC-B | `10.20.0.0/20` | Peering target VPC |
| VPC-B-Public-Subnet-A | `10.20.1.0/24` | nginx validation target |
| VPC-B-Private-Subnet-A | `10.20.11.0/24` | Optional private workload |

## Required Outcomes

- Explain the private EC2 -> NAT Gateway -> Internet Gateway path.
- Compare a cost-safe one-NAT lab with a resilient same-AZ NAT design.
- Prove one controlled Security Group rejection.
- Prove NACL rule order and stateless return-path behavior separately.
- Produce at least one sanitized Flow Log `ACCEPT` and one `REJECT` record.
- Validate private HTTP connectivity from VPC-A to VPC-B over VPC Peering.
- Validate an S3 Gateway Endpoint prefix-list route and successful private read.
- Prove that the endpoint does not grant IAM authorization by showing a denied write from a read-only role.
- Compare Gateway and Interface Endpoints.
- Explain why Transit Gateway is previewed but not provisioned for two VPCs.

## Minimum Submission

- Final VPC-A/VPC-B architecture diagram and CIDR plan
- Public, private, NAT, peering, and S3 endpoint route evidence
- Private EC2 Session Manager and NAT egress evidence
- Sanitized Flow Log `ACCEPT` and controlled `REJECT` evidence
- Security Group and NACL test observations
- Private peering HTTP `200` result
- S3 Gateway Endpoint route and read/denied-write result
- NAT, endpoint, peering, and cleanup decisions in the learner's own words
- Cleanup confirmation and public learning post link

## Cost and Safety Rules

- NAT Gateway, Interface Endpoint, Elastic IP, public IPv4, EC2, and CloudWatch Logs can create charges.
- Create an Interface Endpoint only as an optional short-lived validation and delete it immediately.
- Preview Transit Gateway only; do not provision it for this two-VPC challenge.
- Use Session Manager instead of opening SSH to the internet.
- Delete the Interface Endpoint first, then the NAT Gateway; wait for NAT deletion before releasing its Elastic IP.
- Never publish credentials, account IDs, complete role ARNs, organization information, portal URLs, billing details, or unredacted sensitive output.

<div align="center">

[Week 2](../week-02/) | [Home](../README.md)

</div>
