# Week 6 Quick Revision

## Recall

1. S3 is Regional object storage; console folders are key prefixes.
2. Bucket names must be unique in their selected namespace, and bucket name
   and Region cannot be changed after creation.
3. Keep ACLs disabled, Bucket owner enforced, and all four BPA controls on.
4. S3 Standard fits frequent access; Intelligent-Tiering fits unknown access.
5. Standard-IA is multi-AZ; One Zone-IA stores data in one AZ.
6. Glacier Flexible Retrieval and Deep Archive require a restore before use.
7. Versioning creates independent versions of the same key.
8. A normal delete in a versioned bucket creates a delete marker.
9. Lifecycle actions are configuration-driven and asynchronous.
10. SSE-S3 is simple S3-managed encryption; SSE-KMS adds KMS control, policy,
    auditability, permissions, and request cost.
11. An S3 Bucket Key reduces supported KMS request traffic.
12. A presigned URL grants temporary signed access; it does not make the bucket
    public.
13. Object Lock protects exact object versions.
14. Legal Hold has no fixed expiry; Compliance retention cannot be bypassed.
15. A manual copy creates an independent object; it is not ongoing replication.
16. SRR copies eligible new versions within one Region; CRR copies to another
    Region.
17. Live replication is asynchronous and normally not retroactive.
18. Batch Replication addresses eligible existing or previously failed objects.
19. Transfer Acceleration helps suitable long-distance transfers only when the
    accelerated endpoint is used.
20. Incomplete multipart parts remain billable until completed, aborted, or
    removed by lifecycle.
21. EFS is shared NFS; FSx selection follows the required filesystem and
    workload.

## Decision Table

| Requirement | Best direction |
|---|---|
| Frequent access | S3 Standard |
| Unknown or changing access | Intelligent-Tiering |
| Infrequent resilient data | Standard-IA |
| Recreatable single-AZ data | One Zone-IA |
| Archive with millisecond access | Glacier Instant Retrieval |
| Archive restored in minutes to hours | Glacier Flexible Retrieval |
| Lowest-cost long-term archive | Glacier Deep Archive |
| Simple default encryption | SSE-S3 |
| Customer-controlled key and audit events | SSE-KMS |
| Reduce supported S3 KMS requests | S3 Bucket Key |
| Recover normal deletion | Versioning and remove delete marker |
| Temporary private download | Presigned GET URL |
| Prevent deletion indefinitely until released | Legal Hold |
| Automatic transition and expiration | Lifecycle |
| Selected one-time object transfer | Manual copy |
| Automatic copies within one Region | SRR |
| Automatic copies to another Region | CRR |
| Existing eligible objects | S3 Batch Replication |
| Long-distance upload through edge locations | Transfer Acceleration |
| Shared Linux NFS | EFS |
| Windows SMB and Microsoft integration | FSx for Windows File Server |
| HPC parallel filesystem | FSx for Lustre |
| Automated online movement | DataSync |
| Offline migration or edge compute | Snow Family |
| Managed SFTP into S3 or EFS | Transfer Family |

## Important Traps

- A lower storage price can be offset by retrieval, request, minimum-duration,
  minimum-size, and transfer charges.
- Objects under 128 KB do not auto-tier in Intelligent-Tiering.
- Versioning does not remove old bytes; noncurrent versions still cost money.
- Suspending versioning does not delete existing versions.
- Current-version expiration in a versioned bucket normally creates a delete
  marker; configure noncurrent cleanup separately.
- S3 permission alone does not decrypt an SSE-KMS object.
- A presigned URL is a bearer credential until expiry.
- Block Public Access does not replace least-privilege IAM and bucket policies.
- Object Lock protects versions, not only the visible object key.
- Compliance mode cannot be bypassed; use it only with a short approved
  retention and a pending-cleanup plan.
- Emptying only the normal object list does not empty a versioned bucket.
- Manual copy does not automatically copy future object versions.
- Live replication does not automatically copy pre-rule objects.
- Correcting permissions does not automatically retry every `FAILED` version.
- Replication Time Control, replication metrics, CRR transfer, and destination
  storage can add cost.
- A small console upload does not prove Transfer Acceleration performance.
- The multipart sample file is conceptual and does not force multipart upload.

## Scenarios

### Scenario 1

An application has unpredictable object access and cannot tolerate retrieval
fees. Start with Intelligent-Tiering and evaluate object sizes and monitoring
cost.

### Scenario 2

A private object must be downloadable for five minutes without issuing AWS
credentials. Generate a short-lived presigned GET URL from a principal already
authorized to read the object.

### Scenario 3

A versioned object disappears after a normal delete. Show versions and remove
only the current delete marker to reveal the previous version.

### Scenario 4

A role has `s3:GetObject` but receives `AccessDenied` on an SSE-KMS object.
Check `kms:Decrypt`, the key policy, Region, explicit denies, and encryption
context conditions.

### Scenario 5

Logs should move to Standard-IA at day 30, Glacier Flexible Retrieval at day
90, expire at day 365, and abandon incomplete multipart uploads at day 7. Use
a prefix-scoped lifecycle rule and include noncurrent-version handling.

### Scenario 6

An object must not be deleted until an investigation ends, but no end date is
known. Use Object Lock Legal Hold on the required version.

### Scenario 7

New `crr/` versions must appear in Tokyo, but an older matching object also
needs copying. Use live CRR for new versions and S3 Batch Replication for the
eligible existing object.

### Scenario 8

Linux instances need shared NFS. Choose EFS. Windows applications need managed
SMB and Microsoft integration. Choose FSx for Windows File Server.

### Scenario 9

Data must move automatically over the network from on premises to AWS. Use
DataSync. If network transfer cannot meet the deadline, evaluate Snow Family.

## Day 12 Practice Questions

> **Disclaimer:** These are original educational questions modelled on the
> SAA-C03 style. They are not real exam questions or exam dumps.

### Question 1

An object under `crr/` was uploaded before its CRR rule was enabled and does not
appear in the destination. New versions replicate correctly. What should copy
the existing eligible version?

- A. Transfer Acceleration
- B. S3 Batch Replication
- C. A presigned URL
- D. EFS Replication

<details><summary>Show Answer</summary>

**Answer: B**

Live replication normally processes eligible versions created after the rule
becomes active. Batch Replication addresses eligible existing or failed
versions.

</details>

### Question 2

A company requires automatic copies of new S3 object versions in another AWS
Region. Which feature best meets the requirement?

- A. Same-Region Replication
- B. Cross-Region Replication
- C. S3 File Gateway
- D. Intelligent-Tiering

<details><summary>Show Answer</summary>

**Answer: B**

CRR asynchronously copies eligible versions to a destination bucket in a
different Region.

</details>

### Question 3

An eligible object's replication status is `FAILED`. Permissions are corrected,
but that version is not retried automatically. What is the best next action?

- A. Disable versioning
- B. Upload a new version or use Batch Replication
- C. Make the source bucket public
- D. Enable static website hosting

<details><summary>Show Answer</summary>

**Answer: B**

Correcting the configuration does not guarantee automatic retry of a failed
version. A new eligible version or Batch Replication provides the recovery
path.

</details>

### Question 4

Global clients upload large files over long distances to one S3 bucket. Which
option can route transfers through nearby AWS edge locations?

- A. Transfer Acceleration
- B. One Zone-IA
- C. Object Lock
- D. EFS Access Points

<details><summary>Show Answer</summary>

**Answer: A**

Transfer Acceleration uses an accelerated endpoint, edge locations, and the AWS
global network for suitable long-distance transfers.

</details>

### Question 5

An organization must perform automated online migration from an on-premises
NFS server into AWS storage. Which service is the best fit?

- A. Snow Family
- B. AWS DataSync
- C. S3 Glacier Deep Archive
- D. FSx for Windows File Server

<details><summary>Show Answer</summary>

**Answer: B**

DataSync provides managed online movement between supported storage systems.
Snow Family is evaluated when offline transfer or edge processing is required.

</details>

## Final Check

- [ ] I can describe bucket, object, key, prefix, metadata, and version ID.
- [ ] I can choose an S3 storage class from access and cost requirements.
- [ ] I can explain BPA, Object Ownership, IAM policy, and bucket policy.
- [ ] I can compare SSE-S3, SSE-KMS, and S3 Bucket Keys.
- [ ] I can recover a delete marker without deleting a data version.
- [ ] I can explain lifecycle behavior for current and noncurrent versions.
- [ ] I can explain presigned URL scope, permission, and expiry.
- [ ] I can distinguish Legal Hold, Governance, and Compliance retention.
- [ ] I can distinguish manual copy from S3 Replication.
- [ ] I can compare SRR, CRR, and Batch Replication.
- [ ] I can interpret `PENDING`, `COMPLETED`, `FAILED`, and `REPLICA`.
- [ ] I can explain Transfer Acceleration and multipart cleanup.
- [ ] I can choose EFS, an FSx option, or a hybrid transfer service.
- [ ] I know every Week 6 resource and hidden version that must be cleaned up.
