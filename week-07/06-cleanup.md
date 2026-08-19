# Week 7 Cleanup

Capture sanitized evidence first. Check RDS, EC2, Secrets Manager, IAM, DMS,
DynamoDB, Lambda, DAX, and ElastiCache in Mumbai before declaring cleanup
complete.

## Day 14 Immediate Cleanup

1. Delete the public Function URL from `cloudadhar-day14-ui` first.
2. Delete the DynamoDB trigger/event-source mapping from
   `cloudadhar-day14-stream-consumer`.
3. Delete `cloudadhar-day14-ui` and
   `cloudadhar-day14-stream-consumer`.
4. Delete `cloudadhar-orders-day14`.
5. Delete `cloudadhar-capacity-demo-day14` if it was created.
6. Delete any Global Table replica, DAX cluster, or ElastiCache cache created
   with explicit instructor approval.
7. Delete Day 14 log groups, alarms, VPC endpoints, Security Groups, subnet
   groups, and IAM roles only when they are lab-specific and no longer used.

The Function URL is the first Day 14 cleanup target because the lab configures
public invocation. The demo token is only an application guardrail; it does
not make the URL private.

## Day 13 Order

1. Delete the State Manager association
   `cloudadhar-rds-orders-backup-daily` so it cannot create new backups.
2. Delete the SSM document `CloudAdhar-RDS-MySQL-Table-Backup-To-S3` after
   evidence is captured.
3. Delete any DMS replication configuration, task, endpoint, replication
   instance, or serverless capacity created outside the core walkthrough.
4. Remove any optional Aurora Global Database secondary instance and cluster
   before removing the primary cluster.
5. Delete the separate read-only endpoint of
   `cloudadhar-aurora-proxy-day13`, if the console created one separately.
6. Delete `cloudadhar-aurora-proxy-day13` and wait until it disappears.
7. Delete `cloudadhar-aurora-serverless-day13-reader-1`.
8. Delete the writer and cluster `cloudadhar-aurora-serverless-day13` without
   a final snapshot because the lab contains only synthetic data.
9. Delete `cloudadhar-rds-day13-read-replica`.
10. Delete `cloudadhar-rds-day13-pitr`.
11. Delete `cloudadhar-rds-day13`.
   - Choose whether a final snapshot is required deliberately.
   - For the disposable lab, do not create one unless evidence or policy needs
     it.
   - Choose whether retained automated backups are needed.
12. Delete retained automated backups that are not required.
13. Delete `cloudadhar-rds-day13-snapshot` after evidence.
14. Open the versioned table-backup bucket, delete all current objects, object
    versions, and delete markers, then delete the bucket.
15. Schedule deletion of `cloudadhardb-backup-secret-day13` and the
    training-only RDS/Aurora secrets according to the approved recovery window.
16. Terminate `cloudadhar-rds-client-day13`.
17. Delete `cloudadhar-aurora-proxy-sg-day13` after Proxy dependencies vanish.
18. Delete `cloudadhar-rds-sg-day13` and
    `cloudadhar-ec2-rds-client-sg-day13` after dependencies disappear.
19. Delete `cloudadhar-ssm-association-dispatch-day13`, the proxy service role,
    and `cloudadhar-ec2-ssm-role-day13` only if they were created exclusively
    for this lab. Remove lab-only inline policies from any retained shared role.

Delete the read replica before the source. A snapshot or retained automated
backup can continue to cost money after every DB instance is gone.

## Preserve Shared Resources

Do not delete:

- shared VPCs, subnets, route tables, endpoints, NAT resources, or default
  Security Groups;
- shared IAM roles or KMS keys;
- databases, snapshots, secrets, or DMS resources from another lab; or
- logging and monitoring resources still required by another workload.

## Final Check

- [ ] No Day 13 source, replica, PITR database, or Aurora cluster remains.
- [ ] No unintended final snapshot or retained automated backup remains.
- [ ] No manual Day 13 snapshot remains.
- [ ] No RDS Proxy remains.
- [ ] No Aurora reader, proxy endpoint, or Global Database secondary remains.
- [ ] No DMS task, endpoint, or replication capacity remains.
- [ ] No Day 13 State Manager association or custom SSM document remains.
- [ ] No table-backup object version, delete marker, or bucket remains.
- [ ] No table-backup secret or lab-only IAM permission remains.
- [ ] Training-only Secrets Manager secret is scheduled according to policy.
- [ ] EC2 client is terminated.
- [ ] No orphaned Day 13 EBS volume, public IPv4, or Security Group remains.
- [ ] No lab-only IAM role or profile remains when safe to delete.
- [ ] No Day 14 Function URL or Lambda event-source mapping remains.
- [ ] No Day 14 Lambda function or lab-only log group remains.
- [ ] No Day 14 DynamoDB table or optional capacity table remains.
- [ ] No Day 14 Global Table replica, DAX cluster, or ElastiCache cache remains.
- [ ] No Day 14 lab-only IAM role, VPC endpoint, Security Group, or subnet group
      remains.
- [ ] RDS Events, CloudWatch, and Billing will be reviewed after usage arrives.

RDS instances, replicas, storage, I/O, snapshots, retained backups, Secrets
Manager, Proxy, DMS, EC2, EBS, public IPv4, DynamoDB, Lambda, CloudWatch Logs,
DAX, ElastiCache, Global Tables, and cross-Region transfer can generate charges.
