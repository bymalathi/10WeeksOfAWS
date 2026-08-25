# Week 8 Submission Format

Document Day 15 and Day 16 in one Week 8 submission.

```text
week-08/submissions/<github-username>/
├── README.md
├── day15-edge.png
├── day16-hybrid-dr.png
└── evidence/
    ├── day15-edge-and-dns/
    ├── day16-hybrid-and-dr/
    └── cleanup/
```

## README Template

```markdown
# Week 8 - Global Edge, Hybrid Connectivity, and Disaster Recovery

## Learner
- Name:
- GitHub:
- LinkedIn:
- Learner resource prefix:
- Domain/DNS provider used:
- Primary Region:
- DR Region:

## Day 15
- DNS record and routing-policy decisions:
- Private S3 and OAC result:
- Cache hit and invalidation result:
- Signed URL authorization result:
- ACM request Region and DNS-validation result:
- ACM validation record versus application record:
- Route 53 delegation method or approved exception:
- Custom HTTPS hostname result:
- Weighted routing observation:
- 80/20 versus 50/50 comparison:
- Failover and failback observation:
- WAF Count/Block result:
- Shield and Global Accelerator decision:
- Troubleshooting lesson:

## Day 16
- VPN versus Direct Connect decision:
- Transit Gateway and hybrid DNS decision:
- Private endpoint decision:
- Workload RTO and RPO:
- DR strategy and reason:
- Source backup result:
- Cross-Region copy result:
- Restore and application-validation result:
- `/health` result and IMDSv2 Region/instance-ID proof:
- Source versus restored instance ID:
- AWS Backup service-role policy check:
- Measured recovery observations:
- Achieved RTO milestone calculation:
- Achieved RPO recovery-point calculation:
- Target-Region dependency/quota finding:
- Troubleshooting lesson:

## Architecture Explanation
Write 300-500 words.

## Cleanup
- Day 15 EC2, DNS, health checks, CloudFront, WAF, S3 and signing keys:
- ACM certificate and validation-record decision:
- Day 16 EC2, EBS, backup recovery points and vaults:
- KMS, IAM, Security Groups and optional network resources:
- Regions and global consoles checked:

## Reflection
1. Why are the ACM validation record and CloudFront application record different?
2. Why can DNS failover take longer than the health-check failure threshold?
3. When would signed cookies be more suitable than a signed URL?
4. How do VPN, Direct Connect and Transit Gateway solve different problems?
5. Why does a completed recovery point not prove the workload RTO?
```

## Day 15 Evidence Checklist

- [ ] Learner-created ACM request in `us-east-1`
- [ ] ACM DNS-validation `CNAME` and `Issued` status
- [ ] Learner-owned domain naming map and authoritative-provider proof
- [ ] Four Route 53 `NS` values delegated correctly, or documented Hostinger
      full-domain Route 53 method/approved exception
- [ ] Separate custom-domain DNS record and valid HTTPS result
- [ ] S3 Block Public Access enabled and direct object denial
- [ ] Distribution-scoped OAC bucket policy and CloudFront success
- [ ] `X-Cache`, `Age`, and edge-location evidence
- [ ] Version 2 visible after `/index.html` invalidation
- [ ] Trusted key group and `private/*` behavior
- [ ] Unsigned `403`, signed `200`, and expiry explanation
- [ ] Healthy Mumbai and N. Virginia checks
- [ ] Weighted authoritative-DNS query result
- [ ] `80/20` and `50/50` weighted-routing observations
- [ ] Primary answer, secondary failover, and primary failback
- [ ] WAF Count and temporary Block evidence with access restored
- [ ] Shield/Global Accelerator decision without paid-resource creation
- [ ] Cleanup proof and Day 15 public-post link

## Day 16 Evidence Checklist

- [ ] Encrypted Mumbai EC2 source, `/health`, metadata, and synthetic marker
- [ ] Backup role has approved backup and restore policies, not admin access
- [ ] RTO, RPO, and backup/restore strategy statement
- [ ] Target-Region network, quota, KMS, and dependency check
- [ ] Completed source backup job and recovery point
- [ ] Completed cross-Region copy job
- [ ] Destination vault contains encrypted copied recovery point
- [ ] Completed restore job and distinct restored instance
- [ ] Restored page shows DR success, `us-east-1`, new ID, and marker
- [ ] Restored `/health` returns `healthy`; IMDSv2 confirms Region and ID
- [ ] Detection-to-cutover RTO and latest-usable-copy RPO are calculated
- [ ] VPN/Direct Connect, TGW, Resolver, and endpoint decisions
- [ ] Optional private DNS/endpoint/failover evidence clearly marked optional
- [ ] Cleanup proof in both Regions and Day 16 public-post link
- [ ] `day15-edge.png`, `day16-hybrid-dr.png`, and 300-500 word explanation

Mask account IDs, ARNs, resource IDs, IP addresses, hosted-zone IDs, certificate
validation tokens, signed URLs, private keys, private DNS, console URLs, and
billing information. A certificate's public domain name may be shown only if
you intentionally want it public.
