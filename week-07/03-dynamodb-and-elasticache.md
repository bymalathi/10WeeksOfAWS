# DynamoDB and ElastiCache

Day 14 moves from relational database choices to access-pattern-first NoSQL
design and caching. Use this guide to decide which DynamoDB key, index,
capacity, lifecycle, change-capture, replication, or cache option matches a
measurable requirement.

The complete classroom handout is available as the
[Day 14 student guide](./AWS_Zero_To_Hero_Day14_DynamoDB_and_ElastiCache_Student_Guide.pdf).

## Learning Outcomes

- Translate named access patterns into partition-key and sort-key designs.
- Prefer `GetItem` or `Query` over a frequent table `Scan`.
- Distinguish a Global Secondary Index from a Local Secondary Index.
- Choose on-demand or provisioned capacity and estimate RCU/WCU needs.
- Explain TTL deletion behavior and DynamoDB Streams processing guarantees.
- Select Global Tables only for justified multi-Region requirements.
- Use DAX for repeated eventually consistent DynamoDB reads when metrics
  justify a cache.
- Choose Valkey/Redis OSS or Memcached for the appropriate ElastiCache use
  case.
- Apply IAM, encryption, private networking, monitoring, and cleanup controls.

## Access-Pattern-First Design

DynamoDB design starts with the requests the application must serve, not with
normalized entities or joins.

1. List each business access pattern in plain language.
2. Record the exact values known when the request arrives.
3. Choose a high-cardinality value that supports equality as the partition
   key.
4. Use the sort key for grouping, hierarchy, chronological order, prefixes, or
   ranges.
5. Validate item growth, item size, hot-key risk, and write amplification.

### Orders Example

| Access pattern | Key path |
|---|---|
| Get customer `C101` profile | `PK=CUSTOMER#C101`, `SK=PROFILE` |
| List `C101` orders newest first | Same `PK`; `SK` begins with `ORDER#` and contains an ISO timestamp |
| Find `O9001` without customer ID | `GSI1PK=ORDER#O9001` |
| List `C101` orders by status | Same `PK`; `LSI1SK=STATUS#status#timestamp` |
| Expire a temporary session | Numeric `ExpiresAt` TTL attribute |
| React when an order changes | Stream with `NEW_AND_OLD_IMAGES` |

Example item shapes:

```text
Customer profile
PK = CUSTOMER#C101
SK = PROFILE

Order
PK      = CUSTOMER#C101
SK      = ORDER#2026-08-16T18:30:00Z#O9001
GSI1PK  = ORDER#O9001
GSI1SK  = CUSTOMER#C101
LSI1SK  = STATUS#PAID#2026-08-16T18:30:00Z
```

`Query` requires partition-key equality and can apply a sort-key condition.
`Scan` reads the table or index before applying a filter, so a
`FilterExpression` does not turn a Scan into an efficient lookup.

## GSI versus LSI

| Decision | Global Secondary Index | Local Secondary Index |
|---|---|---|
| Partition key | May differ from the base table | Must match the base table |
| Sort key | Optional and may differ | Required and differs from the base sort key |
| Creation | Can be added or removed later | Must be created with the table |
| Consistency | Eventually consistent reads only | Eventual or strong reads |
| Provisioned capacity | Separate throughput | Shares table throughput |
| Typical use | Query through another partition key | Alternate order within one partition |

Use only indexes tied to named access patterns. Every index adds storage and
write work. Sparse GSIs are useful when only selected item types contain the
index key attributes.

Projection choices:

- `KEYS_ONLY` stores table and index keys.
- `INCLUDE` adds a small, stable set of projected attributes.
- `ALL` returns the complete indexed item but increases storage and write cost.

## Capacity Decisions

| Requirement | Direction |
|---|---|
| New, unpredictable, intermittent, or spiky traffic | On-demand (`PAY_PER_REQUEST`) |
| Stable traffic with reliable forecasts | Provisioned plus auto scaling |

Capacity-unit fundamentals:

- One RCU supports one strongly consistent read per second for an item up to
  4 KB, or two eventually consistent reads per second.
- One WCU supports one write per second for an item up to 1 KB.
- Reads round up in 4 KB blocks and writes round up in 1 KB blocks.
- Transactions consume more capacity than equivalent non-transactional
  operations.
- A provisioned GSI needs enough capacity for the index entries written to it.

When throttling occurs, check hot keys, item size, consistency, scans, filters,
and index write pressure before increasing total capacity.

## TTL and Streams

### Time to Live

- Store TTL as a Number containing Unix epoch time in seconds.
- Deletion is asynchronous; an expired item may remain visible for some time.
- Exclude expired items in application reads when immediate invisibility is
  required.
- TTL is a lifecycle and cost-control feature, not an exact scheduler.
- A service TTL deletion does not consume base-table write throughput, but
  replicated deletes can consume capacity in Global Table replica Regions.

### DynamoDB Streams

Streams retain item-level change records for up to 24 hours. Select the view
that matches the consumer:

| View | Record content |
|---|---|
| `KEYS_ONLY` | Changed item's primary key |
| `NEW_IMAGE` | Item after the change |
| `OLD_IMAGE` | Item before the change |
| `NEW_AND_OLD_IMAGES` | Both versions for comparison or auditing |

Ordering is preserved for changes to the same item, not as one global table
order. Lambda can retry records, so consumers must be idempotent and should
handle partial batch failures deliberately.

## Global Tables

Global Tables provide managed multi-Region, multi-active replication. A
replica alone does not move users: the full design also needs Regional
endpoints, routing, dependency readiness, health checks, observability, retry
logic, conflict handling, and a tested failover runbook.

Before choosing Global Tables:

1. Confirm the business needs multi-Region reads and writes.
2. Select the required consistency model during design.
3. Plan IAM, KMS keys, routing, deployment, and Region-isolation procedures.
4. Model replica storage, replication writes, and cross-Region transfer cost.
5. Test application behavior during concurrent writes and Regional failure.

## DAX and ElastiCache

Fix the DynamoDB access path before adding a cache: replace frequent scans,
improve key distribution, reduce payloads, choose permitted consistency, and
tune capacity from metrics.

| Requirement | Best direction |
|---|---|
| Repeated eventually consistent DynamoDB reads needing microsecond latency | DAX |
| Strongly consistent DynamoDB read | Read DynamoDB directly |
| Leaderboard, rate limiter, counters, queues, rich structures, or Pub/Sub | Valkey/Redis OSS |
| Simple disposable object cache | Memcached |

DAX is Regional and serves cached eventually consistent reads. It is a poor
fit for strong reads, write-heavy workloads, low repeat-read rates, or cases
where normal DynamoDB latency already meets the objective.

ElastiCache security should use approved private subnets, application-SG to
cache-SG rules, supported encryption and authentication, and secret storage.
Monitor cache-hit ratio, evictions, memory, connections, CPU, and replication
lag.

## Security, Reliability, and Cost Guardrails

- Use a scoped IAM training role and synthetic data, never the root user.
- Restrict DynamoDB actions to the Day 14 table and required indexes.
- Consider a DynamoDB gateway VPC endpoint and a constrained endpoint policy
  for supported VPC traffic.
- Keep DAX and ElastiCache in approved private subnets; do not expose cache
  ports publicly.
- Do not create DAX, ElastiCache, or Global Table resources only for a console
  screenshot.
- Treat cached data as disposable unless the chosen engine and deployment
  intentionally provide durability.
- Delete public demo URLs, Lambda mappings and functions, tables, IAM roles,
  cache resources, log groups, endpoints, and Security Groups created only for
  the lab.

## Decision Check

| Scenario | Select |
|---|---|
| Find an order using only `orderId` | GSI on order ID |
| Same customer, alternate order with strong reads | LSI planned at table creation |
| Remove sessions after expiry | TTL |
| Send changed items to a function | Streams plus Lambda |
| Active-active workload in several Regions | Global Tables |
| DynamoDB-compatible repeated eventual reads | DAX |
| Gaming leaderboard and atomic counters | Valkey/Redis OSS |
| Disposable rendered-page cache | Memcached |

## Official AWS References

- [Partition-key design](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-partition-key-design.html)
- [Secondary-index guidance](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-indexes-general.html)
- [Capacity modes](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/capacity-mode.html)
- [Time to Live](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/TTL.html)
- [DynamoDB Streams](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.html)
- [Global Tables](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GlobalTables.html)
- [DynamoDB Accelerator](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DAX.html)
- [ElastiCache engine selection](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/SelectEngine.html)
