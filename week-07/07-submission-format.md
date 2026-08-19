# Week 7 Submission Format

Document Day 13 and Day 14 in the same Week 7 submission.

```text
week-07/submissions/<github-username>/
├── README.md
├── architecture.png
└── evidence/
    ├── day13-rds-aurora/
    ├── day14-database-caching/
    └── cleanup/
```

## README Template

```markdown
# Week 7 - Managed Databases and Caching

## Learner
- Name:
- GitHub:
- LinkedIn:
- Region:

## Day 13
- Engine and compatibility decision:
- Source RDS deployment and security:
- TLS and synthetic-data result:
- Manual snapshot and automated backup result:
- PITR marker window and restore result:
- Read replica and read-only validation:
- Multi-AZ decision:
- Aurora Serverless v2 writer and reader validation:
- Aurora cross-AZ failover result:
- RDS Proxy target health and endpoint validation:
- Aurora Global Database decision:
- DMS migration-mode decision:
- SSM table-backup Run Command result:
- State Manager schedule and repeated backup result:
- Isolated S3 restore and row-validation result:
- Troubleshooting lesson:

## Day 14
- Access patterns and key design:
- Base-table Query result:
- GSI and LSI validation:
- On-demand versus provisioned decision:
- TTL configuration and expiry explanation:
- Stream and Lambda old/new image result:
- Temporary UI demonstration:
- Global Tables decision:
- DAX decision:
- Valkey/Redis OSS versus Memcached decision:
- Troubleshooting lesson:

## Architecture Decision
Write 250-400 words.

## Cleanup
- RDS source, replica, and restore:
- Snapshots and retained backups:
- Secrets Manager:
- EC2 and Security Groups:
- Aurora, Proxy, and DMS:
- SSM document, association, S3 backups, secret, and IAM roles:
- DynamoDB tables and indexes:
- Lambda functions, trigger, Function URL, and log groups:
- Global Tables, DAX, and ElastiCache:
- Regions checked:

## Reflection
1. Why is Multi-AZ different from a read replica?
2. Which recovery option best matches an accidental row deletion, and why?
3. When would you choose Aurora or DMS instead of basic RDS MySQL?
4. Why must a DynamoDB design begin with access patterns?
5. When should you choose a GSI, an LSI, DAX, or ElastiCache?
```

## Day 13 Evidence Checklist

- [ ] Source database private and encrypted
- [ ] DB SG allows TCP `3306` only from the EC2 client SG and Aurora Proxy SG
- [ ] Managed Secrets Manager credential without exposed value
- [ ] Successful TLS connection and non-empty cipher
- [ ] Three synthetic rows and InnoDB validation
- [ ] Manual snapshot `Available`
- [ ] Backup retention, window, automated snapshot, and latest restorable time
- [ ] PITR marker creation and deletion UTC timestamps
- [ ] PITR-restored database contains the marker while the source does not
- [ ] Read replica `Available` with a separate endpoint
- [ ] Replicated row, `read_only=1`, healthy replica status, and failed write
- [ ] Multi-AZ comparison
- [ ] Aurora Serverless v2 writer and reader in different AZs where possible
- [ ] Writer endpoint accepts writes and reader endpoint rejects a write
- [ ] Failover changes the writer backend while the cluster endpoint is stable
- [ ] RDS Proxy and both endpoint types `Available`
- [ ] Proxy target group reports healthy writer and reader targets
- [ ] Proxy read/write insert, read-only select, TLS, and failed read-only write
- [ ] RDS Proxy connection-pooling explanation
- [ ] Aurora Serverless v2 ACU and Global Database decisions
- [ ] DMS full load, CDC, and full load plus CDC comparison
- [ ] Private versioned encrypted S3 backup bucket
- [ ] Backup user has only the required table permission
- [ ] EC2 role policy is restricted to one secret and S3 prefix
- [ ] SSM Command document is schema `2.2` with validated parameters
- [ ] Successful Run Command and State Manager association executions
- [ ] Dedicated dispatch role trusts `ssm.amazonaws.com`
- [ ] Two timestamped encrypted `.sql.gz` objects with successful `gzip -t`
- [ ] Selected S3 dump restored only into `cloudadhardb_restore_test`
- [ ] Restored rows validated and active `cloudadhardb` left unchanged
- [ ] Temporary restore database and EC2 files removed
- [ ] Explanation that logical export does not replace snapshots or PITR
- [ ] Architecture diagram and decision table
- [ ] Cleanup confirmation and Day 13 LinkedIn link

## Day 14 Evidence Checklist

- [ ] Composite `PK` and `SK`, `GSI1`, and `LSI1` definitions
- [ ] Customer profile `GetItem`
- [ ] Customer orders returned newest first with a base-table Query
- [ ] Order lookup through `GSI1` without a customer ID
- [ ] Customer status query through `LSI1` with strong consistency
- [ ] Query-versus-Scan explanation
- [ ] Main table uses on-demand capacity
- [ ] Optional provisioned table shows RCU/WCU configuration, if created
- [ ] TTL is enabled on numeric `ExpiresAt`
- [ ] Stream uses `NEW_AND_OLD_IMAGES`
- [ ] Lambda event-source mapping is enabled and last processing result is OK
- [ ] CloudWatch `MODIFY` event shows the expected old and new status
- [ ] UI demonstrates base Query, GSI lookup, LSI filter, and status update
- [ ] Global Tables, DAX, and ElastiCache engine decisions
- [ ] Public Function URL, Lambdas, mappings, tables, roles, and optional cache
      resources are removed
- [ ] Day 14 LinkedIn link

Mask passwords, secret values and names, database endpoints, account IDs,
ARNs, Security Group IDs, IP addresses, private DNS, connection strings,
console URLs, Function URLs, and billing information.
