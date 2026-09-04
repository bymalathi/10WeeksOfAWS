# Week 9 Architecture Exercise

Design an event-driven order-processing architecture using AWS messaging and
streaming services. Include synchronous and asynchronous pathways, apply
filtering and routing rules, and demonstrate end-to-end data flow from capture
to analytics.

## Required Components

- **Messaging tier:** SQS Standard queue, SQS FIFO queue, SNS topic with filtering
- **Event routing:** EventBridge custom bus with pattern-based rules and multiple targets
- **Scheduling:** EventBridge Scheduler for one-time and recurring tasks
- **Streaming:** Kinesis Data Stream for high-throughput clickstream data
- **Pipeline:** Firehose delivery stream from Kinesis to S3 with buffering
- **Storage:** Private S3 bucket with encryption and date-based partitioning
- **Visibility:** CloudWatch metrics, queues message count, Kinesis records, Firehose delivery
- **Dead-letter handling:** SQS DLQ with redrive capability and monitoring
- **Security:** Least-privilege IAM roles, encryption at rest, Security Group isolation
- **Cost tracking:** Resource tagging with `Project = CloudAdhar-AWS-Zero-To-Hero`

## Message Flow Diagram

Include these pathways:

```text
Order Client
  ├─> SNS topic (all orders)
  │     ├─> SQS Standard queue (all orders)
  │     └─> SQS Priority queue (HIGH priority only via filter)
  │
  ├─> EventBridge custom bus
  │     └─> Rule: amount > 5000
  │         └─> SQS Priority queue (high-value alerts)
  │
  └─> EventBridge Scheduler
        └─> One-time: Payment reminder to Priority queue

Clickstream events
  ├─> Kinesis Data Stream (partition key: customer ID)
  │     └─> Firehose stream
  │         └─> S3 bucket (YYYY/MM/dd/HH partitions)
  │             └─> CloudWatch metrics on delivery
```

## Architecture Decisions Table

Complete the reason column for each decision.

| Requirement | Choice | Reason |
|---|---|---|
| Multiple independent subscribers to order events | SNS Standard topic | |
| Preserve message ordering within an order group | SQS FIFO queue | |
| Failed messages that need investigation | SQS DLQ with retention | |
| Filter messages by attribute without code changes | SNS filter policy | |
| Route based on order amount | EventBridge rule with numeric condition | |
| Send payment reminder at specific time | EventBridge Scheduler one-time | |
| Partition clickstream data by customer | Kinesis with customer-ID partition key | |
| Buffer and deliver clickstream to S3 for analytics | Firehose with S3 destination | |
| Batch storage with low cost | Firehose 5 MiB buffer and 300-second interval | |
| Exactly-once delivery inside order group | SQS FIFO with deduplication | |
| Scale to thousands of concurrent orders | SQS Standard queue unlimited throughput | |
| Near-real-time analytics on clickstream | Kinesis on-demand capacity mode | |
| Long-term retention of orders | SQS message retention 4 days | |
| Event-driven integration without code coupling | EventBridge versus direct SNS/SQS | |
| Private S3 for analytics data | Block public access + encryption + partitioning | |

## Failure and Recovery Review

Explain what happens when:

1. An SNS message arrives while the priority SQS queue is full.
2. A message is received from SQS but the consumer crashes before deleting it.
3. A FIFO message arrives without a message deduplication ID.
4. The EventBridge rule condition does not match an event.
5. An EventBridge Scheduler one-time task fails after three retries.
6. A Kinesis consumer is slow and records accumulate in the shard.
7. Firehose buffering is set to 5 MiB but only 2 MiB arrives; the interval is 300 seconds.
8. An SNS filter policy is updated while messages are in transit.
9. A DLQ message is redriven to the source queue and fails again.
10. The SQS queue visibility timeout is too short for processing time.
11. Multiple EventBridge rules target the same SQS queue with overlapping patterns.
12. Kinesis records arrive out of order from different shards.
13. An S3 prefix already exists with previous Firehose data.
14. CloudShell runs out of time while waiting for Firehose to buffer and deliver.

## Architecture Explanation

Write 250-400 words covering:

- **Message flow:** How orders move from API to SQS, SNS, and EventBridge.
- **Filtering and routing:** SNS filter policies versus EventBridge rules. When to use each.
- **Queue types:** Why Standard for throughput and FIFO for ordering. Trade-offs.
- **Visibility timeout and DLQ:** How consumers process safely with failure handling.
- **Event patterns:** EventBridge condition syntax for amount > 5000 and other rules.
- **Scheduling:** One-time versus recurring schedules. Automatic cleanup after execution.
- **Kinesis partitioning:** Partition key strategy to distribute by customer. Ordering per shard.
- **Firehose buffering:** Size and interval trade-offs between latency and cost.
- **S3 organization:** UTC-based partitioning for easy querying in Athena or S3 Select.
- **Idempotent processing:** Why consumers must handle duplicate messages safely.
- **Cost estimation:** SQS API charges, SNS topic delivery, EventBridge invocations, Kinesis shards, Firehose GB delivered, S3 storage.
- **Monitoring:** CloudWatch metrics for queue depth, visibility timeout, delivery success.
- **Security:** Why DLQ retention is longer than source queue. Least-privilege IAM roles.
- **Failure scenarios:** What happens when message processing fails. Redrive policy behavior.
- **Extension paths:** How to add Lambda transformers, cross-region replication, or analytics.

## Drawing Tips

- Use different colors for SQS (orange), SNS (red), EventBridge (yellow), Kinesis (blue), Firehose (purple), S3 (green).
- Show message flow with arrows and label throughput expectations (e.g., "millions/day").
- Include a legend for "confirmed delivery", "eventual consistency", "strict ordering", "filter applied".
- Label each SQS queue with its type (Standard or FIFO) and retention period.
- Mark the DLQ with a special symbol and connect it to the source queue.
- Show the EventBridge rule pattern condition inline or in a separate decision-tree box.
- Display S3 partitioning structure (YYYY/MM/dd/HH) to show time-based organization.
- Add CloudWatch and monitoring layers to show operational visibility.

## Comparison: This Week's Architecture vs Week 8

| Aspect | Week 8 (Hybrid Connectivity) | Week 9 (Messaging and Streaming) |
|---|---|---|
| Primary pattern | Synchronous API calls across VPCs | Asynchronous decoupled message passing |
| Failure mode | Client waits for response or times out | Message persists in queue or DLQ |
| Ordering | Network-dependent | Guaranteed per FIFO group or shard |
| Scalability | Limited by target capacity | Scale independently (thousands concurrent) |
| Integration style | Direct service-to-service | Pub/Sub, event-driven, fan-out |
| Monitoring | Connection latency, throughput | Queue depth, message age, delivery success |
