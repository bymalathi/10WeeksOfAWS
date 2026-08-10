# Day 6 Challenge - Secure, Connect, and Observe Two VPCs

## Objective

Extend VPC-A with controlled private egress and observability, build VPC-B as a peering target, and prove private connectivity and private S3 access without exposing sensitive information.

## Use

- VPC-A `10.10.0.0/20` with private EC2 in `10.10.12.0/24`
- Public NAT Gateway and Elastic IP
- Session Manager and a read-only EC2 role
- VPC Flow Logs delivered to CloudWatch Logs
- Security Groups and a custom Network ACL
- VPC-B `10.20.0.0/20` with an nginx target in `10.20.1.0/24`
- VPC Peering and routes in both directions
- S3 Gateway Endpoint associated with VPC-A's private route table
- Optional one-subnet Interface Endpoint
- Transit Gateway comparison only

## Constraints

- The private EC2 instance must have no public IPv4 and no inbound SSH rule.
- Use one NAT Gateway for the cost-safe learner build; document the resilient same-AZ NAT-per-AZ production extension.
- Test Security Group and NACL rejection independently so the evidence identifies the changed control.
- Configure required NACL request and ephemeral return paths before subnet association.
- VPC Peering must use non-overlapping CIDRs, routes in both directions, and least-privilege Security Group access.
- Test peering with VPC-B's private IP, not its public IP.
- Transit Gateway must not be created for this two-VPC challenge.
- The optional Interface Endpoint must be limited to one subnet and removed immediately after validation.
- Discover all dynamic IDs, IPs, and AMIs at runtime.

## Required Proof

### Private egress

- VPC-A private route to NAT Gateway
- Private EC2 with no public IPv4 and Session Manager connectivity
- Successful outbound HTTPS and NAT public-IP observation
- Explanation of the one-NAT lab versus resilient production design

### Security and observability

- One controlled Security Group `REJECT` record
- NACL lower-numbered explicit deny and recovery observation
- NACL stateless return-path failure and recovery observation
- At least one sanitized Flow Log `ACCEPT` and one `REJECT`, with field meanings
- Explanation that `ACCEPT` does not prove the application is healthy

### Private VPC connectivity

- VPC-A and VPC-B CIDR and route evidence
- Active peering relationship
- VPC-B Security Group allowing HTTP only from VPC-A's CIDR
- Private-IP HTTP `200` result from VPC-A private EC2 to VPC-B web EC2
- Explanation of why VPC Peering is non-transitive

### Private S3 access

- S3 Gateway Endpoint and AWS-managed prefix-list route
- Successful read from a private test object
- Expected `AccessDenied` for a write attempted by the read-only EC2 role
- Gateway versus Interface Endpoint decision table

## Failure Investigation

Record at least one issue and the order used to investigate it: identity, resource state, subnet association, routes in both directions, Security Group, NACL, DNS, application listener, and logs.

## Cleanup

Complete [06-cleanup.md](./06-cleanup.md) immediately after capturing sanitized evidence.

The submission must explain design choices, results, and troubleshooting. Do not reproduce the Student Guide's implementation steps.
