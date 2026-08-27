# Week 4 - Day 8: EBS Persistence, EFS, and Storage Recovery

## Name
Malathi Shetty

## Tasks Completed
- [x] Watched/read the weekly content
- [x] Completed hands-on labs
- [x] Added screenshots and proof
- [x] Posted on LinkedIn
- [x] Cleaned up AWS resources

---

# Architecture

## Amazon EBS Persistence & Cross-Region Disaster Recovery

<img src="./diagram/Day8-EBS-Snapshot-Cross-Region-DR-Editable.gif" width="600">

### Architecture Overview

- An EC2 instance uses an Amazon EBS gp3 volume for persistent block storage.
- The EBS volume is attached to an EC2 instance in the same Availability Zone.
- Data written to the EBS volume remains available across instance reboot and stop/start operations.
- The EBS volume is expanded from 2 GiB to 4 GiB and the XFS filesystem is grown to use the additional capacity.
- An EBS snapshot provides a point-in-time recovery copy of the volume.
- The snapshot can be used to create another EBS volume for recovery.
- The snapshot is copied to the Sydney Region to provide a separate Regional recovery point.
- A new EBS volume can be created from the Sydney snapshot and attached to a recovery EC2 instance.
- EBS volumes are Availability Zone scoped, while EBS snapshots are Regional.

---

## Amazon EFS Shared Storage

<img src="./diagram/efs-shared-storage-architecture.gif" width="600">

### Architecture Overview

- Amazon EFS provides shared file storage for multiple EC2 clients.
- Two EC2 instances mount the same EFS file system.
- EFS mount targets provide network access to the file system from the Availability Zones.
- The EC2 clients communicate with EFS using NFS over TCP port 2049.
- The EFS security group allows NFS traffic from the EC2 client security group.
- Both clients can read and write files in the same shared EFS directory.
- The shared-file test was validated by creating files from both EFS clients and reading them from the shared filesystem.
- EFS provides Regional shared storage rather than a single-AZ block volume.

---

# Decision Table

| Requirement | Choice | Reason |
|---|---|---|
| Persistent block storage for EC2 | Amazon EBS gp3 | Provides durable SSD block storage suitable for general-purpose application workloads. |
| Secure data at rest | EBS Encryption | Protects EBS volumes and snapshots by encrypting stored data. |
| Automated backup scheduling | Amazon Data Lifecycle Manager (DLM) | Creates scheduled EBS snapshots according to lifecycle rules and resource tags. |
| Point-in-time recovery | EBS Snapshot | Provides a recovery point from which a new EBS volume can be created. |
| Cross-Region disaster recovery | Cross-Region Snapshot Copy | Maintains a snapshot copy in another AWS Region for Regional recovery scenarios. |
| Recovery storage | EBS Volume from Snapshot | Recreates the block volume from the required recovery snapshot. |
| Compute recovery | Recovery EC2 Instance | Provides compute capacity to use the restored EBS volume after a failure. |
| Shared storage across AZs | Amazon EFS | Allows multiple EC2 instances to access the same Regional filesystem. |
| EBS placement | Same Availability Zone | An EBS volume must be attached to an EC2 instance in the same AZ. |
| High-performance shared block storage | io2 Multi-Attach | Allows supported EC2 instances in the same AZ to attach to a single io2 volume. |
| Temporary local storage | Instance Store | Provides high-speed local storage for data that can be recreated after instance replacement. |
| Low-latency HPC workload | Cluster placement | Places instances close together to reduce network latency. |
| Hardware fault isolation | Spread placement | Separates instances across underlying hardware to reduce correlated failures. |
| Rack-aware distributed workload | Partition placement | Distributes instances across separate partitions to improve failure isolation. |

---

# Result

Successfully completed the Day 8 hands-on activities covering EBS persistence, filesystem management, volume resizing, snapshot recovery, cross-Region disaster recovery, Data Lifecycle Manager, Amazon EFS shared storage, Placement Groups, Fast Snapshot Restore, io2 Multi-Attach, and Instance Store.

The EFS validation also confirmed that two separate EC2 clients could mount the same EFS filesystem and exchange files successfully.

---

# Part 1: Amazon EBS Persistence

## Resources Used

- Storage EC2: `cloudadhar-ec2-storage-lab-01`
- Security Group: `cloudadhar-sg-storage-lab`
- Data Volume: `cloudadhar-ebs-gp3-data-01`

### Validation

The gp3 EBS volume was attached to the EC2 instance, formatted with XFS, mounted using its UUID, and tested for data persistence.

The volume was subsequently expanded from **2 GiB to 4 GiB**, followed by filesystem expansion.

### 1. EC2 and EBS Volume

<img src="./screenshots/1-Launch-an-instance-EC2-us-west.png" width="600">

---

### 2. EBS Volume Attached

<img src="./screenshots/5-Attach-volume-EC2.png" width="600">

---

### 3. Filesystem and Mount Validation

<img src="./screenshots/6-Systems-Manager-disk-filesystem-capacity-mountSuccess.png" width="600">

---

### 4. Test Data Written to EBS

<img src="./screenshots/7-test-data-on-EBS.png" width="600">

---

### 5. EBS Configuration

<img src="./screenshots/8-congifurations.png" width="600">

---

### 6. Reboot Persistence

<img src="./screenshots/9-sudo-reboot.png" width="600">

---

### 7. Data Available After Reboot

<img src="./screenshots/10-reboot-persistence.png" width="600">

---

### 8. Persistence After Stop/Start

<img src="./screenshots/11-connected-after-stop-start  .png" width="600">

---

### 9. EBS Resize: 2 GiB → 4 GiB

<img src="./screenshots/12-resize-EBS-2GiB-to-4 GiB.png" width="600">

---

# Part 2: EBS Snapshot and Recovery

## Resources Used

- Snapshot: `cloudadhar-snap-gp3-data-01`
- Restored Volume: `cloudadhar-ebs-gp3-restored-01`

### Validation

An EBS snapshot was created from the data volume and used to create a separate recovery volume. The recovered filesystem and stored data were then validated.

### 10. Snapshot Creation

<img src="./screenshots/13-Create-snapshot-EC2-us-west-2.png" width="600">

---

### 11. Snapshot Available

<img src="./screenshots/14-Snapshots-EC2-us-west-2.png" width="600">

---

### 12. Snapshot Completed

<img src="./screenshots/15-snapshot-created.png" width="600">

---

### 13. Create Recovery Volume from Snapshot

<img src="./screenshots/16-Create-volume-EC2.png" width="600">

---

### 14. Attach Restored Volume

<img src="./screenshots/17-2-Attach-restored-volume-2.png" width="600">

---

### 15. Mount Recovered Filesystem

<img src="./screenshots/18-mount-restored-filesystem.png" width="600">

---

### 16. Recovery Validation

<img src="./screenshots/21-recvery validation.png" width="600">

---

# Part 3: Cross-Region Disaster Recovery

## Resources Used

- Source snapshot: `cloudadhar-snap-gp3-data-01`
- Sydney DR snapshot: `cloudadhar-snap-dr-sydney-01`
- Sydney recovery volume: `cloudadhar-ebs-dr-sydney-01`

### Validation

The EBS snapshot was copied from the source Region to **ap-southeast-2 (Sydney)**. The copied snapshot was then used to create a new gp3 volume in Sydney.

### 17. Copy Snapshot to Sydney

<img src="./screenshots/19-Copy-snapshot-EC2.png" width="600">

---

### 18. Sydney Snapshot

<img src="./screenshots/20-Snapshots-EC2-ap-southeast-2.png" width="600">

---

### 19. Create Recovery Volume in Sydney

<img src="./screenshots/35-create-volume-from-snapshot.png" width="600">

---

### 20. Sydney Recovery Volume

<img src="./screenshots/36-Create-volume-EC2-ap-southeast-2.png" width="600">

---

### 21. Sydney DR Restore Validation

<img src="./screenshots/37-Volumes-EC2-ap-southeast-2-Sydney-DR-restore-successful.png" width="600">

---

# Part 4: Data Lifecycle Manager

## Resource Used

- DLM Policy: `cloudadhar-dlm-daily-ebs-snapshots`

### Validation

The Data Lifecycle Manager policy was configured to target EBS volumes using the tag:

```text
Backup = Daily
````

The policy was enabled with a daily schedule and one most-recent snapshot retained.

### 22. Data Lifecycle Manager

<img src="./screenshots/38-Lifecycle-Manager-EC2-us-west-2.png" width="600">

---

### 23. Create DLM Policy

<img src="./screenshots/39-Create-lifecycle-policy-EC2-us-west-2.png" width="600">

---

### 24. Configure Schedule

<img src="./screenshots/40-Configure-Schedule.png" width="600">

---

### 25. DLM Configuration

<img src="./screenshots/41-DLM-configuration.png" width="600">

---

### 26. DLM Policy Created

<img src="./screenshots/42-DLM created.png" width="600">

---

### 27. Backup Tag on Target Volume

<img src="./screenshots/43-original-EBS-has-the-Backup-tag.png" width="600">

---

# Part 5: Amazon EFS Shared Storage

## Resources Used

* EFS: `cloudadhar-efs-shared-01`
* EFS Security Group: `cloudadhar-sg-efs-nfs`
* EFS Client 1: `cloudadhar-ec2-efs-client-01`
* EFS Client 2: `cloudadhar-ec2-efs-client-02`

### Validation

The EFS utilities were installed on the EC2 clients and the same EFS filesystem was mounted on both instances.

Both clients successfully accessed the shared `/week4/` directory.

### 28. EFS File System

<img src="./screenshots/22-EFS-us-west-2.png" width="600">

---

### 29. EFS File System Created

<img src="./screenshots/23-Amazon-EFS-file-systems-list-created.png" width="600">

---

### 30. NFS Security Group

<img src="./screenshots/25-NFS-SecurityGroup-EC2-us-west-2.png" width="600">

---

### 31. EFS Network Configuration

<img src="./screenshots/26-Amazon-EFS-File-system-configuration-network.png" width="600">

---

### 32. EFS Security Configuration

<img src="./screenshots/27-Amazon-EFS-Amazon-EFS-security-manage.png" width="600">

---

### 33. Client 1 EFS Validation

<img src="./screenshots/28-EFS-Client-1-validation.png" width="600">

---

### 34. Client 1 Writes to Shared EFS

<img src="./screenshots/29-Client1-can-write-to-the-shared-EFS-filesystem.png" width="600">

---

### 35. Client 2 EC2 Instance

<img src="./screenshots/30-client-2-Launch-an-instance-EC2-us-west-2.png" width="600">

---

### 36. Both EC2 Instances Using the Same EFS

<img src="./screenshots/31-two-separate-EC2 instances-are-using-the-same-EFS-filesystem.png" width="600">

---

### 37. Client 2 Writes to EFS

<img src="./screenshots/32-Client-2-can-write-to-EFS.png" width="600">

---

### 38. Two-Way Shared Access

<img src="./screenshots/33-two-way-shared-access.png" width="600">

---

### 39. Persistent EFS Mount Validation

<img src="./screenshots/34-EFS-persistence-remount-validation.png" width="600">

---

# Part 6: Fast Snapshot Restore

## Resource Used

* EBS Snapshot: `cloudadhar-snap-gp3-data-01`

### Validation

Fast Snapshot Restore was enabled for the required Availability Zone, verified, and then disabled after the demonstration to avoid unnecessary charges.

---

# Part 7: io2 Multi-Attach

## Resources Used

* io2 Multi-Attach volume: `cloudadhar-ebs-io2-multiattach-01`
* EC2 Instance 1: `cloudadhar-ec2-multiattach-01`
* EC2 Instance 2: `cloudadhar-ec2-multiattach-02`

### Validation

The io2 Multi-Attach demonstration confirmed that supported EC2 instances in the same Availability Zone could detect the same shared EBS block device.

The demonstration resources were removed after validation.

---

# Part 8: Instance Store

## Resource Used

* EC2 Instance: `cloudadhar-ec2-instance-store-01`

### Validation

The Instance Store demonstration showed that local instance storage can provide fast temporary storage. Data remained available through a reboot but was not retained through an instance stop/start lifecycle.

The demonstration resources were cleaned up after validation.

---

# Where I Got Stuck

`No blocker`

---

# Cleanup

## Amazon EBS

* [x] Unmounted restored EBS volume
* [x] Deleted restored volume
* [x] Deleted source EBS volume
* [x] Deleted source snapshot
* [x] Deleted Sydney DR snapshot
* [x] Deleted DLM policy
* [x] Terminated storage EC2
* [x] Removed associated storage security group

## Amazon EFS

* [x] Unmounted EFS from Client 1
* [x] Unmounted EFS from Client 2
* [x] Deleted EFS file system
* [x] Removed EFS security group
* [x] Terminated EFS Client 1
* [x] Terminated EFS Client 2

## Optional Demonstrations

* [x] Disabled Fast Snapshot Restore
* [x] Deleted io2 Multi-Attach demonstration volume
* [x] Terminated Multi-Attach EC2 instances
* [x] Terminated Instance Store demonstration instance
* [x] Removed Placement Groups

---

# LinkedIn Post

[LinkedIn Link](PASTE_YOUR_LINK_HERE)

