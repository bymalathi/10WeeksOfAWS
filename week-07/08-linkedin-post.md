# Week 7 Learn-in-Public Posts

Write in your own voice and publish only sanitized evidence.

## Day 13

```text
Week 7, Day 13 of #10WeeksOfAWS

Today I built private Amazon RDS MySQL and Aurora Serverless v2 databases and
connected from an EC2 client using Security Group references and verified TLS.

My availability versus scaling decision:
<Single-AZ/Multi-AZ/read replica/Aurora choice -> reason>

My recovery evidence:
<Manual snapshot, automated backup, or PITR result>

My scaling and failover evidence:
<Read replica result, Aurora writer/reader endpoint test, cross-AZ failover,
and RDS Proxy read/write versus read-only result>

My migration lesson:
<Global Database or DMS decision>

My automation evidence:
<SSM document, State Manager schedule, two encrypted table backups, and a safe
restore into an isolated test database>

I removed the RDS and Aurora databases, Proxy, replica, restore, snapshots,
scheduled association, S3 backup versions, secrets, EC2 client, and other
training resources after collecting evidence.

#AWS #AmazonRDS #AmazonAurora #DatabaseMigration #CloudAdhar #TrainWithShubham
```

## Day 14

```text
Week 7, Day 14 of #10WeeksOfAWS

Today I designed and built a DynamoDB orders workflow from named access
patterns rather than starting with generic keys.

My key and index design:
<PK/SK collection, GSI reverse lookup, and LSI status-order explanation>

My capacity and lifecycle lesson:
<On-demand versus provisioned decision and TTL behavior>

My event-driven evidence:
<Status update -> DynamoDB Stream -> Lambda -> CloudWatch old/new image>

My caching decision:
<When I would choose DAX, Valkey/Redis OSS, or Memcached>

I removed the temporary public Function URL, Lambda functions and trigger,
DynamoDB tables, IAM roles, and any other lab-only resources after collecting
sanitized evidence.

#AWS #DynamoDB #AWSLambda #ElastiCache #CloudAdhar #TrainWithShubham
```

Never publish passwords, secrets, endpoints, account IDs, ARNs, Security Group
IDs, private network details, connection strings, or billing data.
