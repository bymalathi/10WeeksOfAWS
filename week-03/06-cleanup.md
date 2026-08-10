# Week 3 Cleanup

Cleanup order matters because resources have dependencies and time-based charges.

## Delete First

1. Optional Interface Endpoint and its unused endpoint Security Group
2. NAT Gateway; wait until it is deleted
3. NAT Gateway Elastic IP after deletion completes

## Remove Remaining Challenge Resources

- Terminate VPC-A private EC2 and VPC-B web EC2 when no longer needed.
- Delete the S3 test object and private test bucket.
- Delete the S3 Gateway Endpoint if it will not be reused.
- Delete the VPC Peering connection and remove peering routes.
- Delete VPC Flow Logs and the dedicated CloudWatch log group after evidence is saved.
- Reset NACL associations and delete custom NACLs and temporary deny rules.
- Remove temporary Security Group rules.
- Delete lab-only IAM roles, policies, Security Groups, and key pairs when unused.
- Delete VPC-B and then VPC-A only when the trainer confirms they are not needed later.

## Verification

- No NAT Gateway remains in a billable state.
- No allocated Elastic IP remains.
- No Interface Endpoint remains.
- No Week 3 EC2 instance or public IPv4 remains.
- No test S3 object or bucket remains.
- No unneeded peering connection, endpoint, Flow Log, or CloudWatch log group remains.
- No challenge resources remain in another Region.

Discover and verify resource IDs before deletion. Never run cleanup against an empty variable, an ID copied from an old screenshot, or an unrelated/default-account resource.

Add sanitized cleanup evidence to the submission.
