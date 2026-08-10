# S3 Replication, Transfer, and Hybrid Storage

Day 12 extends the private S3 foundation with live replication, transfer
optimization, file-storage selection, and hybrid migration decisions.

## Same-Region and Cross-Region Replication

| Feature | SRR | CRR |
|---|---|---|
| Destination | Same AWS Region | Different AWS Region |
| Common use | Log aggregation, compliance copies, separate ownership | Regional resilience, latency, regulatory copies |
| Versioning | Required on source and destination | Required on source and destination |
| Processing | Asynchronous | Asynchronous |
| Cost | Destination storage and requests | Storage, requests, and inter-Region transfer |

Replication rules can filter by prefix or tags. The Day 12 lab uses:

```text
srr/ -> Mumbai SRR destination
crr/ -> Tokyo CRR destination
other/ -> no matching rule
```

Live replication normally applies to eligible object versions created after
the rule becomes active. Use S3 Batch Replication for eligible existing or
previously failed objects.

## Replication States

| State | Meaning |
|---|---|
| `PENDING` | S3 accepted the eligible source version and replication is in progress |
| `COMPLETED` | Source version replicated successfully |
| `FAILED` | Replication failed; inspect permissions, destination, encryption, and rule eligibility |
| `REPLICA` | Object version is a destination replica |

Replication is asynchronous. A brief `PENDING` state is normal. An object that
does not match any enabled rule might not display replication status.

Objects marked `FAILED` are not automatically retried simply because a later
permission error was corrected. Upload a new version or use Batch Replication
when appropriate.

## Replication Controls

- The S3 service role must read eligible source versions and write to the
  destination.
- Source and destination versioning must remain enabled.
- Delete-marker replication is a separate decision.
- Replication Time Control and detailed replication metrics add cost and are
  not enabled in this lab.
- SSE-KMS replication needs explicit KMS permissions and key configuration;
  the cost-controlled lab uses SSE-S3.
- Deleting a replication rule does not delete replicas already created.
- Destination replicas are independent stored versions and incur storage cost.

## S3 Transfer Acceleration

Transfer Acceleration uses nearby AWS edge locations and the AWS global network
for suitable long-distance transfers. The client must use the accelerated
endpoint:

```text
<bucket-name>.s3-accelerate.amazonaws.com
```

Important constraints:

- Bucket names used with acceleration cannot contain periods.
- Normal Regional endpoints continue to work.
- Acceleration adds usage charges.
- A small same-Region upload does not prove a performance benefit.
- Compare transfer location, object size, network path, and cost before use.

## Multipart Upload and Cleanup

Multipart upload divides an object into parts that can be uploaded concurrently
and retried independently. The upload must eventually be completed or aborted.
Unfinished parts remain stored and can incur charges.

Use a lifecycle rule to abort incomplete multipart uploads after a defined
period. The Day 12 rule uses seven days and does not expire completed objects.

The included multipart text file is conceptual. A genuinely large object or
explicit CLI/SDK multipart operation is needed to prove multipart behavior.

## Amazon EFS Review

EFS is shared elastic NFS file storage for Linux workloads. Review:

- Regional versus One Zone storage;
- General Purpose versus Max I/O performance mode;
- Elastic, Provisioned, or Bursting throughput;
- VPC mount targets and their subnets;
- NFS TCP `2049` Security Group flow; and
- EFS Access Points for application-specific entry paths and POSIX identities.

```text
EC2 client SG -> outbound TCP 2049
EFS mount-target SG -> inbound TCP 2049 from EC2 client SG
```

Reuse the earlier EFS lab filesystem when it still exists. Do not create a
duplicate merely for this review.

## Amazon FSx Family

| Service | Workload signal |
|---|---|
| FSx for Windows File Server | Windows, SMB, Active Directory, and Microsoft integration |
| FSx for Lustre | HPC, machine learning, and parallel high-performance processing |
| FSx for NetApp ONTAP | Enterprise NAS and NetApp-compatible features |
| FSx for OpenZFS | Managed ZFS-based storage for Linux workloads |

The lab reviews the console choices but does not deploy an FSx filesystem.

## Hybrid and Transfer Decisions

| Requirement | Service |
|---|---|
| Present S3 objects through NFS or SMB with local cache | S3 File Gateway |
| Present cloud-backed block volumes through iSCSI | Volume Gateway |
| Replace physical backup tapes with virtual tapes | Tape Gateway |
| Automated online movement between supported storage systems | AWS DataSync |
| Offline migration or edge compute when network transfer is unsuitable | AWS Snow Family |
| Managed SFTP, FTPS, FTP, AS2, or browser-based transfer into S3/EFS | AWS Transfer Family |

These services solve different access and movement problems. Do not choose
Snow solely because the data is large; first evaluate available bandwidth,
deadline, online/offline constraints, and operational requirements.

## Native S3 Website vs Production HTTPS

A native S3 website endpoint supports static HTML over HTTP and requires public
read access to the website objects. Use only a dedicated disposable website
bucket in an isolated sandbox.

For production HTTPS:

- keep S3 private;
- use the regular S3 origin behind CloudFront;
- use Origin Access Control;
- redirect viewers to HTTPS; and
- add Route 53, ACM, and WAF when required.

Never mix private reports, replication data, or locked records into the public
website bucket.

## Object Lock Compliance Reminder

Object Lock Compliance mode prevents deletion of a protected object version
until its retain-until time, including by the root user. A normal delete can
still create a delete marker above the protected version. To prove protection,
attempt permanent deletion of the exact retained data version.

Compliance retention cannot be shortened or bypassed. Record pending cleanup
and return after the retention period expires.

## Exam Cues

- Same-Region automated copies -> SRR
- Regional copy and resilience -> CRR
- Pre-existing eligible objects -> S3 Batch Replication
- Long-distance S3 transfer through edge locations -> Transfer Acceleration
- Incomplete multipart cost control -> lifecycle abort action
- Shared Linux NFS -> EFS
- Windows SMB and Microsoft integration -> FSx for Windows File Server
- HPC parallel filesystem -> FSx for Lustre
- Online automated data movement -> DataSync
- Offline migration or edge processing -> Snow Family
- Managed SFTP into S3 or EFS -> Transfer Family
- Cached NFS/SMB view of S3 on premises -> S3 File Gateway

## Official References

- [S3 Replication](https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication.html)
- [Replication requirements](https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication-requirements.html)
- [Replication status](https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication-status.html)
- [S3 Batch Replication](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-batch-replication-existing-config.html)
- [S3 Transfer Acceleration](https://docs.aws.amazon.com/AmazonS3/latest/userguide/transfer-acceleration.html)
- [Multipart upload](https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html)
- [EFS performance](https://docs.aws.amazon.com/efs/latest/ug/performance.html)
- [Amazon FSx](https://docs.aws.amazon.com/fsx/latest/WindowsGuide/what-is.html)
- [AWS Storage Gateway](https://docs.aws.amazon.com/storagegateway/latest/userguide/WhatIsStorageGateway.html)
- [AWS DataSync](https://docs.aws.amazon.com/datasync/latest/userguide/what-is-datasync.html)
- [AWS Snow Family](https://docs.aws.amazon.com/snowball/latest/developer-guide/whatisedge.html)
- [AWS Transfer Family](https://docs.aws.amazon.com/transfer/latest/userguide/what-is-aws-transfer-family.html)
