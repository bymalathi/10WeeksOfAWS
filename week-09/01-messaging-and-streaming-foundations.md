# Day 17 - Messaging and Streaming Foundations

## What is Messaging?

Messaging enables asynchronous communication between independent application components
without requiring real-time direct connections. Instead of calling a service and waiting
for a response (synchronous), you send a message to a queue or topic and both sender and
receiver continue their work independently.

### Why Messaging?

- **Decoupling:** Sender and receiver don't need to know about each other.
- **Reliability:** If a receiver crashes, messages wait in a queue.
- **Scalability:** Multiple receivers can process messages in parallel.
- **Resilience:** Temporary failures don't cause entire workflows to fail.
- **Throttling:** Slow consumers don't overload fast producers.

### Synchronous vs Asynchronous

**Synchronous (Request-Response):**
```
Client -> Request -> Service -> Response -> Client (waits)
```

**Asynchronous (Message Queue):**
```
Client -> Send Message -> Queue -> Receiver picks up -> Process
```

---

## Amazon SQS (Simple Queue Service)

SQS is a fully managed message queue service. Producers send messages; consumers poll
for and process them.

### SQS Concepts

- **Queue:** A temporary message buffer (FIFO order only in FIFO queues).
- **Message:** A unit of data (up to 1024 KiB by default, up to 2 GiB with S3).
- **Visibility Timeout:** Time a message is hidden after being received but before being deleted.
- **Long Polling:** Wait for a message to arrive instead of returning immediately with empty.
- **Message Retention:** How long an unprocessed message stays in the queue (1 minute to 14 days).
- **Delivery Delay:** Time before a message becomes visible after being sent.

### SQS Queue Types

#### Standard Queue

- Best-effort FIFO ordering (not guaranteed).
- At-least-once delivery (duplicates possible).
- Nearly unlimited throughput (1000s per second).
- Use for: Most applications where order doesn't matter.

#### FIFO Queue

- Strict FIFO ordering (messages processed in order).
- Exactly-once processing (with deduplication).
- Lower throughput (300 per second without batching, 3000 with batching).
- Use for: Order-critical workflows (payment processing, inventory updates).

### Visibility Timeout and Receive-Process-Delete Pattern

```
1. Receive message -> message becomes invisible for visibility timeout
2. Process message (consume, transform, delete from database)
3. Delete message from queue (within visibility timeout)

If step 2 fails or times out:
- Message remains in queue and becomes visible again
- Consumer should be idempotent (process multiple times safely)
- After max receive count exceeded, message moves to DLQ
```

### Dead-Letter Queue (DLQ)

A separate queue that receives messages after they fail processing repeatedly.

- Configure DLQ on source queue (max receives = 3 means after 4th receive, move to DLQ).
- Keep DLQ messages longer than source queue (source: 4 days, DLQ: 14 days).
- Redrive: Move messages from DLQ back to source for reprocessing.
- Use for: Debugging, auditing, and retrying failed messages.

### Long Polling vs Short Polling

**Short Polling (default):**
- Consumer polls immediately.
- If no message, returns empty response.
- Higher API calls = higher cost.

**Long Polling (ReceiveMessageWaitTime > 0):**
- Consumer waits up to configured time for a message.
- If message arrives, returns immediately.
- If timeout expires, returns empty.
- Lower API calls = lower cost.

---

## Amazon SNS (Simple Notification Service)

SNS is a fully managed pub/sub service. One producer publishes to a topic; multiple
subscribers receive copies.

### SNS Concepts

- **Topic:** A communication channel (like a radio station).
- **Publisher:** Sends messages to topic (doesn't know subscribers).
- **Subscriber:** Receives messages published to topic.
- **Message Attribute:** Metadata about the message (used for filtering).

### SNS Topic Types

#### Standard Topic

- Best-effort delivery (messages might be lost).
- Nearly unlimited throughput.
- No guaranteed ordering.
- Use for: Non-critical notifications.

#### FIFO Topic

- Exactly-once processing within a message group.
- Strict ordering within a message group.
- Lower throughput.
- Use for: Order-critical fan-out scenarios.

### SNS vs SQS Comparison

| Feature | SNS | SQS |
|---|---|---|
| Pattern | Pub/Sub (1-to-many) | Point-to-point (1-to-1) |
| Delivery | Push to subscribers | Pull from queue |
| Ordering | Standard topic (no guarantee) | FIFO queue (guaranteed) |
| Deduplication | Standard topic (no) | FIFO queue (yes) |
| Use Case | Broadcast, notifications | Tasks, work queue |

### SNS Subscription Filtering

Filter subscriptions by message attributes so only matching messages are delivered.

**Example Filter Policy (JSON):**
```json
{
  "priority": ["HIGH"],
  "department": ["BILLING", "OPERATIONS"]
}
```

This means: Only deliver messages where `priority = HIGH` **AND** `department` is `BILLING` or `OPERATIONS`.

---

## AWS EventBridge

EventBridge is a serverless event-driven architecture service. It matches events against
rules and routes them to targets.

### EventBridge Concepts

- **Event Bus:** A router for events (default, partner, or custom).
- **Event:** A JSON message describing what happened (source, detail-type, detail).
- **Rule:** Defines which events match and where to route them.
- **Target:** A service that receives matched events (SQS, Lambda, SNS, Kinesis, etc.).
- **Event Pattern:** JSON condition to match events (source, detail-type, detail fields).

### Event Pattern Example

```json
{
  "source": ["cloudadhar.orders"],
  "detail-type": ["OrderCreated"],
  "detail": {
    "amount": [
      {
        "numeric": [">", 5000]
      }
    ]
  }
}
```

This matches: Orders from `cloudadhar.orders` with amount > 5000.

### Custom Event Buses

Instead of using the default event bus, create custom buses for:
- Isolating application events by domain (orders, payments, inventory).
- Controlling who can publish and subscribe.
- Organizing rules by application layer.

### EventBridge vs SNS

| Feature | EventBridge | SNS |
|---|---|---|
| Matching | Content-based pattern | Message attributes only |
| Targets | 60+ AWS services | HTTP, email, SMS, Lambda, SQS |
| Scalability | Highly scalable | Very scalable |
| Use Case | Event-driven workflows | Simple notifications |

---

## AWS EventBridge Scheduler

EventBridge Scheduler replaces cron jobs, at tasks, and time-based triggers.

### Scheduler Concepts

- **One-time Schedule:** Execute once at a specific date and time.
- **Recurring Schedule:** Execute on a cron expression or rate.
- **Target:** Any AWS service or HTTP endpoint.
- **Retry Policy:** How many times to retry if target fails.
- **DLQ:** Where to send events if all retries fail.

### One-Time Schedule Example

Execute a payment reminder at 2026-08-30 16:45:00 IST.

- Scheduler creates the schedule.
- At scheduled time, invokes the target (SQS SendMessage).
- After successful delivery, automatically deletes the schedule.

### Recurring Schedule Example

Execute every day at 9:00 AM IST.

```
rate: 1 day
or
cron: 0 3:30 * * ? *  (UTC for 9:00 AM IST)
```

---

## Amazon Kinesis Data Streams

Kinesis is a real-time data streaming service for high-throughput, low-latency analytics.

### Kinesis Concepts

- **Stream:** A sequence of data records (like a river).
- **Record:** A single data element (JSON, blob, up to 1 MB).
- **Partition Key:** Used to distribute records across shards (same key → same shard).
- **Shard:** A unit of throughput (1 MB inbound, 1 MB outbound per second).
- **Sequence Number:** Assigned by Kinesis; unique within shard; indicates order.
- **Iterator:** A pointer to read records from a shard (from TRIM_HORIZON, LATEST, etc.).

### Capacity Modes

#### On-Demand

- Automatically scales based on traffic.
- Pay per GB written and read.
- Use for: Unpredictable or bursty workloads.

#### Provisioned

- Fixed shards; you manage throughput.
- Pay per shard per hour.
- Use for: Predictable, steady workloads.

### Partition Key Distribution

Records with the same partition key go to the same shard (guarantees ordering within that key).

```
Partition Keys: customer-C001, customer-C002, customer-C003, ...
Shards: 1, 2, 3 (distributed by hash of partition key)

All records for customer-C001 → Shard 1
All records for customer-C002 → Shard 2
All records for customer-C003 → Shard 3
```

**Important:** Ordering is per-shard, not stream-wide. Multiple shards can process in parallel.

### Kinesis Consumer Patterns

- **Kinesis Consumer Library (KCL):** Official library for consuming with checkpointing.
- **Lambda Trigger:** Automatically invoke Lambda when records arrive.
- **Kinesis Firehose:** Transform and deliver to S3, Redshift, Elasticsearch, or Splunk.

---

## Amazon Data Firehose

Firehose is a managed data pipeline that loads streaming data into data lakes and data warehouses.

### Firehose Concepts

- **Delivery Stream:** A named entity that captures and delivers data.
- **Source:** Where data comes from (Kinesis, direct API, CloudWatch Logs, SNS).
- **Destination:** Where data is delivered (S3, Redshift, Elasticsearch, Datadog, Splunk, HTTP).
- **Buffer Size:** Data is batched until this size is reached (5 MB default).
- **Buffer Interval:** Time to wait if buffer not full (300 seconds default).
- **Transformation:** Optional Lambda function to transform records.

### S3 Prefix and Partitioning

Firehose delivers objects to S3 with paths like:
```
s3://bucket/YYYY/MM/dd/HH/KDS-S3-...-YYYY-MM-dd-HH-mm-ss-UUID
```

UTC time is used (not local time). A record delivered at 10:10 PM IST (UTC 16:40) appears under the UTC 16 folder.

### Firehose vs Kinesis

| Feature | Kinesis | Firehose |
|---|---|---|
| Latency | Sub-second | Buffered (minutes) |
| Use Case | Real-time processing | Data pipeline to S3/warehouse |
| Consumer | Your code, Lambda | Managed (S3, Redshift, etc.) |
| Cost | Per shard-hour | Per GB delivered |

---

## Amazon MQ and Amazon MSK (Selection Only)

### Amazon MQ

Managed message broker for **RabbitMQ** or **ActiveMQ** engines.

- Use if: Existing application depends on RabbitMQ or ActiveMQ protocols.
- Provides: Open-source broker with managed deployment, scaling, patching.
- Not use if: AWS-native SQS, SNS sufficient or want serverless.

### Amazon MSK (Managed Streaming for Apache Kafka)

Managed Kafka cluster and operations.

- Use if: Applications need Kafka consumer groups, topic retention, partition rebalancing.
- Provides: VPC deployment, IAM/SASL authentication, encryption, monitoring.
- Not use if: Kinesis sufficient or don't need Kafka-specific features.

---

## Event-Driven Architecture Patterns

### Fan-Out Pattern (SNS to Multiple SQS)

```
Producer -> SNS topic -> SQS queue 1 (all messages)
                      -> SQS queue 2 (filtered messages)
                      -> Lambda function
```

Use for: Multiple consumers of same event.

### Event Router Pattern (EventBridge Rules)

```
Event source -> Custom Event Bus -> Rule (condition) -> SQS
                                 -> Rule (condition) -> Lambda
                                 -> Rule (condition) -> SNS
```

Use for: Complex event routing based on content.

### Work Queue Pattern (SQS + Consumer)

```
Producer -> SQS queue -> Consumer 1 (processes)
                      -> Consumer 2 (processes)
                      -> Consumer 3 (processes)
```

Use for: Batch processing, background jobs, decoupled workers.

### Real-Time Analytics Pattern (Kinesis → Firehose → S3 → Analytics)

```
Data source -> Kinesis stream -> Firehose -> S3 (data lake)
                                          -> Redshift (warehouse)
```

Use for: Clickstreams, logs, sensors, high-frequency data.

---

## Best Practices

1. **Visibility Timeout:** Set longer than expected processing time + retry buffer (2-3x typical).
2. **DLQ Always:** Every queue should have a DLQ with longer retention.
3. **Idempotent Consumers:** Design consumers to safely process messages multiple times.
4. **Message Deduplication:** Use FIFO queues when exactly-once processing is critical.
5. **Filter at SNS:** Use SNS filter policies to reduce SQS message volume.
6. **EventBridge for Complex Logic:** Use EventBridge rules instead of SNS for content-based routing.
7. **Kinesis Partition Keys:** Choose keys that distribute evenly (customer ID, session ID, not timestamp).
8. **Firehose Buffering:** Longer buffer intervals = lower S3 cost but higher latency.
9. **Dead-Letter Queues:** Always redrive and investigate DLQ messages.
10. **Tagging and Monitoring:** Tag all resources for cost allocation; set CloudWatch alarms.

---

## Summary

| Service | Pattern | Throughput | Ordering | Exactly-Once | Use Case |
|---|---|---|---:|---|---|
| SQS Standard | Queue | Very high | Best-effort | No | General work queue |
| SQS FIFO | Queue | Lower | Guaranteed | Yes | Order-critical |
| SNS Standard | Pub/Sub | Very high | None | No | Broadcast, notifications |
| SNS FIFO | Pub/Sub | Lower | Yes | Yes | Order-critical fan-out |
| EventBridge | Event Router | Very high | None | No | Event-driven workflows |
| Kinesis | Stream | Configurable | Per-shard | No | Real-time analytics |
| Firehose | Delivery | Buffered | Best-effort | No | Data pipeline to S3 |
| MQ | Message Broker | High | Yes (broker) | Yes | Legacy RabbitMQ/ActiveMQ |
| MSK | Kafka | Very high | Per-partition | Yes | Kafka ecosystem |

---

## References

- [AWS SQS Developer Guide](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html)
- [AWS SNS Developer Guide](https://docs.aws.amazon.com/sns/latest/dg/welcome.html)
- [AWS EventBridge User Guide](https://docs.aws.amazon.com/eventbridge/latest/userguide/what-is-eventbridge.html)
- [Amazon Kinesis Developer Guide](https://docs.aws.amazon.com/streams/latest/dev/introduction.html)
- [AWS Glue Data Catalog with Kinesis](https://docs.aws.amazon.com/firehose/latest/dev/what-is-this-service.html)

