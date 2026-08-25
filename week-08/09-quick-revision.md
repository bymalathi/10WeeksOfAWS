# Week 8 Quick Revision

## Day 15 Recall

1. Route 53 alias records can point the zone apex to supported AWS resources.
2. Weighted routing controls relative answer weights, not an exact request ratio.
3. Failover routing needs primary/secondary records and a health decision.
4. TTL, recursive resolvers, and client caching influence DNS failover time.
5. OAC authorizes CloudFront's request to a private S3 origin.
6. OAC does not authorize viewers; signed URLs/cookies do that.
7. A cache policy controls cache-key and TTL behavior.
8. Invalidation expires selected edge objects before normal TTL expiry.
9. Protect one resource with a signed URL; use signed cookies for several paths.
   Keep the challenge URL lifetime to no more than 15 minutes.
10. CloudFront receives the public key; the signer retains the private key.
11. A CloudFront viewer certificate must be in ACM `us-east-1`.
12. ACM's validation `CNAME` differs from the application DNS record.
13. Keep the validation record for eligible managed certificate renewal.
14. Start WAF rules in Count mode before enforcing Block.
15. Shield Standard is included; Shield Advanced is paid.
16. CloudFront caches HTTP content; Global Accelerator does not cache.
17. The registrar and authoritative DNS provider can be different; edit records
    where `dig NS` points.
18. ACM validation CNAME, CloudFront application CNAME, and Route 53 subdomain
    delegation are three separate DNS operations.
19. GoDaddy, Namecheap, and Cloudflare can delegate `lab` with subdomain NS
    records; Hostinger's DNS editor currently requires the full-domain Route 53
    nameserver method for this exact routing-policy lab.

## Day 16 Recall

1. Site-to-Site VPN uses two tunnels and provides encryption over the internet.
2. Direct Connect is a private circuit and is not encrypted by default.
3. Transit Gateway is a Regional routing hub for multiple attachments.
4. Association selects an attachment's ingress route table; propagation adds
   learned attachment routes to selected TGW route tables.
5. Resolver inbound endpoints accept DNS queries from on-premises networks.
6. Resolver outbound endpoints forward selected VPC queries to external DNS.
7. Gateway endpoints support private S3/DynamoDB routing without an endpoint
   hourly charge; interface endpoints create private ENIs and are billed.
8. RTO is acceptable recovery time; RPO is acceptable data loss in time.
9. Backup/restore is lowest-cost and normally slowest to recover.
10. Pilot light keeps core services, warm standby keeps a reduced full stack,
    and active-active serves traffic from multiple Regions.
11. A backup job, copy job, and restore job are different recovery milestones.
12. A completed restore still requires application and data validation.
13. Target-Region quotas, KMS, network, IAM, secrets, and dependencies matter.
14. Restore creates new resources rather than overwriting the source.
15. A restored boot service can query IMDSv2 and render the new Region and
    instance ID; copied static text alone is weak recovery proof.
16. A `/health` response, page content, and metadata validate different layers.
17. Inter-Region TGW peering uses static routes and provides reachability, not
    workload or backup replication.
18. Achieved RTO includes detection through validation and traffic cutover;
    achieved RPO uses the latest usable recovery point at incident time.

## Decision Table

| Requirement | Best direction |
|---|---|
| Private S3 global delivery | CloudFront + OAC |
| One protected download | Signed URL |
| Several protected paths | Signed cookies |
| Canary traffic shift | Weighted routing |
| Active-passive endpoint | Failover routing + health check |
| Viewer country decision | Geolocation routing |
| Web request inspection | AWS WAF |
| Static anycast IPs without caching | Global Accelerator |
| Rapid encrypted hybrid setup | Site-to-Site VPN |
| Predictable private bandwidth | Direct Connect |
| Hub for many networks | Transit Gateway |
| On-premises resolves private AWS names | Resolver inbound endpoint |
| Private S3/DynamoDB route | Gateway VPC endpoint |
| Lowest-cost relaxed DR | Backup and restore |
| Reduced full DR environment | Warm standby |

## Important Traps

- A public S3 website endpoint cannot use OAC like the S3 REST origin.
- `403` from S3 does not prove CloudFront works; validate both paths.
- Adding every header/cookie/query to the cache key damages cache efficiency.
- ACM in the workload Region is invisible for CloudFront viewer use unless that
  Region is `us-east-1`.
- Deleting ACM's DNS validation record can prevent managed renewal.
- Changing root nameservers without recreating MX/TXT and other records can
  break email and domain services.
- Route 53 changes answers; it does not replicate data or warm a DR Region.
- A healthy network endpoint does not prove the application is correct.
- Direct Connect alone does not guarantee encryption or resilience.
- A TGW attachment needs correct TGW and VPC route tables.
- TGW peering is not required for AWS Backup cross-Region copy.
- `AdministratorAccess` is not a substitute for the approved AWS Backup service
  role policies.
- A backup in only the failed Region may not meet a Regional disaster goal.
- `Completed` restore means infrastructure recovery finished, not that the
  workload passed business validation.
- In backup-and-restore DR, validate the restored endpoint before creating or
  updating the Route 53 secondary; DNS cannot restore the workload.
- Terminating EC2 does not delete AWS Backup recovery points.

## Practice Questions

> These are original educational questions modelled on SAA-C03 style. They are
> not real exam questions or exam dumps.

### Question 1

A private S3 bucket must serve content globally, and users must not bypass the
CDN. Which design is best?

- A. S3 website hosting with public read
- B. CloudFront with OAC and a distribution-scoped bucket policy
- C. Route 53 health check directly to the private bucket
- D. Global Accelerator to the S3 object URL

<details><summary>Show Answer</summary>

**Answer: B.** OAC authenticates the distribution to the private S3 REST origin
while Block Public Access remains enabled.

</details>

### Question 2

A custom CloudFront hostname needs an Amazon-issued viewer certificate. Where
must the certificate be requested?

- A. The S3 bucket Region
- B. Any Region
- C. `us-east-1`
- D. The viewer's nearest Region

<details><summary>Show Answer</summary>

**Answer: C.** CloudFront requires its ACM viewer certificate in N. Virginia.

</details>

### Question 3

A company wants 10% of DNS answers sent to a new deployment during a canary.
Which Route 53 policy fits?

- A. Weighted
- B. Geolocation
- C. Failover
- D. Multivalue only

<details><summary>Show Answer</summary>

**Answer: A.** Weighted records support relative traffic distribution.

</details>

### Question 4

On-premises clients must resolve records in a Route 53 private hosted zone.
Which component accepts their DNS queries in AWS?

- A. Resolver outbound endpoint
- B. Resolver inbound endpoint
- C. NAT gateway
- D. Gateway VPC endpoint

<details><summary>Show Answer</summary>

**Answer: B.** An inbound endpoint provides IPs to which on-premises DNS can
forward private AWS queries.

</details>

### Question 5

A workload has relaxed RTO/RPO targets and the lowest DR cost is the priority.
Which strategy is the best starting point?

- A. Active-active
- B. Warm standby
- C. Backup and restore
- D. Global Accelerator only

<details><summary>Show Answer</summary>

**Answer: C.** Backup and restore minimizes running DR infrastructure at the
cost of longer recovery.

</details>

### Question 6

An EC2 recovery point copied to another Region has status Completed. What is
still required to prove recovery?

- A. Nothing
- B. Restore, target dependency checks, and application/data validation
- C. Delete the source immediately
- D. Create a public hosted zone only

<details><summary>Show Answer</summary>

**Answer: B.** A recovery artifact is useful only when the full restore path and
workload behavior are validated.

</details>

## Final Check

- [ ] I can separate DNS routing, edge caching, origin access, and viewer access.
- [ ] I can request and DNS-validate CloudFront ACM in `us-east-1`.
- [ ] I can explain cache hit/miss, TTL, and invalidation.
- [ ] I can choose Route 53 policies and explain DNS failover timing.
- [ ] I can compare WAF, Shield, CloudFront, and Global Accelerator.
- [ ] I can compare VPN, Direct Connect, TGW, Resolver, and VPC endpoints.
- [ ] I can define RTO/RPO and select a DR strategy.
- [ ] I can trace backup, copy, restore, validation, cutover, and cleanup.
