# Week 6 Architecture Exercise

Draw one Week 6 architecture connecting the private-report workflow, live
replication, transfer path, and storage-service decisions.

## Required Components

- AWS account and `ap-south-1` Region boundary
- Private source General Purpose bucket
- Source versioning, SSE-S3, storage classes, lifecycle rule, and BPA controls
- Private destination bucket with versioning, SSE-KMS, and S3 Bucket Key
- Customer managed KMS key `alias/cloudadhar-s3-day11`
- `CopyObject` path from source to destination
- Approved user using a short-lived presigned GET
- Anonymous user denied through a normal Object URL
- Separate versioned Object Lock bucket with Legal Hold
- Mumbai source bucket with `srr/` and `crr/` filters
- Mumbai SRR destination and Tokyo CRR destination
- S3 service role used by the replication rules
- Edge location and accelerated S3 endpoint
- Existing EFS filesystem with VPC mount targets and TCP `2049`
- FSx family decision box
- On-premises environment connected to a hybrid-service decision box

Use arrows labeled `uploads`, `CopyObject`, `replicates srr/`, `replicates
crr/`, `GenerateDataKey / Decrypt`, `presigned GET`, and `NFS 2049`. Use a red
denied path for anonymous access.

## Decision Table

Complete the reason column in your own words.

| Requirement | Choice | Reason |
|---|---|---|
| Frequently accessed data | S3 Standard | |
| Unknown access pattern | Intelligent-Tiering | |
| Infrequent multi-AZ data | Standard-IA | |
| Recreatable single-AZ data | One Zone-IA | |
| Lowest-cost long-term archive | Glacier Deep Archive | |
| Simple server-side encryption | SSE-S3 | |
| Separate key policy and audit events | SSE-KMS | |
| Temporary private download | Presigned GET URL | |
| Recover normal deletion | Versioning and delete-marker removal | |
| Prevent deletion without a fixed expiry | Legal Hold | |
| Automated transition and expiration | Lifecycle rule | |
| Selected one-time object transfer | Manual copy | |
| Automatic Mumbai copy of new versions | SRR | |
| Automatic Tokyo copy of new versions | CRR | |
| Existing eligible objects | S3 Batch Replication | |
| Long-distance upload through edge network | Transfer Acceleration | |
| Shared Linux NFS | EFS | |
| Windows SMB integration | FSx for Windows File Server | |
| HPC parallel filesystem | FSx for Lustre | |
| Automated online migration | DataSync | |
| Offline migration or edge compute | Snow Family | |
| Cached on-premises NFS/SMB view of S3 | S3 File Gateway | |

## Failure and Recovery Review

Explain the expected result when:

1. An anonymous user opens the normal private Object URL.
2. A learner tries to save a public-read policy while BPA is on.
3. The role has `s3:GetObject` but lacks `kms:Decrypt`.
4. The current object is deleted in the versioned source bucket.
5. A protected object version is permanently deleted while Legal Hold is on.
6. The destination object is deleted after a successful manual copy.
7. A lifecycle transition has been configured but its minimum object age has
   not passed.
8. An object existed under `srr/` before the SRR rule was created.
9. A new version matches `crr/`, but the replication service role cannot write
   to the Tokyo destination.
10. An object uses the unmatched `other/` prefix.

## Architecture Explanation

Write 250-400 words covering:

- data classification and access requirements;
- why buckets remain private and ACLs stay disabled;
- source and destination encryption choices;
- how versioning, lifecycle, and Object Lock solve different problems;
- why a presigned URL is temporary authorization, not public access;
- why manual copy does not provide continuous replication;
- why SRR, CRR, and Batch Replication solve different copy requirements;
- where Transfer Acceleration helps and what it costs;
- how EFS, FSx, and hybrid services are selected from protocol and movement
  requirements;
- failure and recovery behavior; and
- storage, request, retrieval, KMS, version, and cleanup costs.

Do not include bucket names with personal data, account IDs, ARNs, object URLs,
or presigned URLs.
