# Week 3 Submission Format

Create this folder in your fork:

```text
week-03/submissions/YOUR-NAME/
```

## Suggested Structure

```text
week-03/submissions/your-name/
├── README.md
├── cidr-plan.md
├── decisions.md
├── commands/
│   ├── dynamic-discovery.sh
│   └── validation-commands.md
├── diagrams/
│   ├── week-03-vpc-architecture.drawio
│   └── week-03-vpc-architecture.png
├── screenshots/
│   ├── nat-route-masked.png
│   ├── private-ec2-session-manager-masked.png
│   ├── flow-log-accept-masked.png
│   ├── flow-log-reject-masked.png
│   ├── peering-routes-masked.png
│   ├── peering-http-success.png
│   ├── s3-gateway-endpoint-route.png
│   └── cleanup.png
└── cleanup/
    └── cleanup-checklist.md
```

## README Requirements

- Project objective and final VPC-A/VPC-B architecture
- Updated CIDR plan and subnet classifications based on routing
- NAT Gateway versus NAT Instance decision
- Cost-safe one-NAT build versus resilient same-AZ production design
- Security Group versus NACL comparison
- Stateful/stateless and ephemeral-return-port explanation
- Flow Log `ACCEPT` and `REJECT` observations
- VPC Peering routes and private HTTP validation
- S3 Gateway Endpoint route, successful read, and denied write
- Gateway versus Interface Endpoint decision
- VPC Peering versus Transit Gateway decision
- Troubleshooting notes and cleanup confirmation

## Minimum Accepted Evidence

- Architecture diagram and CIDR plan
- Private egress and route-table proof
- One Security Group rejection and one NACL behavior test
- Sanitized Flow Log `ACCEPT` and `REJECT`
- Peering routes and private HTTP `200`
- S3 endpoint prefix-list route, successful read, and expected denied write
- Cleanup confirmation
- Public learning post link

## Safety

Do not upload credentials, private keys, complete account IDs or role ARNs, MFA data, billing information, organization details, portal URLs, sensitive public IPs, internal email addresses, or unredacted console URLs. Use placeholders for dynamic identifiers.
