# Week 8 Global Edge and DR Learn-in-Public Posts

Write in your own voice and publish only sanitized evidence.

## Day 15

```text
Week 8, Day 15 of #10WeeksOfAWS

Today I built a private S3 delivery path through CloudFront Origin Access
Control and proved that direct S3 access failed while the edge URL worked.

My cache evidence:
<X-Cache/edge result and invalidation lesson>

My private-content evidence:
<Unsigned denial and short-lived signed URL result>

I also requested my own ACM public certificate in us-east-1, completed DNS
validation from scratch, attached it to CloudFront, and tested HTTPS on my
custom hostname.

My DNS and resilience lesson:
<Weighted result plus primary failure and failback observation>

My edge-security lesson:
<WAF Count-to-Block test, Shield, or Global Accelerator decision>

I removed the temporary compute, DNS health checks, edge, signing, WAF, and S3
resources after collecting evidence.

#AWS #Route53 #CloudFront #AWSCertificateManager #AWSWAF #CloudAdhar #TrainWithShubham
```

## Day 16

```text
Week 8, Day 16 of #10WeeksOfAWS

Today I practiced disaster recovery by protecting an encrypted Mumbai EC2
workload with AWS Backup, copying the recovery point to N. Virginia, restoring
a new instance, and validating the recovered application marker.

My objectives and strategy:
<RTO, RPO, and why backup-and-restore fits>

My recovery evidence:
<Completed backup, copy, restore, and application-validation observations>

My hybrid-networking decision:
<VPN versus Direct Connect, Transit Gateway, DNS, or endpoint lesson>

The biggest lesson was that a completed backup is not proof of recovery:
target-Region quotas, KMS, networking, identity, dependencies, restore time,
and application validation all matter.

I removed resources and recovery points in both Regions after collecting
sanitized evidence.

#AWS #AWSBackup #DisasterRecovery #HybridCloud #RTO #RPO #CloudAdhar #TrainWithShubham
```

Never publish signing keys, signed URLs, validation tokens, account IDs, ARNs,
IP addresses, resource IDs, private network details, or billing data.
