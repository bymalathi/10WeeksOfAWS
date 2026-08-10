# Week 4 Cleanup

Capture sanitized evidence first. Check `ap-south-1` and every other Region
used.

## Order

1. On both EFS clients, unmount `/efs` and remove its `/etc/fstab` entry if an
   instance will remain.
2. On the storage EC2, unmount `/restore` and `/data`.
3. Terminate:
   - `cloudadhar-ec2-ami-builder-01`
   - `cloudadhar-ec2-ami-test-v2-01`
   - `cloudadhar-ec2-storage-lab-01`
   - `cloudadhar-ec2-efs-client-02`
   - `cloudadhar-ec2-multiattach-02`, if created
   - `cloudadhar-ec2-instance-store-01`, if created
4. Detach from both instances and delete
   `cloudadhar-ebs-io2-multiattach-01`, if created.
5. Delete:
   - `cloudadhar-ebs-gp3-data-01`
   - `cloudadhar-ebs-gp3-restored-01`
   - Any orphaned Week 4 root or data volume
6. Disable Fast Snapshot Restore for every snapshot and AZ where it was enabled.
7. Deregister Golden AMI v1, if created, and v2.
8. Delete the AMIs' backing snapshots after deregistration.
9. Delete `cloudadhar-snap-gp3-data-01`.
10. Delete `cloudadhar-dlm-daily-ebs-snapshots`, if created.
11. Delete the three placement groups.
12. Delete `cloudadhar-efs-shared-01` after confirming its training data is no
    longer required. EFS deletion permanently deletes its files.
13. After EFS mount targets are removed, delete `cloudadhar-sg-efs-nfs`.
14. Delete `cloudadhar-sg-nginx-public` and
    `cloudadhar-sg-storage-lab` after their dependencies are gone.
15. Delete the SSM role only if it was created exclusively for this lab.

## Sydney Region

Switch to `ap-southeast-2` and delete:

1. `cloudadhar-snap-dr-sydney-01`
2. Any EBS volume or EC2 recovery instance created from the copied snapshot
3. Any lab-only KMS alias or key only when your instructor explicitly confirms
   that it is safe to schedule its deletion

## Final Check

- [ ] No Week 4 instance is running or stopped.
- [ ] No Week 4 EBS volume remains.
- [ ] No Week 4 AMI remains registered.
- [ ] No Week 4 snapshot remains.
- [ ] No DLM policy remains active.
- [ ] Fast Snapshot Restore is not enabled.
- [ ] No Week 4 EFS filesystem or mount target remains.
- [ ] No io2 Multi-Attach volume remains.
- [ ] No Week 4 placement group remains.
- [ ] No unused security group, instance profile, or role remains.
- [ ] Mumbai, Sydney, and every other Region used were checked.

A stopped instance can still create costs through EBS, snapshots, AMIs, public
IPv4, and recurring lifecycle policies. Review billing later because usage data
can arrive after deletion.
