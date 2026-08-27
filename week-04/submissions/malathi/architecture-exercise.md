# Week 4 Architecture Exercise

## 1. Combined Day 7 + Day 8 Architecture

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│                                      AWS CLOUD                                                │
│                                                                                              │
│  ┌────────────────────────────── REGION: ap-south-1 ──────────────────────────────────────┐  │
│  │                                                                                       │  │
│  │  ┌──────────────────────────────────── VPC ─────────────────────────────────────────┐ │  │
│  │  │                                                                                 │ │  │
│  │  │  ┌──────────────────────── AVAILABILITY ZONE ────────────────────────────────┐ │ │  │
│  │  │  │                                                                          │ │ │  │
│  │  │  │                     DAY 7 — IMAGE LIFECYCLE                              │ │ │  │
│  │  │  │                                                                          │ │ │  │
│  │  │  │  ┌──────────────────────────────┐                                        │ │ │  │
│  │  │  │  │ Builder EC2                  │                                        │ │ │  │
│  │  │  │  │                              │                                        │ │ │  │
│  │  │  │  │ User Data                    │                                        │ │ │  │
│  │  │  │  │ SSM IAM Role                 │                                        │ │ │  │
│  │  │  │  │ Security Group               │                                        │ │ │  │
│  │  │  │  │ IMDSv2 Required              │                                        │ │ │  │
│  │  │  │  └──────────────┬───────────────┘                                        │ │ │  │
│  │  │  │                 │                                                       │ │ │  │
│  │  │  │                 │ bootstraps                                            │ │ │  │
│  │  │  │                 ▼                                                       │ │ │  │
│  │  │  │        ┌─────────────────────┐                                          │ │ │  │
│  │  │  │        │ Patched Golden AMI  │                                          │ │ │  │
│  │  │  │        │        v2           │                                          │ │ │  │
│  │  │  │        │     nginx + patch   │                                          │ │ │  │
│  │  │  │        └──────────┬──────────┘                                          │ │ │  │
│  │  │  │                   │                                                     │ │ │  │
│  │  │  │                   │ launches from                                       │ │ │  │
│  │  │  │                   ▼                                                     │ │ │  │
│  │  │  │        ┌─────────────────────────┐                                      │ │ │  │
│  │  │  │        │ Test EC2                │                                      │ │ │  │
│  │  │  │        │                         │                                      │ │ │  │
│  │  │  │        │ Golden AMI v2           │                                      │ │ │  │
│  │  │  │        │ No User Data            │                                      │ │ │  │
│  │  │  │        │ IMDSv2 Required         │                                      │ │ │  │
│  │  │  │        │ nginx validated         │                                      │ │ │  │
│  │  │  │        └─────────────────────────┘                                      │ │ │  │
│  │  │  │                                                                          │ │ │  │
│  │  │  └──────────────────────────────────────────────────────────────────────────┘ │ │  │
│  │  │                                                                                 │ │  │
│  │  │  ┌──────────────────────── AVAILABILITY ZONE ────────────────────────────────┐ │ │  │
│  │  │  │                                                                          │ │ │  │
│  │  │  │                     DAY 8 — EBS LIFECYCLE                                │ │ │  │
│  │  │  │                                                                          │ │ │  │
│  │  │  │       ┌──────────────────────┐                                           │ │ │  │
│  │  │  │       │ Storage EC2          │                                           │ │ │  │
│  │  │  │       └──────────┬───────────┘                                           │ │ │  │
│  │  │  │                  │                                                       │ │ │  │
│  │  │  │                  │ attaches                                              │ │ │  │
│  │  │  │                  ▼                                                       │ │ │  │
│  │  │  │       ┌──────────────────────┐                                           │ │ │  │
│  │  │  │       │ EBS gp3 Data Volume  │                                           │ │ │  │
│  │  │  │       └──────────┬───────────┘                                           │ │ │  │
│  │  │  │                  │                                                       │ │ │  │
│  │  │  │                  │ snapshots                                             │ │ │  │
│  │  │  │                  ▼                                                       │ │ │  │
│  │  │  │       ┌──────────────────────┐                                           │ │ │  │
│  │  │  │       │ EBS Snapshot         │                                           │ │ │  │
│  │  │  │       └──────────┬───────────┘                                           │ │ │  │
│  │  │  │                  │                                                       │ │ │  │
│  │  │  │                  │ restores                                              │ │ │  │
│  │  │  │                  ▼                                                       │ │ │  │
│  │  │  │       ┌──────────────────────┐                                           │ │ │  │
│  │  │  │       │ Restored EBS Volume  │                                           │ │ │  │
│  │  │  │       └──────────────────────┘                                           │ │ │  │
│  │  │  │                                                                          │ │ │  │
│  │  │  └──────────────────────────────────────────────────────────────────────────┘ │ │  │
│  │  │                                                                                 │ │  │
│  │  │  EBS volumes are AZ-scoped. AMIs and EBS snapshots are Regional.              │ │  │
│  │  │                                                                                 │ │  │
│  │  └─────────────────────────────────────────────────────────────────────────────────┘ │  │
│  │                                                                                       │  │
│  │                                                                                       │  │
│  │                     DAY 8 — EFS SHARED STORAGE                                      │  │
│  │                                                                                       │  │
│  │                 ┌──────────────────────────────────┐                                │  │
│  │                 │ Regional EFS File System          │                                │  │
│  │                 └───────────────┬──────────────────┘                                │  │
│  │                                 │                                                   │  │
│  │                    ┌────────────┴────────────┐                                      │  │
│  │                    │                         │                                      │  │
│  │                    ▼                         ▼                                      │  │
│  │          ┌──────────────────┐       ┌──────────────────┐                            │  │
│  │          │ EFS Mount Target │       │ EFS Mount Target │                            │  │
│  │          │                  │       │                  │                            │  │
│  │          │ NFS TCP 2049     │       │ NFS TCP 2049     │                            │  │
│  │          └────────┬─────────┘       └─────────┬────────┘                            │  │
│  │                   │                           │                                     │  │
│  │                   │ mounts                    │ mounts                              │  │
│  │                   ▼                           ▼                                     │  │
│  │          ┌──────────────────┐       ┌──────────────────┐                            │  │
│  │          │ EC2 Client 1     │       │ EC2 Client 2     │                            │  │
│  │          │                  │       │                  │                            │  │
│  │          │ NFS Security     │       │ NFS Security     │                            │  │
│  │          │ Group            │       │ Group            │                            │  │
│  │          └──────────────────┘       └──────────────────┘                            │  │
│  │                                                                                       │  │
│  └───────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                              │
│                                                                                              │
│  ┌──────────────────────────── REGION: ap-southeast-2 ─────────────────────────────────┐  │
│  │                                  SYDNEY DR                                           │  │
│  │                                                                                     │  │
│  │             EBS Snapshot                                                            │  │
│  │                  │                                                                  │  │
│  │                  │ copies to Region                                                 │  │
│  │                  ▼                                                                  │  │
│  │       ┌──────────────────────────────┐                                              │  │
│  │       │ Cross-Region Snapshot Copy   │                                              │  │
│  │       │                              │                                              │  │
│  │       │ DR recovery point            │                                              │  │
│  │       └──────────────────────────────┘                                              │  │
│  │                                                                                     │  │
│  │       Snapshot copy supports DR but is not a running recovery environment.          │  │
│  │                                                                                     │  │
│  └─────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ IMPORTANT SCOPE NOTES                                                                 │  │
│  │                                                                                       │  │
│  │ EBS Volume    → Availability Zone scoped                                             │  │
│  │ EBS Snapshot  → Regional                                                             │  │
│  │ AMI           → Regional                                                             │  │
│  │ EFS           → Regional                                                             │  │
│  └──────────────────────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
````

## 2. Decision Table

| Requirement                                 | Choice              | Reason                                                                                                                     |
| ------------------------------------------- | ------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Repeatable patched nginx baseline           | Golden AMI          | Provides a reusable and versioned server image with the required OS, nginx configuration, and patches already installed.   |
| Automated image pipeline                    | EC2 Image Builder   | Automates image creation, testing, patching, and distribution of standardized AMIs.                                        |
| Secure instance administration              | Session Manager     | Provides secure instance access without requiring inbound SSH or managing SSH keys.                                        |
| Token-based metadata                        | IMDSv2 required     | Requires session-based tokens for metadata access and provides stronger protection against unauthorized metadata requests. |
| General application block storage           | gp3                 | Provides cost-effective general-purpose SSD block storage with configurable IOPS and throughput.                           |
| Critical provisioned IOPS                   | io2 Block Express   | Provides high and consistent IOPS with high durability for demanding and critical workloads.                               |
| Shared files for Linux instances across AZs | EFS                 | Provides Regional shared file storage that can be mounted by multiple Linux EC2 instances across Availability Zones.       |
| Same-AZ cluster-aware shared block device   | io2 Multi-Attach    | Allows supported EC2 instances in the same Availability Zone to attach to a shared EBS volume.                             |
| Temporary reproducible cache                | Instance Store      | Provides fast local storage for temporary data that can be recreated when the instance is replaced.                        |
| Tightly coupled HPC                         | Cluster placement   | Places instances physically close together to provide low network latency and high network throughput.                     |
| Critical instance isolation                 | Spread placement    | Separates instances across underlying hardware to reduce the impact of hardware failures.                                  |
| Rack-aware Kafka                            | Partition placement | Distributes instances across separate hardware partitions to improve fault isolation for distributed workloads.            |

## 3. Pricing Scenarios

1. **A new API has unpredictable demand → On-Demand Instances →** Provides flexible capacity without requiring a long-term commitment.

2. **A checkpointed rendering fleet tolerates interruption → Spot Instances →** Provides significant cost savings for workloads that can tolerate interruptions and resume from checkpoints.

3. **A company has steady compute spend across services → Compute Savings Plans →** Provides discounted compute pricing for consistent usage while offering flexibility across supported AWS compute services.

4. **Licensed software requires physical-host visibility → Dedicated Hosts →** Provides a dedicated physical server with visibility into the underlying host for licensing and compliance requirements.

5. **A stable fleet uses the same EC2 family in one Region → EC2 Instance Savings Plans →** Provides discounted pricing for predictable EC2 usage while committing to a specific EC2 instance family in a Region.

## 4. Architecture Explanation

The Golden AMI is versioned and tested so that a known-good nginx configuration can be reused consistently. Versioning makes it possible to identify which image contains a particular patch or configuration and provides a reliable baseline for launching new instances. Testing the image before use helps confirm that nginx and the required configuration work correctly.

IMDSv2 improves security by requiring a session token when accessing instance metadata. The IAM instance role allows the EC2 instance to obtain temporary AWS credentials without storing long-term access keys on the server. Session Manager provides secure administration without requiring inbound SSH access.

An EBS volume is Availability Zone scoped, so the EC2 instance and its EBS volume must be in the same Availability Zone for attachment. EBS snapshots provide recovery points that can be used to create new volumes. A snapshot copied to the Sydney Region provides an additional disaster-recovery copy if the primary Region becomes unavailable. However, the copied snapshot is not a running recovery environment; compute and other infrastructure would still need to be provisioned.

EFS is Regional shared file storage. Mount targets provide network access to the file system from the Availability Zones where clients operate. EC2 clients use NFS over TCP port 2049, controlled by the EFS security group.

In production, applications should use Multi-AZ architecture so that an Availability Zone failure does not cause a complete service outage. Stopping an EC2 instance does not stop all charges. Attached EBS volumes, EBS snapshots, EFS storage, and other persistent resources can continue to incur charges.

