# Day 8 Lab - EBS Persistence, EFS, and Storage Recovery

This lab uses the AWS Management Console for every AWS resource operation.
Commands are used only inside the Linux instances to prepare and validate the
file systems. Complete the required EBS sequence before the optional
cost-generating demonstrations.

## Learner Sequence

Complete Parts 1-8, Part 12, Part 13, and the final validation checklist in
order. Parts 9-11 are optional, cost-controlled demonstrations. Do not skip a
validation step merely because a resource shows `Available` or `Completed` in
the console.

## Resources

| Resource | Exact name |
|---|---|
| Storage EC2 | `cloudadhar-ec2-storage-lab-01` |
| EC2 client security group | `cloudadhar-sg-storage-lab` |
| Data volume | `cloudadhar-ebs-gp3-data-01` |
| Snapshot | `cloudadhar-snap-gp3-data-01` |
| Restored volume | `cloudadhar-ebs-gp3-restored-01` |
| Sydney DR snapshot | `cloudadhar-snap-dr-sydney-01` |
| DLM policy | `cloudadhar-dlm-daily-ebs-snapshots` |
| EFS client 2 | `cloudadhar-ec2-efs-client-02` |
| EFS file system | `cloudadhar-efs-shared-01` |
| EFS security group | `cloudadhar-sg-efs-nfs` |
| Optional Multi-Attach EC2 | `cloudadhar-ec2-multiattach-02` |
| Optional Multi-Attach volume | `cloudadhar-ebs-io2-multiattach-01` |
| Optional Instance Store EC2 | `cloudadhar-ec2-instance-store-01` |
| Placement groups | `cloudadhar-pg-cluster-demo`, `cloudadhar-pg-spread-demo`, `cloudadhar-pg-partition-demo` |

Use `ap-south-1` (Mumbai) unless a step explicitly says to switch to
`ap-southeast-2` (Sydney).

Tag resources with `Project=AWS-Zero-To-Hero`, `Module=EC2-Storage`,
`Environment=Training`, `Owner=CloudAdhar`, `ManagedBy=Manual`,
`CleanupAfter=26-July-2026`, and `DataClassification=Training-Only`.
Add `Backup=Daily` to the original gp3 volume.

## Safety and Cost Warnings

- `mkfs` destroys the filesystem on the selected device. Run `lsblk -f`,
  identify the new empty 2 GiB disk, and confirm it is not the root disk.
- Never format a volume restored from a snapshot.
- Never mount a normal XFS or ext4 filesystem read/write from two instances.
- Do not allow SSH or NFS from `0.0.0.0/0`.
- Fast Snapshot Restore, io2, cross-Region snapshot copies, EFS, public IPv4
  addresses, EBS volumes, and snapshots can generate charges.
- Disable or delete optional resources immediately after validating them.

## Part 1 - Launch the Storage Instance

1. Open **EC2 -> Instances -> Launch instances**.
2. Configure:
   - Name: `cloudadhar-ec2-storage-lab-01`
   - AMI: Amazon Linux 2023, 64-bit x86
   - Instance type: `t3.micro`
   - VPC: your default or training VPC
   - Subnet: a subnet with the connectivity required by your chosen connection
     method
   - IAM instance profile: the class SSM role when using Session Manager
3. Create or select `cloudadhar-sg-storage-lab`.
   - Prefer Session Manager with no inbound rule.
   - If direct SSH is required, allow TCP `22` only from **My IP**.
4. Configure an encrypted 8 GiB gp3 root volume with **Delete on termination**
   enabled.
5. Under **Advanced details**, set:
   - Metadata accessible: Enabled
   - Metadata version: V2 only / Required
   - Metadata response hop limit: `1`
6. Launch the instance and wait for **Running** and both status checks.
7. Record the actual Availability Zone. The data volume must use this exact AZ.
8. Connect through Session Manager or EC2 Instance Connect and inspect:

```bash
hostname
lsblk
lsblk -f
df -hT
```

## Part 2 - Create, Attach, and Mount gp3

1. Open **EC2 -> Elastic Block Store -> Volumes -> Create volume**.
2. Configure:
   - Type: gp3
   - Size: 2 GiB
   - IOPS: 3,000
   - Throughput: 125 MiB/s
   - Availability Zone: the storage instance's actual AZ
   - Encryption: Enabled
   - KMS key: `aws/ebs` or the approved training key
   - Name: `cloudadhar-ebs-gp3-data-01`
   - Tag: `Backup=Daily`
3. Wait for **Available**.
4. Select the volume and choose **Actions -> Attach volume**.
5. Select `cloudadhar-ec2-storage-lab-01`, request `/dev/sdf`, and attach.
6. Wait for **In-use**, then identify the new device by its 2 GiB size:

```bash
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
lsblk -f
sudo file -s /dev/nvme1n1
```

The console name `/dev/sdf` commonly appears as `/dev/nvme1n1` on Nitro
instances. Use the actual empty device shown by your instance.

After confirming the correct device:

```bash
DATA_DEVICE=/dev/nvme1n1
sudo dnf install -y xfsprogs
sudo mkfs -t xfs "$DATA_DEVICE"
sudo mkdir -p /data
sudo mount "$DATA_DEVICE" /data
sudo chown ec2-user:ec2-user /data
lsblk -f
df -hT /data
```

Create the original Week 4 proof data:

```bash
echo "Week 4 EBS test - $(date -u +%FT%TZ)" \
  | sudo tee /data/week4-proof.txt
sudo mkdir -p /data/application
echo "Version 1" | sudo tee /data/application/version.txt
sudo sync
sudo cat /data/week4-proof.txt
sudo cat /data/application/version.txt
```

## Part 3 - Configure and Prove Persistent Mounting

1. Get the filesystem UUID and back up `/etc/fstab`:

```bash
sudo blkid "$DATA_DEVICE"
sudo cp /etc/fstab /etc/fstab.before-ebs
DATA_UUID=$(sudo blkid -s UUID -o value "$DATA_DEVICE")
echo "$DATA_UUID"
```

2. Add exactly one entry to `/etc/fstab`:

```text
UUID=<actual-filesystem-uuid> /data xfs defaults,nofail 0 2
```

3. Validate before restarting:

```bash
sudo grep -n "$DATA_UUID" /etc/fstab
sudo findmnt --verify --verbose
sudo umount /data
sudo mount -a
findmnt /data
df -hT /data
sudo cat /data/week4-proof.txt
```

Do not restart until `mount -a` succeeds. If validation fails, restore
`/etc/fstab.before-ebs`, mount the device manually, correct the entry, and
repeat the checks.

4. Run `sudo reboot`, reconnect, and prove `/data` and the file are present.
5. In the console, stop the instance, wait for **Stopped**, and start it.
6. Reconnect and repeat:

```bash
findmnt /data
sudo cat /data/week4-proof.txt
```

This proves that EBS data persists across reboot and stop/start.

## Part 4 - Resize EBS from 2 GiB to 4 GiB

1. Open **EC2 -> Volumes** and select
   `cloudadhar-ebs-gp3-data-01`.
2. Choose **Actions -> Modify volume**.
3. Change only the size from 2 GiB to 4 GiB. Keep gp3, 3,000 IOPS, and
   125 MiB/s throughput.
4. Confirm and wait for the modification to reach **Optimizing** or
   **Completed**.
5. On the instance, confirm that Linux sees the larger block device:

```bash
lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINTS
df -hT /data
```

Do not grow the filesystem until `lsblk` shows approximately 4 GiB.

6. Grow XFS and validate:

```bash
sudo xfs_growfs /data
df -hT /data
lsblk -f
```

The EBS block device and Linux filesystem are separate layers; both must show
the increased capacity. This lab formats the whole disk. A partitioned disk
would require the partition to be grown before the filesystem.

## Part 5 - Snapshot and Point-in-Time Restore

1. Run `sudo sync`. For production databases, use an application-aware
   quiesce or backup procedure.
2. Open **EC2 -> Volumes**, select the data volume, and choose
   **Actions -> Create snapshot**.
3. Set:
   - Name: `cloudadhar-snap-gp3-data-01`
   - Description: `CloudAdhar Week 4 EBS snapshot practical`
4. Wait under **EC2 -> Snapshots** until the status is **Completed**.
5. After snapshot creation, change the live source:

```bash
echo "Created after snapshot" > /data/after-snapshot.txt
echo "Version 2" | sudo tee /data/application/version.txt
sync
cat /data/after-snapshot.txt
cat /data/application/version.txt
```

6. Select the completed snapshot and choose
   **Actions -> Create volume from snapshot**.
7. Configure:
   - Type: gp3
   - Availability Zone: the storage instance's AZ
   - Encryption: Enabled
   - Name: `cloudadhar-ebs-gp3-restored-01`
8. Wait for **Available**, then attach the restored volume to the storage
   instance as `/dev/sdg`.
9. Identify the restored device with `lsblk -f`. Do not run `mkfs`.
10. Mount the cloned XFS filesystem with `nouuid` because the source and clone
    initially have the same filesystem UUID:

```bash
RESTORED_DEVICE=/dev/nvme2n1
sudo mkdir -p /restore
sudo mount -o nouuid "$RESTORED_DEVICE" /restore
ls -la /restore
sudo cat /restore/week4-proof.txt
sudo cat /restore/application/version.txt
test ! -f /restore/after-snapshot.txt \
  && echo "PASS: Post-snapshot file is not present in restored volume"
```

Expected: the restored volume contains `week4-proof.txt`,
`application/version.txt` contains `Version 1`, and `after-snapshot.txt` is
absent. This proves that the snapshot is a point-in-time backup rather than a
copy of the current live volume.

If the clone will be retained independently, unmount it and use
`xfs_admin -U generate <restored-device>` to create a new XFS UUID. Confirm the
device carefully and never change the original `/data` filesystem UUID.

## Part 6 - Cross-Region Snapshot Copy

1. In Mumbai, open **EC2 -> Snapshots**.
2. Select `cloudadhar-snap-gp3-data-01` and choose
   **Actions -> Copy snapshot**.
3. Configure:
   - Destination Region: Asia Pacific (Sydney), `ap-southeast-2`
   - Description: `CloudAdhar Week 4 cross-Region DR snapshot`
   - Encryption: Enabled
   - KMS key: an approved destination-Region key
4. Choose **Copy snapshot**.
5. Switch the console Region to **Asia Pacific (Sydney)**.
6. Open **EC2 -> Snapshots**, locate the copy, and name it
   `cloudadhar-snap-dr-sydney-01`.
7. Wait for **Completed** if class time permits.

The recovery flow is: copied snapshot -> new EBS volume in a Sydney AZ -> a
Sydney EC2 recovery instance -> mount the existing filesystem -> recover data.
An EBS volume cannot attach directly across Regions.

## Part 7 - Validate Encryption

For the required path, verify in the console that:

1. `cloudadhar-ebs-gp3-data-01` shows **Encrypted: Yes**.
2. Its Mumbai snapshot is encrypted.
3. The restored volume is encrypted.
4. The Sydney copied snapshot is encrypted with a key available in Sydney.

Remember:

- Encrypted volume -> encrypted snapshot -> encrypted restored volume.
- An unencrypted snapshot can be copied while enabling encryption.
- An encrypted snapshot cannot be converted to an unencrypted snapshot.
- An existing unencrypted volume cannot be encrypted in place.

Do not create an unencrypted training volume only to demonstrate conversion.

## Part 8 - Data Lifecycle Manager

1. Confirm that the source volume has `Backup=Daily`.
2. In Mumbai, open **EC2 -> Elastic Block Store -> Lifecycle Manager**.
3. Choose **Create lifecycle policy**.
4. Select **EBS snapshot policy** with **Volume** as the target resource type.
5. Set the target tag to `Backup=Daily`.
6. Configure:
   - Description: `Daily snapshots for CloudAdhar training EBS volumes`
   - IAM role: Default DLM role
   - Policy status: Enabled
   - Schedule name: `DailySnapshots`
   - Frequency: Every 24 hours
   - Starting time: an appropriate UTC time
   - Retention: Count based, retain 7
   - Copy tags from source: Enabled
7. Review that only the intended tagged volume is selected.
8. Either create `cloudadhar-dlm-daily-ebs-snapshots` and delete it during
   cleanup, or capture the final review screen and cancel.

DLM deletes only snapshots created and managed by that policy. It does not
delete the manual snapshot created earlier.

## Part 9 - Optional Fast Snapshot Restore

FSR adds cost. Use it only for a short demonstration.

1. Open **EC2 -> Snapshots** and select the completed Mumbai snapshot.
2. Choose **Actions -> Manage Fast Snapshot Restore**.
3. Enable it in the storage instance's AZ.
4. Explain that FSR is configured for one snapshot and AZ combination and that
   a copied snapshot does not inherit FSR.
5. Return to **Manage Fast Snapshot Restore**, disable it immediately, and
   verify that it is no longer enabled.

## Part 10 - Optional io2 Multi-Attach

This demonstration adds EC2 and io2 charges.

1. Launch `cloudadhar-ec2-multiattach-02` using a supported Nitro instance type
   in the same AZ as the storage instance.
2. Open **EC2 -> Volumes -> Create volume** and configure:
   - Name: `cloudadhar-ebs-io2-multiattach-01`
   - Type: io2
   - Size: 4 GiB
   - Provisioned IOPS: the lowest suitable value allowed by the console
   - AZ: the same AZ as both instances
   - Multi-Attach: Enabled
   - Encryption: Enabled
3. Attach the same volume to both EC2 instances.
4. Run `lsblk` on each instance and prove that both can see the block device.
5. Do not format or mount a normal XFS/ext4 filesystem read/write on both
   clients.
6. Explain that production use requires a cluster-aware application,
   clustered filesystem, coordinated writes, and I/O fencing.
7. Detach the volume from both instances, delete it, and terminate the second
   instance immediately.

## Part 11 - Optional Instance Store

This demonstration requires an instance type that explicitly includes local
NVMe Instance Store and may cost more than `t3.micro`.

1. In the EC2 launch wizard, select a supported instance type and verify its
   Instance Store capacity and price before launching
   `cloudadhar-ec2-instance-store-01`.
2. Connect and identify the non-root local NVMe device:

```bash
lsblk
sudo nvme list
```

3. After verifying the actual device, format and mount it:

```bash
INSTANCE_STORE_DEVICE=/dev/nvme1n1
sudo mkfs -t xfs "$INSTANCE_STORE_DEVICE"
sudo mkdir -p /instance-store
sudo mount "$INSTANCE_STORE_DEVICE" /instance-store
echo "Temporary Instance Store data" \
  | sudo tee /instance-store/temporary.txt
sudo cat /instance-store/temporary.txt
```

4. Reboot and observe that the data normally remains after remounting.
5. Stop and start the instance, then inspect the disks and explain that the
   previous Instance Store data is not guaranteed to remain.
6. Terminate the instance immediately.

## Part 12 - Placement Groups

Open **EC2 -> Network & Security -> Placement Groups** and create:

- `cloudadhar-pg-cluster-demo` - Cluster. One AZ, close placement, low latency,
  and high throughput for tightly coupled workloads.
- `cloudadhar-pg-spread-demo` - Spread at rack level. Distinct underlying
  hardware for a small number of critical instances.
- `cloudadhar-pg-partition-demo` - Partition with three partitions. Separate
  rack-level failure domains for Hadoop, Cassandra, Kafka, and similar systems.

Open the EC2 launch wizard and locate **Advanced details -> Placement group** to
show where an instance is assigned. Cancel the launch. Do not assume that
`t3.micro` is appropriate for a Cluster placement group; verify compatibility
and capacity for the intended production instance type.

## Part 13 - EFS Shared Storage on Two EC2 Instances

This demonstration proves sharing only when two different EC2 instances mount
the same EFS ID and read each other's files.

### Create the EFS security group

1. Open **VPC or EC2 -> Security Groups -> Create security group**.
2. Configure:
   - Name: `cloudadhar-sg-efs-nfs`
   - VPC: the same VPC as `cloudadhar-ec2-storage-lab-01`
   - Inbound type: NFS
   - Protocol and port: TCP `2049`
   - Source: security group `cloudadhar-sg-storage-lab`
3. Keep the default outbound rule. Never use `0.0.0.0/0` as the NFS source.

### Create EFS and its mount targets

1. Open **EFS -> File systems -> Create file system** and choose
   **Customize**.
2. Configure:
   - Name: `cloudadhar-efs-shared-01`
   - File-system type: Regional
   - Encryption at rest: Enabled
   - Performance mode: General Purpose
   - Throughput mode: Elastic
   - VPC: the EC2 instances' VPC
3. Keep or create a mount target in every AZ used by the two EC2 instances.
4. Select the appropriate subnet in each AZ and associate
   `cloudadhar-sg-efs-nfs` with every mount target.
5. Remove the default security group from the mount targets if it is not
   required.
6. Create the filesystem, wait for **Available**, and copy its actual
   `fs-...` ID. Allow a short time for DNS and mount-target propagation.

### Mount and write from EC2 client 1

On `cloudadhar-ec2-storage-lab-01`:

```bash
sudo dnf install -y amazon-efs-utils
sudo mkdir -p /efs
sudo mount -t efs -o tls fs-XXXXXXXX:/ /efs
hostname
findmnt /efs
df -hT /efs
echo "Shared file created from EC2 instance 1" \
  | sudo tee /efs/cloudadhar-efs-shared.txt
date | sudo tee -a /efs/cloudadhar-efs-shared.txt
sudo cat /efs/cloudadhar-efs-shared.txt
```

Replace `fs-XXXXXXXX` with the actual EFS ID. The EFS console's **Attach**
button also displays the account-specific mount command.

### Mount and validate from EC2 client 2

1. Launch or reuse a second Amazon Linux 2023 instance:
   - Name: `cloudadhar-ec2-efs-client-02`
   - VPC: the same VPC
   - Subnet: preferably in another AZ with an EFS mount target
   - Security group: `cloudadhar-sg-storage-lab`
2. Connect to client 2 and run:

```bash
sudo dnf install -y amazon-efs-utils
sudo mkdir -p /efs
sudo mount -t efs -o tls fs-XXXXXXXX:/ /efs
hostname
findmnt /efs
sudo cat /efs/cloudadhar-efs-shared.txt
echo "Shared file created from EC2 instance 2" \
  | sudo tee /efs/cloudadhar-efs-client-02.txt
```

3. Return to client 1 and read the file created by client 2:

```bash
hostname
sudo cat /efs/cloudadhar-efs-client-02.txt
```

Capture both hostnames. Reading the same file twice on one instance does not
prove shared access.

### Configure persistent EFS mounting

On each EC2 instance:

```bash
sudo cp /etc/fstab /etc/fstab.before-efs
```

Add one entry using the actual EFS ID:

```text
fs-XXXXXXXX:/ /efs efs _netdev,tls,nofail 0 0
```

Then validate:

```bash
sudo umount /efs
sudo mount -a
findmnt /efs
df -hT /efs
sudo cat /efs/cloudadhar-efs-shared.txt
```

`_netdev` tells Linux that the filesystem depends on network connectivity.

### Troubleshoot EFS

If mounting times out, verify:

- Both clients and EFS use the same VPC.
- A mount target exists in each required AZ.
- The mount-target security group allows TCP `2049` from the EC2 client
  security group.
- VPC DNS resolution and DNS hostnames are enabled.
- `amazon-efs-utils` is installed.
- The actual EFS ID is used.
- The filesystem is **Available** and DNS has had time to propagate.

## Validation and Evidence

- [ ] EC2 and the original EBS volume are in the same AZ.
- [ ] The correct empty NVMe device was identified before `mkfs`.
- [ ] XFS is mounted at `/data` using its UUID.
- [ ] Data survived reboot and stop/start.
- [ ] EBS and XFS grew from 2 GiB to 4 GiB.
- [ ] The completed snapshot restored `Version 1`.
- [ ] The restored volume does not contain the post-snapshot file.
- [ ] The encrypted snapshot was copied from Mumbai to Sydney.
- [ ] The source volume, snapshots, and restored volume show encryption.
- [ ] The DLM policy review targets only `Backup=Daily`.
- [ ] Optional FSR was disabled after demonstration.
- [ ] Optional Multi-Attach and Instance Store resources were removed.
- [ ] All three placement strategies were created and explained.
- [ ] EFS uses mount targets and an NFS security-group rule on TCP `2049`.
- [ ] Two different EC2 hostnames mounted the same EFS ID.
- [ ] Client 2 read client 1's file, and client 1 read client 2's file.
- [ ] Persistent EFS mounting passed `mount -a` on both clients.

Proceed to [06-cleanup.md](./06-cleanup.md) after capturing sanitized evidence.
