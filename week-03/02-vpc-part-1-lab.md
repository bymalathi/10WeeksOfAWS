# Day 5 Challenge - Build the VPC-A Foundation

## Objective

Create the VPC-A two-AZ network foundation that Day 6 will extend with private egress, observability, peering, and endpoints.

## Use

- Amazon VPC `10.10.0.0/20`
- Two Availability Zones
- Two public and two private `/24` subnets from the updated classroom plan
- Internet Gateway
- Main, public, and private route tables
- VPC Resource Map and AWS CLI or Console evidence

## Constraints

- Public-A and Public-B must use a route table with `0.0.0.0/0` targeting the Internet Gateway.
- Private-A and Private-B must remain local-only during Part 1.
- Every subnet must have an explicit intended route-table association.
- Enable public IPv4 assignment only on public subnets.
- Do not create EC2 instances, NAT Gateways, or paid endpoints in Part 1.
- Resource identifiers must be discovered dynamically; never copy IDs from screenshots.

## Required Proof

- VPC Resource Map showing four subnets across two Availability Zones
- CIDR table with total and AWS-usable addresses
- Public route table and subnet associations
- Private route table and subnet associations
- Main route table retained as a local-only fallback
- Internet Gateway attachment
- Explanation of what makes a subnet public or private

## Validation Questions

- Are all four `/24` ranges inside `10.10.0.0/20` and non-overlapping?
- Do only the public subnets receive the IGW default route?
- Are public IPv4 settings aligned with actual routing?
- Can you identify the route that wins for internal VPC traffic and explain longest-prefix match?

## Carry Forward

Keep VPC-A only when continuing directly to the Day 6 challenge. Otherwise complete [06-cleanup.md](./06-cleanup.md).

Document the architecture and evidence. Do not submit a click-by-click console tutorial.
