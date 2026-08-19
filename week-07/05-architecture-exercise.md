# Week 7 Architecture Exercise

Draw a production-oriented Week 7 data architecture. Include the relational
Day 13 path and a separate Day 14 DynamoDB and caching path.

## Required Components

- Application clients or services
- Private application tier across at least two AZs
- Systems Manager path for administration
- Application Security Group
- Private DB subnet group spanning at least two AZs
- RDS or Aurora writer and database Security Group
- TLS path on the engine port
- Secrets Manager and approved KMS keys
- Automated backups, PITR window, and manual snapshot
- Multi-AZ availability path
- Read scaling path through RDS read replica or Aurora reader endpoint
- CloudWatch metrics, RDS events, logs, and alarms
- RDS Proxy with distinct read/write and read-only endpoints between clients
  and the Aurora cluster
- Aurora Serverless v2 writer and reader across different AZs
- Optional DMS source, target, and replication path
- State Manager association, custom SSM Command document, dedicated database
  backup user, Secrets Manager secret, and private encrypted S3 backup prefix
- DynamoDB table with composite `PK`/`SK`, `GSI1`, `LSI1`, TTL, and Streams
- Idempotent Stream consumer Lambda and CloudWatch Logs
- Optional application Lambda using `GetItem`, `Query`, and `UpdateItem`
- A DynamoDB gateway VPC endpoint where it matches the application network
- Deliberate Global Tables, DAX, and ElastiCache decision boundaries

Do not place a database or standby in a public subnet merely to simplify the
diagram.

## Decision Table

Complete the reason column.

| Requirement | Choice | Reason |
|---|---|---|
| Existing MySQL application with minimal change | RDS MySQL or tested Aurora MySQL | |
| Advanced SQL, JSON, geospatial, or extensions | PostgreSQL-compatible option | |
| Automatic AZ failover without read scaling | Multi-AZ DB instance | |
| HA plus readable RDS instances across three AZs | Multi-AZ DB cluster | |
| Reporting load reduces writer performance | Read replica | |
| Recover just before an accidental delete | PITR | |
| Preserve a release checkpoint | Manual snapshot | |
| Thousands of short Lambda connections | RDS Proxy | |
| Variable compatible relational compute | Aurora Serverless v2 | |
| Global reads and managed cross-Region Aurora DR | Aurora Global Database | |
| Baseline and ongoing changes until cutover | DMS full load plus CDC | |
| Scheduled export of one table | SSM document plus State Manager and S3 | |
| Order lookup without customer ID | DynamoDB GSI | |
| Same customer ordered by status with strong reads | DynamoDB LSI | |
| Expire temporary sessions | DynamoDB TTL | |
| React to item changes | DynamoDB Streams plus Lambda | |
| Repeated eventual reads require microsecond latency | DAX | |
| Leaderboards, counters, or Pub/Sub | Valkey/Redis OSS | |
| Simple disposable object cache | Memcached | |

## Failure and Recovery Review

Explain what happens when:

1. The writer's AZ becomes unavailable in a Multi-AZ DB instance deployment.
2. A traditional Multi-AZ standby is queried for reporting.
3. A read replica falls behind during heavy write activity.
4. A developer accidentally deletes a row inside the PITR window.
5. The application hard-codes an Aurora writer instance endpoint and failover
   changes the writer.
6. A Lambda burst opens more connections than the database can sustain.
7. DMS completes the initial load while the source application continues
   writing.
8. The Aurora reader becomes writer during failover while applications use the
   stable cluster endpoint.
9. An RDS Proxy endpoint is available but its target health is not yet
   available.
10. The table-backup command can reach RDS but cannot write to its S3 prefix.
11. A hot DynamoDB partition throttles while total table capacity appears
    sufficient.
12. Lambda receives the same Stream record more than once.
13. An expired TTL item remains visible after its expiry timestamp.
14. A Global Table replica exists but client traffic does not fail over.

## Architecture Explanation

Write 250-400 words covering:

- engine compatibility and deployment choice;
- private networking, SG-to-SG access, encryption, TLS, and secrets;
- availability versus read-scaling decisions;
- backup, snapshot, PITR, RPO, and RTO;
- endpoint selection and failover behavior;
- connection management, Proxy target health, and observability;
- migration and cutover approach;
- why logical table export complements rather than replaces native backups;
- how an S3 dump is restored into an isolated database and validated safely;
- separation of EC2 execution and State Manager dispatch IAM roles;
- instance, storage, I/O, backup, replica, license, and transfer costs;
- access-pattern-first DynamoDB keys, indexes, consistency, and hot-key risk;
- TTL, Stream idempotency, and multi-Region routing behavior; and
- the boundary between DAX, Valkey/Redis OSS, and Memcached.

Mask database endpoints, account IDs, ARNs, Security Group IDs, secret names,
and private network details.
