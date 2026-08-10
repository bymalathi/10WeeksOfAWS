# Week 6 Submission Format

Keep Day 11 and Day 12 evidence in the same Week 6 submission.

```text
week-06/submissions/<github-username>/
├── README.md
├── architecture.png
└── evidence/
    ├── day11-s3/
    ├── day12-storage/
    └── cleanup/
```

## README Template

```markdown
# Week 6 - Amazon S3 and Storage

## Learner
- Name:
- GitHub:
- LinkedIn:
- Primary Region:

## Day 11
- Source-bucket security controls:
- Destination SSE-KMS and Bucket Key:
- Storage-class decisions:
- Version and delete-marker recovery:
- Manual copy and encryption result:
- Normal URL denial:
- Presigned URL result and expiry:
- Lifecycle rule:
- Object Lock Legal Hold result:
- Troubleshooting lesson:

## Day 12
- Source, SRR destination, and CRR destination Regions:
- SRR rule and version results:
- CRR rule and version results:
- Pre-rule object result:
- Unmatched-prefix result:
- Transfer Acceleration review:
- Multipart cleanup rule:
- EFS and FSx review:
- Hybrid-storage decisions:
- Optional Compliance or website result:

## Architecture Decision
Write 250-400 words.

## Cleanup
- Source bucket and versions:
- Destination bucket and versions:
- Object Lock bucket and protected versions:
- Multipart uploads:
- KMS key:
- Replication rules and IAM role:
- Transfer Acceleration:
- Optional website and Compliance cleanup:
- Public-access controls:

## Reflection
1. Which S3 control protects confidentiality, and which protects recovery?
2. Why is a presigned URL different from making a bucket public?
3. Which storage-class or lifecycle decision is easiest to get wrong on cost?
4. Why did pre-rule objects remain only in the source?
5. When would you choose DataSync instead of Snow Family?
```

## Day 11 Evidence Checklist

- [ ] Source: Bucket owner enforced, BPA on, versioning, and SSE-S3
- [ ] Destination: BPA on, versioning, SSE-KMS, correct KMS key, and Bucket Key
- [ ] Standard and Intelligent-Tiering object properties
- [ ] Two version IDs and a delete marker
- [ ] Recovered object after deleting only the delete marker
- [ ] Successful manual copy into `copied/private-report.txt`
- [ ] Destination-object SSE-KMS validation
- [ ] Normal private Object URL denied
- [ ] Controlled public-policy denial while BPA remains on
- [ ] Presigned access success without showing the URL
- [ ] Presigned access failure after expiry
- [ ] Enabled `logs-transition-and-cleanup` lifecycle timeline
- [ ] Object Lock enabled and Legal Hold on the exact version
- [ ] Controlled delete denial and successful cleanup after Legal Hold off
- [ ] Day 11 architecture and decision table
- [ ] Complete cleanup evidence and Day 11 LinkedIn link

## Day 12 Evidence Checklist

- [ ] Three private, versioned SSE-S3 buckets in the intended Regions
- [ ] Enabled `srr-prefix-rule` and `crr-prefix-rule`
- [ ] SRR source `COMPLETED` and destination `REPLICA` evidence
- [ ] SRR destination contains Versions 1 and 2
- [ ] CRR source `COMPLETED` and destination `REPLICA` evidence
- [ ] CRR destination contains Versions 1 and 2
- [ ] `srr/before-rule.txt` and `crr/before-rule.txt` remain source-only
- [ ] `other/no-replication-demo.txt` remains source-only
- [ ] Transfer Acceleration configuration reviewed
- [ ] Seven-day incomplete multipart cleanup rule
- [ ] Existing EFS configuration and TCP `2049` review
- [ ] FSx family and hybrid-storage decision table
- [ ] Optional Compliance denial and pending-cleanup note, if performed
- [ ] Optional website and error page plus restored BPA, if performed
- [ ] Complete Day 12 cleanup and LinkedIn link

Mask account IDs, ARNs, bucket/object URLs, presigned URLs, access keys, session
tokens, email addresses, organization data, private object contents, and
billing information.
