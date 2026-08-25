# Week 8 Architecture Exercise

Draw two production-oriented diagrams: one for the Day 15 global-delivery path
and one for the Day 16 hybrid-connectivity and disaster-recovery path.

Use the supplied [hybrid and multi-Region DR reference architecture](./Hybrid%20Conectivity%20and%20Multi%20region%20disaster%20recovery.png)
as a learning reference. Redraw it with your own labels and decisions; do not
present the supplied image as your personal deliverable.

## Diagram 1 - Edge Delivery and Security

- Users and authoritative DNS
- Route 53 records, routing policy, health checks, and TTL boundary
- ACM DNS-validation record and a separate application record
- ACM viewer certificate in `us-east-1`
- CloudFront distribution, cache behaviors, HTTPS, and invalidation path
- AWS WAF web ACL and Shield Standard
- Trusted key group and signed URL/cookie authorization boundary
- Private S3 origin, OAC, Block Public Access, and distribution-scoped policy
- Primary and secondary Regional application endpoints
- A stated Global Accelerator decision boundary
- Cache-hit, cache-miss, and blocked direct-origin paths

## Diagram 2 - Hybrid Connectivity and Recovery

- On-premises network with redundant connectivity choice
- Customer gateway, Site-to-Site VPN tunnels and/or Direct Connect path
- Transit Gateway attachments and segmented route tables where appropriate
- Route 53 Resolver inbound/outbound endpoints and forwarding direction
- Private hosted zone and VPC endpoint decisions
- Mumbai source EC2 and encrypted EBS
- Mumbai AWS Backup vault and completed recovery point
- Cross-Region copy to a KMS-encrypted N. Virginia vault
- Restored EC2, target VPC/subnet/SG, validation, and traffic cutover
- Dynamic `/health` plus IMDSv2 Region and restored instance-ID validation
- Monitoring, alarms, logs, backup/copy/restore jobs, and cost controls

## Required Annotations

Label:

1. DNS resolution, viewer HTTPS, cache hit, cache miss, and OAC-signed request.
2. The exact trust boundary for S3 origin access and viewer authorization.
3. Health-check direction and where DNS caching can extend failover time.
4. Hybrid routes in both directions and whether transport is encrypted.
5. Backup completion, cross-Region copy, restore, validation, and DNS cutover.
6. Detection, declaration, orchestration, restore, configuration, validation,
   and DNS cutover as separate RTO milestones.
7. The latest usable copied recovery point used for achieved RPO.
8. Regional TGWs/peering as reachability, separate from AWS Backup data copy.
9. Services created hands-on versus design-only services.

## Decision Table

| Requirement | Selection | Why | Main trade-off |
|---|---|---|---|
| DNS routing policy |  |  |  |
| Viewer private-content method |  |  |  |
| CloudFront origin authorization |  |  |  |
| Edge request protection |  |  |  |
| VPN versus Direct Connect |  |  |  |
| Hybrid DNS direction |  |  |  |
| Gateway versus interface endpoint |  |  |  |
| DR strategy |  |  |  |
| Backup/copy frequency |  |  |  |
| Recovery traffic cutover |  |  |  |

## Failure Walkthrough

Write 300-500 words that trace:

1. normal request flow;
2. an unhealthy primary application endpoint;
3. an unavailable source Region;
4. selection and restore of a destination recovery point;
5. application and data validation before cutover;
6. DNS or endpoint traffic change; and
7. controlled failback after the source is safe.

Do not claim zero downtime or zero data loss unless the architecture and tested
measurements prove it.

## Deliverables

Export `day15-edge.png` and `day16-hybrid-dr.png` with readable labels. Remove
account IDs, resource IDs, IP addresses, ARNs, private hostnames, certificate
tokens, and other sensitive operational details. A single PDF is acceptable
only when it contains two clearly separated, readable diagrams.
