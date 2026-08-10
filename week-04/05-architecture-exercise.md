# Week 4 Architecture Exercise

Draw one diagram connecting the image and storage lifecycles.

## Required Components

- Region boundary labeled `ap-south-1`
- Availability Zone boundary for EC2 and EBS
- Builder, SSM role, security group, User Data, and IMDSv2
- Golden AMI v2 and test EC2 with no User Data
- Storage EC2, gp3 data volume, snapshot, and restored volume
- Sydney Region boundary and the cross-Region snapshot copy
- Regional EFS, its mount targets, NFS security group, and two EC2 clients
- A note that EBS volumes are AZ scoped while AMIs and snapshots are Regional

Use arrows labeled `bootstraps`, `creates image`, `launches from`, `attaches`,
`snapshots`, `copies to Region`, `restores`, and `mounts`.

## Decision Table

Complete the reason column:

| Requirement | Choice | Reason |
|---|---|---|
| Repeatable patched nginx baseline | Golden AMI | |
| Automated image pipeline | EC2 Image Builder | |
| Secure instance administration | Session Manager | |
| Token-based metadata | IMDSv2 required | |
| General application block storage | gp3 | |
| Critical provisioned IOPS | io2 Block Express | |
| Shared files for Linux instances across AZs | EFS | |
| Same-AZ cluster-aware shared block device | io2 Multi-Attach | |
| Temporary reproducible cache | Instance Store | |
| Tightly coupled HPC | Cluster placement | |
| Critical instance isolation | Spread placement | |
| Rack-aware Kafka | Partition placement | |

## Pricing Scenarios

Answer as `requirement -> option -> reason`:

1. A new API has unpredictable demand.
2. A checkpointed rendering fleet tolerates interruption.
3. A company has steady compute spend across services.
4. Licensed software requires physical-host visibility.
5. A stable fleet uses the same EC2 family in one Region.

## Architecture Explanation

Write 200-300 words explaining:

- Why the image is versioned and tested
- Why IMDSv2 and an instance role improve security
- Why the EBS volume must share the instance AZ
- Why snapshots are recovery points
- Why a cross-Region snapshot copy supports DR but is not a running recovery
  environment
- Why EFS uses mount targets and TCP `2049` from the EC2 security group
- What still requires Multi-AZ design in production
- Which resources can still cost money after an instance stops

Do not include account IDs, resource IDs, IPs, or private data.
