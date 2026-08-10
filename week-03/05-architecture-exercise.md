# Week 3 Architecture Exercise

Create an editable diagram showing the cost-safe learner build and label the resilient production extension separately.

## Required Boundaries and Components

- AWS Region and Availability Zone boundaries
- VPC-A `10.10.0.0/20` with its four updated `/24` subnets
- VPC-B `10.20.0.0/20` with public `10.20.1.0/24` and optional private `10.20.11.0/24`
- Internet Gateways and public route tables
- NAT-Gateway-A in VPC-A Public-A
- VPC-A private EC2 without a public IPv4
- VPC-B web EC2 and its least-privilege Security Group
- VPC Peering connection and routes in both directions
- S3 Gateway Endpoint and prefix-list route
- Optional Interface Endpoint ENI and Security Group
- VPC Flow Logs to CloudWatch Logs
- Security Group boundaries and subnet NACL boundaries
- Transit Gateway as a comparison callout only, not a deployed component

## Traffic Flows to Draw

- VPC-A private EC2 -> NAT Gateway -> Internet Gateway -> internet
- VPC-A private EC2 -> VPC Peering -> VPC-B private web address -> HTTP `200`
- VPC-A private EC2 -> S3 Gateway Endpoint -> S3
- Read-only EC2 role attempting and failing `PutObject`
- Flow Log metadata path to CloudWatch Logs

## Production Extension

Show NAT-B in VPC-A Public-B with same-AZ routing from Private-B. Clearly label it as the resilient production extension, not part of the one-NAT cost-safe learner build.

## Required Decision Notes

- Route tables select paths; Security Groups and NACLs filter traffic.
- Security Groups are stateful; NACLs are stateless.
- Peering requires non-overlapping CIDRs and is non-transitive.
- Gateway Endpoints provide private S3/DynamoDB routing but do not replace IAM.
- Transit Gateway is appropriate when centralized transitive connectivity justifies its cost and design.

Save an editable diagram and an exported image. Do not include account IDs, complete role ARNs, resource IDs, public IPs, or private organizational ranges.
