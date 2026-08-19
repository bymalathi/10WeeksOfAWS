# Week 7 - Managed Databases and Caching

AWS Zero To Hero - CloudAdhar x TrainWithShubham<br>
Sessions: Aug 15-16, 2026<br>
Course sessions: Day 13-14<br>
Exam focus: SAA-C03 Domains 1-4<br>
Main pillars: Security, Reliability, Performance Efficiency, and Cost Optimization

Week 7 covers managed relational and NoSQL data services. Day 13 focuses on
Amazon RDS, Amazon Aurora, backup and recovery, read scaling, connection
management, and migration. Day 14 adds access-pattern-first DynamoDB design,
indexes, capacity, TTL, Streams, Global Tables, DAX, and ElastiCache decisions.

## Start Here

| Seq | Session | Focus | File |
|---:|---|---|---|
| 01 | Day 13 | RDS engines, deployment models, Aurora, recovery, and migration | [01-rds-aurora-and-migration.md](./01-rds-aurora-and-migration.md) |
| 02 | Day 13 | Build and validate a private RDS MySQL architecture | [02-rds-aurora-migration-lab.md](./02-rds-aurora-migration-lab.md) |
| 03 | Day 14 | DynamoDB keys, indexes, capacity, lifecycle, replication, and caching | [03-dynamodb-and-elasticache.md](./03-dynamodb-and-elasticache.md) |
| 04 | Day 14 | Build an orders table with GSI, LSI, TTL, Streams, Lambda, and a temporary UI | [04-dynamodb-elasticache-practical.md](./04-dynamodb-elasticache-practical.md) |
| 05 | Week 7 | Document the relational, NoSQL, and caching architecture | [05-architecture-exercise.md](./05-architecture-exercise.md) |
| 06 | End | Remove Day 13 and Day 14 resources safely | [06-cleanup.md](./06-cleanup.md) |
| 07 | End | Submit Week 7 evidence | [07-submission-format.md](./07-submission-format.md) |
| 08 | Daily | Share learning progress | [08-linkedin-post.md](./08-linkedin-post.md) |
| 09 | Review | Revise Week 7 decisions and practice questions | [09-quick-revision.md](./09-quick-revision.md) |

Day 14 downloads:

- [Student guide (PDF)](./AWS_Zero_To_Hero_Day14_DynamoDB_and_ElastiCache_Student_Guide.pdf)
- [Standalone Lambda UI helper](./day14.py)

## Day 13 Required Outcomes

- Select RDS MySQL, PostgreSQL, MariaDB, SQL Server, Oracle, Db2, or Aurora
  from compatibility, features, licensing, and workload requirements.
- Distinguish Single-AZ DB instance, Multi-AZ DB instance, Multi-AZ DB cluster,
  and asynchronous read replicas.
- Build a private encrypted RDS MySQL database accessible only from an EC2
  application Security Group.
- Keep master credentials in Secrets Manager and connect from EC2 using TLS
  certificate verification.
- Create synthetic InnoDB data and verify a non-empty TLS cipher.
- Compare automated backups, manual snapshots, and Point-in-Time Recovery.
- Explain that every snapshot or PITR restore creates a new database.
- Create and validate a same-Region read replica, replication health, read-only
  behavior, and possible lag.
- Create an Aurora MySQL Serverless v2 writer and reader in different AZs.
- Prove writer-endpoint writes, reader-endpoint reads, and a failed reader write.
- Perform a cross-AZ Aurora failover and validate the stable cluster endpoint.
- Create RDS Proxy read/write and read-only endpoints, confirm target health,
  and validate TLS routing through each.
- Explain RDS Proxy connection pooling without confusing it with query caching
  or read scaling.
- Select Aurora writer, reader, and instance endpoints correctly.
- Explain Aurora Serverless v2 ACUs and Global Database decisions.
- Select AWS DMS full load, CDC only, or full load plus CDC.
- Create a least-privilege logical `orders` table backup using an SSM Command
  document, Secrets Manager, an encrypted private S3 prefix, and a scheduled
  State Manager association.
- Restore a selected S3 table dump into an isolated temporary database,
  validate its rows, and prove that the active database remains unchanged.

## Day 13 Architecture

```text
Session Manager
      |
      v
cloudadhar-rds-client-day13
EC2 client SG
      |-- TCP 3306 + TLS --> private RDS MySQL writer
      |                       |-- backup, snapshot, and PITR
      |                       `-- asynchronous read replica
      |
      `-- TCP 3306 + TLS --> RDS Proxy SG
                              |-- read/write proxy endpoint
                              `-- read-only proxy endpoint
                                      |
                                      v
                           private Aurora Serverless v2 cluster
                           writer AZ <--> reader AZ
                           cluster endpoint survives failover

State Manager -> SSM Command document -> EC2 client
                                         |-- Secrets Manager backup credential
                                         `-- encrypted versioned S3 backup
```

The database Security Group accepts direct TCP `3306` from the EC2 client SG
for endpoint testing and from the Proxy SG for proxy traffic. The Proxy SG
accepts `3306` only from the EC2 client SG. Databases remain private. Multi-AZ,
Global Database and DMS deployment remain design exercises unless their
additional cost is explicitly approved.

## Day 14 Required Outcomes

- Convert access patterns into a composite DynamoDB primary key.
- Use `GetItem`, a base-table `Query`, `GSI1`, and `LSI1` for four distinct
  access paths without relying on a frequent Scan.
- Compare on-demand and provisioned capacity and explain RCU/WCU rounding.
- Configure TTL on numeric epoch seconds and explain asynchronous deletion.
- Enable `NEW_AND_OLD_IMAGES` Streams and process a change with Lambda.
- Demonstrate a status update from the temporary UI through DynamoDB, Streams,
  Lambda, and CloudWatch Logs.
- Explain when Global Tables, DAX, Valkey/Redis OSS, or Memcached is appropriate.
- Remove the public Function URL first and delete all lab-only resources.

## Minimum Submission for Day 13

- Private RDS security and networking configuration
- Encryption, automated backup, and managed-credential settings
- TLS connection proof and three synthetic rows
- InnoDB validation
- Manual snapshot in `Available` state
- Backup window, retention, and latest restorable time
- PITR marker timeline and completed restore proof
- Read replica endpoint, replicated row, read-only state, and failed write
- Aurora Serverless v2 writer/reader endpoint tests and failover proof
- RDS Proxy target health plus read/write and read-only endpoint tests
- Multi-AZ, Global Database, logical-backup, and DMS decision notes
- Successful SSM Run Command and scheduled State Manager execution
- Two encrypted timestamped table dumps with gzip integrity proof
- Isolated restore from S3 with restored-row and source-safety proof
- Architecture diagram, cleanup proof, and public learning post

## Minimum Submission for Day 14

- Composite table key, `GSI1`, and `LSI1` definitions
- Base-table Query, GSI lookup, LSI status query, and Query-versus-Scan note
- On-demand mode and optional provisioned-capacity comparison
- TTL configuration and asynchronous-expiry explanation
- Stream configuration, enabled Lambda trigger, and CloudWatch old/new image
- Temporary UI base Query, GSI lookup, LSI filter, and status update
- Global Tables, DAX, and ElastiCache decisions
- Cleanup proof and public learning post

## Cost and Safety

- Use synthetic data and an IAM training identity, never the root user.
- Keep databases private; never open a database port to `0.0.0.0/0` or `::/0`.
- Prefer Session Manager and avoid public SSH.
- Never place passwords, secret values, endpoints, account IDs, Security Group
  IDs, or connection strings in screenshots or repository files.
- Review the console estimate before creating RDS resources.
- Source DB, read replica, PITR restore, snapshots, retained automated backups,
  Secrets Manager, Proxy, Aurora, and DMS can all create charges.
- The logical-backup extension creates an additional secret, versioned S3
  objects, an SSM document, an association, and IAM permissions.
- The hands-on challenge provisions Aurora Serverless v2 and RDS Proxy; use the
  smallest approved settings and delete them the same day.
- Do not provision Multi-AZ, Aurora Global Database, or DMS unless their extra
  cost is separately approved.
- Do not create a Global Table replica, DAX cluster, or ElastiCache cache only
  for a screenshot. Delete a temporary public Function URL immediately after
  the demonstration.
- Delete the read replica before the source and deliberately decide whether a
  final snapshot is required.

<div align="center">

[Week 6](../week-06/) | [Home](../README.md)

</div>
