# Week 7 Quick Revision

## Recall

1. Choose the database engine from compatibility before deployment features.
2. Single-AZ is not a high-availability design.
3. A traditional Multi-AZ DB instance standby does not serve application reads.
4. A read replica scales reads asynchronously and can lag.
5. Making a read replica Multi-AZ protects the replica; source replication is
   still asynchronous.
6. Restore from snapshot or PITR creates a new database.
7. Manual snapshots remain until deleted.
8. RDS MySQL automated backup and PITR design should use supported storage
   engines such as InnoDB.
9. RDS Proxy pools connections; it does not cache query results.
10. Aurora writer endpoint handles changes; reader endpoint distributes reads.
11. Aurora Serverless v2 scales compute inside configured ACU bounds.
12. Aurora Global Database has one primary write Region and secondary read
    Regions.
13. DMS full load copies the baseline; CDC captures ongoing changes.
14. Full load plus CDC supports low-downtime migration toward cutover.
15. Keep RDS private and allow its port only from the application SG.
16. Aurora failover changes the writer instance while the cluster endpoint
    remains stable.
17. An available Proxy endpoint is not sufficient; confirm target health.
18. A logical table dump complements native snapshots, automated backups, and
    PITR; it does not replace them.
19. The EC2 role performs the backup, while the State Manager dispatch role
    sends the approved command to the managed node.
20. Restore testing must use an isolated database; never import the table dump
    over the active training or production schema.

## Decision Table

| Requirement | Best direction |
|---|---|
| Existing MySQL application | RDS MySQL or compatible Aurora after testing |
| Complex SQL, JSON, geospatial, extensions | PostgreSQL-compatible engine |
| Microsoft ecosystem | RDS SQL Server |
| Automatic AZ failover | Multi-AZ deployment |
| Reduce read load | Read replica or Aurora reader |
| Recover just before accidental change | PITR |
| Long-lived release checkpoint | Manual snapshot |
| Short-lived connection storm | RDS Proxy |
| Variable compatible relational compute | Aurora Serverless v2 |
| Global Aurora reads and managed DR | Aurora Global Database |
| Existing data plus ongoing changes | DMS full load plus CDC |

## Day 14 Recall

1. DynamoDB design begins with named access patterns.
2. A Query requires partition-key equality; a sort-key condition narrows and
   orders the result.
3. A Scan reads data before applying a filter.
4. A GSI can use another partition key and supports eventual reads only.
5. An LSI keeps the table partition key, must be created with the table, and
   can support strong reads.
6. On-demand capacity suits unknown or variable traffic; provisioned capacity
   suits measurable, forecastable traffic.
7. Reads round to 4 KB blocks and writes round to 1 KB blocks.
8. TTL stores epoch seconds and deletes asynchronously.
9. Streams retain change records for up to 24 hours and Lambda consumers must
   be idempotent.
10. Global Tables require routing, dependency readiness, and failover testing
    in addition to replicas.
11. DAX accelerates repeated eventually consistent DynamoDB reads.
12. Valkey/Redis OSS supports rich data structures and Pub/Sub; Memcached is a
    simple disposable object cache.

## Important Traps

- Multi-AZ is not automatically read scaling.
- Read replicas are not synchronous standby replacements.
- A replica endpoint is different from the source endpoint.
- Replica lag can be non-zero and must be monitored.
- PITR does not rewind the source database.
- A backup existing is not proof that restore meets the required RTO.
- Public access set to No does not replace correct Security Groups and routes.
- S3-style public-access concepts do not apply to a database port; never expose
  the DB port publicly.
- RDS-managed credentials must still be retrieved and used privately.
- RDS Proxy is not ElastiCache.
- A Proxy read-only endpoint routes connections to readers; it does not make a
  writer endpoint query cache.
- Applications must retry interrupted connections and transactions after
  failover.
- A State Manager association's S3 output location stores command logs, not the
  `.sql.gz` file created by the backup script.
- A versioned S3 bucket is not empty until current objects, prior versions, and
  delete markers are removed.
- Aurora Multi-AZ storage architecture is not the same as an RDS Multi-AZ DB
  cluster.
- DMS moves data; heterogeneous migrations can also require schema conversion.

## Day 13 Practice Questions

> **Disclaimer:** These are original educational questions modelled on the
> SAA-C03 style. They are not real exam questions or exam dumps.

### Question 1

A production RDS MySQL database needs automatic failover to another AZ. The
standby does not need to serve reporting queries. Which design fits best?

- A. Single-AZ with a manual snapshot
- B. Multi-AZ DB instance
- C. Same-Region read replica only
- D. RDS Proxy

<details><summary>Show Answer</summary>

**Answer: B**

A Multi-AZ DB instance provides a synchronously maintained standby and managed
failover. The traditional standby is not a read target.

</details>

### Question 2

Reporting queries are slowing the RDS writer. The reports tolerate small
replication lag. What should be added?

- A. Read replica
- B. Manual snapshot
- C. Larger backup window
- D. Secrets Manager rotation

<details><summary>Show Answer</summary>

**Answer: A**

An asynchronous read replica offloads read-only reporting work from the writer.

</details>

### Question 3

A row was deleted accidentally at 10:05 UTC. The database has automated
backups and a valid restorable window. Which recovery method is most precise?

- A. Reboot the source
- B. PITR to a time immediately before 10:05
- C. Promote the read replica automatically
- D. Create an RDS Proxy

<details><summary>Show Answer</summary>

**Answer: B**

PITR creates a new database at a supported point before the accidental delete.

</details>

### Question 4

Thousands of Lambda invocations create short-lived database connections and
threaten connection capacity. Which service directly addresses this problem?

- A. RDS Proxy
- B. Manual snapshot
- C. Aurora custom endpoint
- D. DMS CDC

<details><summary>Show Answer</summary>

**Answer: A**

RDS Proxy pools and reuses backend connections. It does not cache SQL results.

</details>

### Question 5

A migration must copy existing relational data and continue applying changes
until a low-downtime cutover. Which DMS mode should be selected?

- A. Full load only
- B. CDC only with no baseline
- C. Full load plus CDC
- D. Multi-AZ DB instance

<details><summary>Show Answer</summary>

**Answer: C**

Full load copies the existing baseline, and CDC continues ongoing source
changes until cutover.

</details>

## Day 14 Practice Questions

### Question 6

An application knows an order ID but not the customer partition key. Which
design supports an efficient lookup?

- A. A frequent Scan with a filter
- B. A GSI whose partition key is the order ID
- C. TTL on the order
- D. A read replica

<details><summary>Show Answer</summary>

**Answer: B**

A GSI creates the alternate partition-key access path required by the request.

</details>

### Question 7

Expired session items must be removed eventually, but deletion does not need
to happen at an exact second. Which DynamoDB feature fits?

- A. TTL
- B. DAX
- C. LSI
- D. Global Tables

<details><summary>Show Answer</summary>

**Answer: A**

TTL provides asynchronous lifecycle deletion using an epoch-seconds attribute.

</details>

### Question 8

A workload repeatedly reads the same DynamoDB items with eventual consistency
and requires microsecond latency. Which service is the closest fit?

- A. RDS Proxy
- B. DAX
- C. Memcached with SQL
- D. DynamoDB Scan

<details><summary>Show Answer</summary>

**Answer: B**

DAX is a DynamoDB-compatible cache for repeated eventually consistent reads.

</details>

## Final Check

- [ ] I can select an engine from compatibility and licensing requirements.
- [ ] I can compare Single-AZ, both Multi-AZ patterns, and read replicas.
- [ ] I can design private SG-to-SG database access with TLS and secrets.
- [ ] I can choose automated backup, manual snapshot, or PITR.
- [ ] I can explain replica lag, read-only behavior, and promotion.
- [ ] I can explain RDS Proxy without calling it a cache.
- [ ] I can route Aurora reads and writes through the correct endpoint.
- [ ] I can explain Serverless v2 and Global Database.
- [ ] I can select DMS full load, CDC, or full load plus CDC.
- [ ] I know every billable Day 13 resource that must be removed.
- [ ] I can explain the SSM document, State Manager, IAM, secret, and S3 path
      used for the scheduled logical table backup.
- [ ] I can restore an S3 logical dump safely and validate that the source was
      not overwritten.
- [ ] I can map access patterns to DynamoDB keys, a GSI, or an LSI.
- [ ] I can compare Query and Scan behavior.
- [ ] I can calculate basic RCU/WCU requirements.
- [ ] I can explain TTL timing and Stream retry/idempotency behavior.
- [ ] I can choose between Global Tables, DAX, Valkey/Redis OSS, and Memcached.
- [ ] I know every billable or public Day 14 resource that must be removed.

## Practical Knowledge Check

Complete these before viewing your notes:

1. Multi-AZ is mainly for __________.
2. A read replica is mainly for __________.
3. PITR restores to a __________ database endpoint.
4. The Aurora cluster endpoint follows the current __________.
5. The Aurora reader endpoint is used for __________ traffic.
6. RDS Proxy pools and __________ database connections.
7. Aurora Serverless v2 capacity is measured in __________.
8. Aurora Global Database uses __________ replication between Regions.
9. DMS Full load plus CDC copies existing data and then __________.
10. A failed transaction during failover still requires application
    __________ logic.
