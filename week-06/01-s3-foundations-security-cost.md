# Amazon S3 Foundations, Security, and Cost

Amazon S3 is Regional object storage. A bucket contains objects; each object
has data, a key, metadata, and optionally a version ID. The console's folders
are prefixes within object keys, not directories on a block filesystem.

Example:

```text
Bucket: cloudadhar-s3-day11-<unique-suffix>
Key:    documents/private-report.txt
Prefix: documents/
```

Bucket names must be unique within their namespace. A bucket's name and Region
cannot be changed after creation.

## Storage-Class Decisions

| Storage class | Best use | Resilience scope | Key cost behavior |
|---|---|---|---|
| S3 Standard | Frequently accessed data | At least 3 AZs | No minimum duration or retrieval fee |
| S3 Intelligent-Tiering | Unknown or changing access | At least 3 AZs | Monitoring charge; no retrieval fee |
| S3 Standard-IA | Long-lived, monthly access | At least 3 AZs | 30-day minimum, 128 KB minimum, retrieval fee |
| S3 One Zone-IA | Recreatable infrequent data | One AZ | 30-day minimum, 128 KB minimum, retrieval fee |
| S3 Express One Zone | Latency-sensitive workloads | One AZ | Designed for very low-latency access |
| Glacier Instant Retrieval | Archive with millisecond retrieval | At least 3 AZs | 90-day minimum and retrieval fee |
| Glacier Flexible Retrieval | Archive accessed about yearly | At least 3 AZs | Restore first; 90-day minimum |
| Glacier Deep Archive | Lowest-cost long-term archive | At least 3 AZs | Restore first; 180-day minimum |

Remember:

```text
Standard-IA and One Zone-IA: 30 days
Glacier Instant and Flexible Retrieval: 90 days
Glacier Deep Archive: 180 days
IA and Glacier Instant minimum billable object size: 128 KB
```

Do not select a class from storage price alone. Include retrieval frequency,
retrieval time, minimum billable duration, minimum object size, AZ resilience,
transition requests, and data-transfer requirements.

## Intelligent-Tiering

Intelligent-Tiering fits unknown or changing access patterns. Eligible objects
move automatically between access tiers based on observed access.

```text
Frequent Access
      |
      | 30 days without access
      v
Infrequent Access
      |
      | 90 days without access
      v
Archive Instant Access
```

Archive Access and Deep Archive Access are optional asynchronous tiers. Objects
in those tiers must be restored before use. Objects smaller than 128 KB remain
in Frequent Access and are not monitored or auto-tiered.

## Versioning and Delete Markers

- Uploading the same key again creates a new version.
- A normal delete in a versioned bucket creates a delete marker.
- The older data versions remain stored and billable.
- Removing the delete marker makes the previous current version visible again.
- Permanently deleting a specific version is normally irreversible.
- Suspending versioning does not delete existing versions.

Versioning improves recovery, but lifecycle rules should control noncurrent
versions and expired delete markers.

## Lifecycle Management

Lifecycle rules can:

- transition current and noncurrent objects;
- expire current objects;
- permanently remove noncurrent versions;
- remove eligible expired delete markers; and
- abort incomplete multipart uploads.

Lifecycle processing is asynchronous. Validate the rule configuration rather
than expecting an immediate transition. In a versioned bucket, current-version
expiration generally creates a delete marker; noncurrent data needs its own
retention action.

## Access-Control Layers

Use defense in depth:

1. Keep Object Ownership set to **Bucket owner enforced**.
2. Keep ACLs disabled.
3. Keep all four account- and bucket-level Block Public Access controls on.
4. Use identity policies and bucket policies for intended access.
5. Remember that an explicit deny overrides an allow.
6. Use IAM Access Analyzer for S3 to identify unintended external access.

| IAM policy | Bucket policy |
|---|---|
| Identity-based | Resource-based |
| Attached to a user or role | Attached to a bucket |
| Describes what the identity can do | Describes who can access the resource |

A normal private object URL should return `AccessDenied` anonymously.

## SSE-S3 and SSE-KMS

| SSE-S3 | SSE-KMS |
|---|---|
| S3 manages the encryption keys | AWS KMS manages the key |
| Simple default encryption | Separate key policy, permissions, and audit events |
| No KMS key selection | AWS managed or customer managed KMS key |
| No KMS request charge | KMS request charges can apply |

For SSE-KMS:

- the KMS key and S3 bucket must be in the same Region;
- upload typically requires `kms:GenerateDataKey`;
- download requires `kms:Decrypt`;
- S3 permission alone is not sufficient when KMS permission is missing; and
- an S3 Bucket Key can reduce direct KMS request traffic and cost.

An S3 Bucket Key is not a customer managed KMS key. It is an S3 mechanism that
reduces how often S3 must call KMS for supported workloads.

## Presigned URLs

A presigned URL grants temporary permission for one signed operation against a
specific bucket and object key.

- It does not make the bucket public.
- It cannot exceed the signing principal's permissions.
- Anyone holding an active URL can use it.
- The signer needs applicable KMS permission for an SSE-KMS object.
- Use a short expiry and never publish the full URL.

## Object Lock

Object Lock protects individual object versions using write-once-read-many
controls. Versioning is required.

| Protection | Behavior |
|---|---|
| Legal Hold | On/off protection without a fixed expiry |
| Governance mode | Authorized principals can bypass retention |
| Compliance mode | No principal, including root, can bypass before expiry |

Use Legal Hold for the Day 11 core lab. The optional Day 12 Compliance make-up
uses a separate bucket, a short approved retention, and documented pending
cleanup because Compliance retention cannot be bypassed.

## Manual Copy vs Replication

| Manual copy | S3 Replication |
|---|---|
| Started by a person or application | Automatically processes eligible versions |
| Copies selected objects | Uses rules and an IAM role |
| Destination object is independent | Ongoing asynchronous protection or distribution |
| Day 11 topic | Day 12 topic |

Copying can change destination-controlled settings such as encryption, storage
class, and metadata. It does not establish continuous replication.

## Exam Cues

- Frequent access -> S3 Standard
- Unknown access -> Intelligent-Tiering
- Infrequent multi-AZ -> Standard-IA
- Recreatable infrequent single-AZ -> One Zone-IA
- Instant archive -> Glacier Instant Retrieval
- Minutes-to-hours archive -> Glacier Flexible Retrieval
- Lowest-cost long-term archive -> Glacier Deep Archive
- Recover a normal delete -> versioning and delete-marker removal
- Prevent deletion for an unknown duration -> Legal Hold
- Temporary private-object sharing -> presigned URL
- More KMS control and auditability -> SSE-KMS
- Reduce supported S3-to-KMS request traffic -> S3 Bucket Key

## Official References

- [Amazon S3 storage classes](https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html)
- [S3 Intelligent-Tiering](https://docs.aws.amazon.com/AmazonS3/latest/userguide/intelligent-tiering-overview.html)
- [Managing S3 Lifecycle](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html)
- [Enabling S3 Versioning](https://docs.aws.amazon.com/AmazonS3/latest/userguide/manage-versioning-examples.html)
- [S3 Block Public Access](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html)
- [Default bucket encryption](https://docs.aws.amazon.com/AmazonS3/latest/userguide/default-bucket-encryption.html)
- [Using SSE-KMS with S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingKMSEncryption.html)
- [S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html)
- [Presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/ShareObjectPreSignedURL.html)
