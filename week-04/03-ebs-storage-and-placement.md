# EBS, EFS, Instance Store, and Placement

Choose storage using IOPS, throughput, durability, persistence, access pattern,
failure scope, and cost.

## Storage Selection

| Requirement | Best fit | Important boundary |
|---|---|---|
| Boot disk or persistent block device for EC2 | EBS | Volume is scoped to one AZ |
| Shared files for multiple Linux instances | EFS | Uses NFS and VPC mount targets |
| Temporary host-local cache or scratch data | Instance Store | Data can be lost after stop/start or host failure |
| Shared block device for a cluster-aware application | io2 Multi-Attach | Same AZ; application coordinates writes |

EBS and EFS solve different problems. EBS presents a block device that the
operating system formats and mounts. EFS presents a managed network file system
that multiple Linux clients can mount concurrently.

## EBS Volume Types

| Type | Media | Best use |
|---|---|---|
| gp3 | SSD | General purpose, boot, applications |
| io2 Block Express | Provisioned IOPS SSD | Critical low-latency databases |
| st1 | Throughput HDD | Frequently accessed large sequential data |
| sc1 | Cold HDD | Infrequently accessed sequential data |

`st1` and `sc1` cannot be boot volumes. EBS volumes are Availability Zone
scoped and normally attach only to instances in the same AZ.

## Snapshots and Recovery

EBS snapshots are incremental point-in-time backups managed Regionally. They
can restore volumes into AZs in their Region and can be copied to another
Region.

- Quiesce applications when consistency matters.
- A snapshot cannot be mounted directly; create a volume from it.
- A cross-Region recovery copies the snapshot first, then creates a new volume
  and EC2 recovery environment in the destination Region.
- Restored volumes normally initialize blocks as they are read.
- Fast Snapshot Restore creates fully initialized volumes in selected AZs and
  adds cost.
- Data Lifecycle Manager automates tag-based snapshot and EBS-backed AMI
  creation and retention.
- Plan KMS permissions before copying or sharing encrypted snapshots.

## Encryption

EBS encryption protects data volumes, snapshots, restored volumes, and
cross-Region copies using AWS KMS.

- An encrypted volume creates encrypted snapshots.
- An encrypted snapshot creates encrypted volumes.
- An unencrypted snapshot can be copied while enabling encryption.
- An encrypted snapshot cannot be copied into an unencrypted snapshot.
- An existing unencrypted EBS volume cannot be encrypted in place. Create an
  encrypted snapshot copy and restore a new encrypted volume.

## Amazon EFS

Amazon EFS is managed NFS file storage for Linux workloads.

- Regional EFS stores data across multiple AZs; EFS One Zone stores data in one
  AZ at a lower price.
- Mount targets provide connectivity from VPC subnets.
- The mount-target security group should allow TCP `2049` only from the EC2
  client security group, never from `0.0.0.0/0`.
- Multiple EC2 instances can mount the same file system.
- Capacity grows and shrinks automatically.
- Encryption at rest uses KMS, and the EFS mount helper supports TLS in
  transit.
- EFS Access Points can provide application-specific entry paths and identities.

## Multi-Attach and Instance Store

Multi-Attach supports compatible `io1` or `io2` volumes attached to multiple
Nitro instances in one AZ. The application and filesystem must coordinate
concurrent writes. It is not cross-AZ shared storage.

Instance Store is host-attached ephemeral storage. Use it for cache, buffer,
scratch, and replicated or reproducible data. Do not keep the only copy of
important data there. Stop, hibernate, terminate, or host failure can remove
the data.

## Placement Groups

| Strategy | Priority | Typical workload |
|---|---|---|
| Cluster | Low latency and high throughput | HPC and tightly coupled nodes |
| Spread | Distinct underlying hardware | Small set of critical instances |
| Partition | Failure-domain separation | Kafka, Hadoop, Cassandra |

Placement groups do not replace Multi-AZ design, replication, backups, or Auto
Scaling.

## Exam Cues

- General boot/application volume -> gp3
- Critical sustained provisioned IOPS -> io2 Block Express
- Frequent large sequential data -> st1
- Cold sequential data -> sc1
- Temporary reproducible local data -> Instance Store
- Immediate restored-volume performance -> Fast Snapshot Restore
- Automated snapshot retention -> DLM
- Shared files across Linux instances or AZs -> EFS
- Shared same-AZ block device with coordinated writes -> io2 Multi-Attach
- Tightly coupled compute -> Cluster
- Individual hardware isolation -> Spread
- Rack-aware distributed system -> Partition

## Official References

- [EBS volume types](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-volume-types.html)
- [EBS snapshots](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-snapshots.html)
- [Copy an EBS snapshot](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-copy-snapshot.html)
- [EBS encryption](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-encryption.html)
- [Data Lifecycle Manager](https://docs.aws.amazon.com/ebs/latest/userguide/snapshot-lifecycle.html)
- [Multi-Attach](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-volumes-multi.html)
- [Fast Snapshot Restore](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-fast-snapshot-restore.html)
- [Amazon EFS](https://docs.aws.amazon.com/efs/latest/ug/whatisefs.html)
- [Mounting EFS file systems](https://docs.aws.amazon.com/efs/latest/ug/mounting-fs.html)
- [Instance Store](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/InstanceStorage.html)
- [Placement groups](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/placement-groups.html)
