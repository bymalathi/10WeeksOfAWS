# Amazon RDS, Aurora, Recovery, and Migration

Amazon RDS manages much of the relational database infrastructure, including
host provisioning, patching workflows, backups, monitoring integrations, and
replacement of failed infrastructure. You still own schemas, users,
permissions, queries, application behavior, recovery decisions, security, and
cost control.

## Select the Engine First

Start with compatibility and vendor requirements before selecting availability
or scaling features.

| Engine | Choose it when | Important caution |
|---|---|---|
| RDS MySQL | Existing MySQL app, common web/CMS workload, straightforward transactions | Verify version, storage engine, and feature compatibility |
| RDS PostgreSQL | Advanced SQL, JSON, geospatial, complex queries, or extensions | Confirm required extensions and versions are supported |
| RDS MariaDB | Application is built and tested for MariaDB-specific behavior | MySQL and MariaDB are related but not identical |
| RDS SQL Server | Microsoft stack, T-SQL, reporting, or vendor requirement | Edition, features, and licensing affect cost |
| RDS Oracle | Oracle feature or vendor certification requirement | Review licensing and supported features |
| RDS Db2 | Existing Db2 application or vendor dependency | Confirm edition, licensing, and Region availability |
| Aurora MySQL-Compatible | MySQL-compatible app needs Aurora replicas, failover, Serverless v2, or Global Database | Test feature and version compatibility |
| Aurora PostgreSQL-Compatible | PostgreSQL-compatible app needs Aurora architecture and features | Validate extensions and compatibility |

Ask:

1. Which engine and version does the application already use?
2. Which extensions, stored procedures, licenses, or certifications are hard
   requirements?
3. Is the requirement availability, read scaling, variable compute, or global
   reads and disaster recovery?
4. Can the application tolerate an engine change?
5. What are the complete instance, storage, I/O, backup, replica, license, and
   transfer costs?

## Deployment Models

| Deployment | Topology | Read capacity | Main purpose |
|---|---|---|---|
| Single-AZ DB instance | One instance in one AZ | Writer serves reads and writes | Development, test, or non-HA workloads |
| Multi-AZ DB instance | Writer plus synchronous non-readable standby | Standby does not serve application reads | High availability and automatic failover |
| Multi-AZ DB cluster | Writer plus two readable instances across three AZs | Readers serve reads | High availability plus read capacity for supported engines |
| Read replica | Separate asynchronously updated instance | Replica serves reads | Read scaling, reporting, and manual promotion option |

Essential distinctions:

- Multi-AZ is primarily for availability.
- A traditional Multi-AZ standby is not a read-scaling target.
- A read replica is primarily for read scaling and can lag.
- A replica has its own endpoint and cost.
- Making the replica Multi-AZ protects that replica; source-to-replica
  replication remains asynchronous.
- Promotion is a manual action that creates an independent writable database.
- An RDS Multi-AZ DB cluster is not an Aurora DB cluster.

## Private Database Security

```text
Application EC2 SG -> TCP database port -> RDS SG
```

- Put the client and database in the intended VPC.
- Use a DB subnet group spanning at least two AZs.
- Set **Public access = No**.
- Reference the application Security Group as the database inbound source.
- Use Secrets Manager or another approved private store for credentials.
- Enable encryption at rest with an approved KMS key.
- Validate the RDS CA certificate and server identity for TLS in transit.
- Never expose MySQL `3306`, PostgreSQL `5432`, SQL Server `1433`, Oracle
  `1521`, or another database port to the internet.

## Backup and Recovery

| Feature | Created by | Retention | Restore result | Best use |
|---|---|---|---|---|
| Automated backup | RDS service | Configured retention window | New DB | Operational recovery and PITR |
| Manual snapshot | User or automation | Until explicitly deleted | New DB | Release checkpoint or longer-lived restore point |
| PITR | Automated backups plus transaction logs | Supported time inside restorable window | New DB | Recover just before a bad change |

Important facts:

- Restore creates a new database; it does not rewind the source.
- For RDS MySQL, InnoDB supports the expected automated backup and PITR path;
  MyISAM has restrictions.
- Backup window controls daily backup activity; retention controls how long
  backups are retained.
- Restore duration contributes to Recovery Time Objective.
- Retention and snapshot storage contribute to cost.
- Test the restore path rather than assuming a completed backup proves
  recoverability.

## RDS Read Replicas

Read replicas asynchronously copy changes from a source and use separate
endpoints. They support read-heavy workloads, reporting, and isolation of some
queries from the writer.

Validate:

- the expected source row reaches the replica;
- the replica reports read-only behavior;
- replication threads are healthy;
- lag is observed and monitored; and
- a write attempt fails.

`Seconds_Behind_Source = 0` means the replica is caught up at that instant, not
that asynchronous replication can never lag.

## RDS Proxy

RDS Proxy maintains and reuses database connections. It helps applications
such as Lambda functions and containers that create many short-lived
connections.

| Requirement | Proxy behavior |
|---|---|
| Connection burst | Pools and controls backend connections |
| Credential handling | Uses Secrets Manager and supports IAM authentication patterns |
| Database failover | Stable endpoint and reduced reconnection disruption |
| SQL result caching | Not provided; use a suitable cache such as ElastiCache |

A Proxy design includes the engine family, target database, secret, IAM role,
TLS requirement, VPC, at least two subnets, and Security Groups.

## Amazon Aurora

Aurora uses a distributed cluster volume across Availability Zones. One writer
accepts changes, Aurora replicas serve reads, and an eligible replica can be
promoted during failover.

| Endpoint | Use |
|---|---|
| Cluster/writer | DDL, inserts, updates, and deletes |
| Reader | Load-balanced read-only queries across readers |
| Instance | Diagnostics or direct access to one instance |
| Custom | Route a special workload to a selected subset |

Use role-based writer and reader endpoints for managed failover. Avoid
hard-coding a physical writer instance endpoint.

### Aurora Serverless v2

Choose it for compatible variable or unpredictable relational compute. It
scales within configured Aurora Capacity Unit bounds. Consumed compute,
storage, I/O, backups, and other enabled features still cost money.

### Aurora Global Database

One primary Region accepts writes; secondary Regions normally serve low-latency
reads and provide a managed cross-Region recovery architecture. Use switchover
for a planned healthy move and failover for outage recovery.

## AWS DMS Migration Modes

| Mode | Choose it when |
|---|---|
| Full load | Copy existing data and accept a migration window |
| CDC only | Baseline already exists; capture ongoing changes |
| Full load plus CDC | Copy existing data and continue changes until cutover |

DMS moves data. A heterogeneous migration can also require schema conversion.
A complete migration covers source and target preparation, network access,
endpoints, endpoint tests, table mappings, premigration assessment,
replication, validation, and cutover.

## Logical Table Backup Automation

RDS automated backups, snapshots, and PITR protect a complete DB instance or
cluster. A logical export such as `mysqldump` can protect or move selected
schemas and tables, but it is an additional recovery artifact rather than a
replacement for native backups.

A secure scheduled design uses:

- a dedicated database user with only the required table privileges;
- a Secrets Manager secret scoped to that backup job;
- an SSM-managed EC2 worker with access to only that secret and S3 prefix;
- a schema `2.2` Command document with validated `ENV_VAR` parameters;
- a separate State Manager dispatch role trusted by `ssm.amazonaws.com`; and
- an encrypted, private, versioned S3 bucket with repeated restore validation.

The association's optional S3 output stores command execution logs. The dump
script must upload the actual `.sql.gz` artifact separately.

## Exam Cues

- Managed AZ failover without read scaling -> Multi-AZ DB instance
- HA plus readable RDS instances across three AZs -> Multi-AZ DB cluster
- Reporting load is slowing writer -> read replica
- Recover immediately before an accidental change -> PITR
- Preserve a release checkpoint -> manual snapshot
- Thousands of short connections -> RDS Proxy
- Variable compatible relational compute -> Aurora Serverless v2
- Global Aurora reads and managed cross-Region DR -> Global Database
- Copy baseline and ongoing changes -> DMS full load plus CDC
- Scheduled export of one table -> SSM Command document plus State Manager

## Official References

- [Choosing an RDS database engine](https://docs.aws.amazon.com/AmazonRDS/latest/gettingstartedguide/choosing-engine.html)
- [Multi-AZ DB instance](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZSingleStandby.html)
- [Multi-AZ DB clusters](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.html)
- [RDS read replicas](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReadRepl.html)
- [Automated backups](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.html)
- [Point-in-Time Recovery](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PIT.html)
- [Create an RDS Proxy](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy-creating.html)
- [Aurora endpoints](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.Overview.Endpoints.html)
- [Aurora Serverless v2](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.html)
- [Aurora Global Database](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database.html)
- [AWS DMS replication](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_GettingStarted.Replication.html)
- [SSM document schemas and features](https://docs.aws.amazon.com/systems-manager/latest/userguide/documents-schemas-features.html)
- [Creating State Manager associations](https://docs.aws.amazon.com/systems-manager/latest/userguide/state-manager-associations-creating.html)
- [State Manager association dispatch roles](https://docs.aws.amazon.com/systems-manager/latest/userguide/state-manager-about.html)
