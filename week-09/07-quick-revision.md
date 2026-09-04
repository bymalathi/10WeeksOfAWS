# Week 9 Quick Revision

## Recall

1. Messaging decouples producers from consumers; they don't run at the same time.
2. SQS Standard queue offers unlimited throughput; FIFO queue guarantees ordering within a message group.
3. Visibility timeout hides a message while a consumer processes it; if processing fails or times out, the message becomes visible again.
4. Consumers must be idempotent: processing the same message multiple times must produce the same result.
5. Dead-letter queues preserve messages that fail after maximum receive attempts.
6. DLQ retention should be longer than source queue retention (14 days vs 4 days).
7. Long polling waits for a message instead of returning immediately with empty; reduces API costs.
8. SNS is pub/sub (1-to-many); SQS is point-to-point (1-to-1 or 1-to-N workers).
9. SNS filter policies reduce subscription volume by message attributes; filter matching is AND for multiple attributes.
10. EventBridge patterns support numeric, string, and complex conditions; routing is content-based, not just attribute-based.
11. EventBridge Scheduler replaces cron jobs; one-time schedules auto-delete after execution.
12. Kinesis partition keys determine shard assignment; same key → same shard → guaranteed order; different keys → different shards → parallelism.
13. Kinesis ordering is per-shard, not stream-wide; multiple shards process in parallel.
14. Firehose buffers data until size or interval is reached, then delivers; lower throughput but cheaper and durable.
15. Firehose S3 path uses UTC time, not local time; a record at 10:10 PM IST (UTC 16:40) appears under the 16 folder.
16. Deduplication ID in SQS FIFO prevents duplicate messages within a 5-minute interval.
17. Message group ID in SQS FIFO ensures ordering; messages without a group ID use the default group.
18. SNS subscription filter policies and EventBridge rules are different; EventBridge is more flexible.
19. RawMessageDelivery disabled wraps SNS messages in an SNS envelope; enabled sends just the message body.
20. EventBridge Scheduler DLQ captures scheduler failures; SQS DLQ captures message processing failures.

## Decision Table

| Requirement | Best Service | Why |
|---|---|---|
| Multiple subscribers to same event | SNS topic | Fan-out to many subscribers |
| Worker queue for background jobs | SQS Standard | Unlimited throughput, good for tasks |
| Strict message order within an order | SQS FIFO | Ordered delivery within message group |
| Preserve failed messages | SQS DLQ | Investigate failures after max attempts |
| Route by event content | EventBridge | Numeric, string, and complex patterns |
| Broadcast a notification | SNS Standard topic | One-to-many push |
| Send at specific time | EventBridge Scheduler | One-time or recurring scheduling |
| High-throughput events | Kinesis | Millions per second with partitioning |
| Batch to S3 for analytics | Firehose | Buffer and deliver, automatic retry |
| Existing RabbitMQ app | Amazon MQ | Drop-in replacement, managed broker |
| Kafka consumer groups | Amazon MSK | Offset tracking, rebalancing, topics |

## Important Traps

- Visibility timeout too short leads to duplicate processing; if consumer needs 60 seconds, set timeout > 60 seconds.
- Visibility timeout not related to delivery delay; delivery delay is before message appears, timeout is after receive.
- SQS FIFO throughput is 300/sec without batch, 3000/sec with batch; use Standard if speed is critical over order.
- FIFO ordering is within message group; multiple groups run in parallel. Single global group becomes bottleneck.
- SNS and SQS filters use different syntax: SNS uses `MessageAttributes`, EventBridge uses `detail` and dot notation.
- EventBridge Scheduler one-time schedules auto-delete; don't expect them to remain for auditing.
- Kinesis partition key is not the same as SQS message group ID; poor key choice creates hot shards.
- Firehose delivery is not real-time; buffering introduces latency (seconds to minutes).
- S3 path timestamps are UTC, not local; 10:10 PM IST is 16:40 UTC = hour folder 16.
- Long polling is queue attribute (`ReceiveMessageWaitTime`), not console setting; console and queue are different.
- Consumer must delete message within visibility timeout, not after. If visibility expires before delete, message becomes visible.
- DLQ redrive moves messages, but if they fail again, they go back to DLQ. Fix the root cause first.
- EventBridge rule does not queue events; if rule has no target, the event disappears silently.
- SNS subscriptions are not queues; a message published to SNS with no subscribers is lost.
- Firehose source can be Kinesis, not Kinesis as consumer of Firehose. Kinesis → Firehose → S3, not the reverse.

## Week 9 Recall

- **Asynchronous patterns scale.** Synchronous API calls fail when one service is slow.
- **Ordering and throughput trade off.** FIFO is ordered but slow (300/sec); Standard is fast but unordered.
- **Idempotent processing is mandatory.** Duplicate messages happen; design for it.
- **DLQs are audit logs.** They preserve evidence of failed messages for debugging.
- **Events decouple services.** Service A publishes; Services B, C, D subscribe. Service A doesn't know about them.
- **Partition keys matter.** Bad key = hot shard = throttling even with on-demand mode.
- **Visibility timeout + DLQ = reliability.** Together they enable safe async processing and failure recovery.
- **Filtering happens before delivery.** SNS filter policies and EventBridge patterns reduce unnecessary messages.
- **Firehose buffers for cost.** Batching and intervals reduce S3 API calls and lower per-GB costs.
- **Scheduler is not cron.** EventBridge Scheduler deletes completed one-time schedules; cron keeps running.

## Practice Scenario: E-Commerce Order System

Design a system where:
- Order API receives thousands of orders per second.
- Payment must happen before shipping (order, not concurrent).
- High-value orders (> $5000) get priority processing.
- Clickstream events (product views, searches) flow to analytics database.

**Solution:**
1. **API → SNS Topic:** Order API publishes to SNS (fan-out).
2. **SNS → SQS Standard Queue:** All orders processed by workers.
3. **SNS → SQS FIFO Queue:** Order-specific FIFO with message group ID = order ID (payment must complete before shipment).
4. **EventBridge Rule:** Custom rule matches orders > $5000, routes to priority SQS FIFO queue.
5. **EventBridge Scheduler:** Reminder for unpaid orders at 24-hour mark.
6. **Kinesis Stream:** Clickstream events with partition key = customer ID.
7. **Firehose → S3:** Deliver clickstream to data lake every 5 minutes.

**Why:**
- SNS fan-out allows multiple processing paths without replicating the order.
- Standard SQS for workers to scale independently.
- FIFO for payment → shipping order guarantee.
- EventBridge rule routes high-value orders without modifying API logic.
- Kinesis partitions by customer, preserving order within a customer, parallelizing across customers.
- Firehose batches and delivers, reducing S3 costs.

## Day 17 Practice Questions

> **Disclaimer:** These are original educational questions modeled on the SAA-C03 style. They are not real exam questions or exam dumps.

### Question 1

A company receives 100,000 orders per minute from an e-commerce website. Orders must be processed by multiple worker services in parallel. A failed order should remain in the queue for debugging.

Which combination is most suitable?

A) SQS Standard queue with a DLQ
B) SQS FIFO queue with a DLQ
C) SNS topic with SQS subscriptions
D) EventBridge custom bus with Kinesis

**Answer:** A

**Explanation:** Standard queue supports high throughput (100k/minute). DLQ preserves failed orders. FIFO is not needed because orders are independent. SNS + SQS adds unnecessary complexity. EventBridge is for event routing, not high-volume queuing.

### Question 2

An application needs to ensure that payment messages are processed before shipping messages for the same order. Throughput is 1000 messages/minute.

Which service should be used?

A) SQS Standard queue
B) SQS FIFO queue with message group ID = order ID
C) SNS topic with filter policy
D) EventBridge with numeric pattern

**Answer:** B

**Explanation:** FIFO guarantees order within message group. Message group ID = order ID ensures payment before shipping. Throughput 1000/min is within FIFO limits. Standard queue does not guarantee order. SNS and EventBridge don't provide strict ordering.

### Question 3

A rule in EventBridge should trigger only when an order amount exceeds $5000.

What is the correct event pattern?

A) `{ "amount": { "greaterThan": 5000 } }`
B) `{ "detail": { "amount": [ { "numeric": [">", 5000] } ] } }`
C) `{ "detail.amount": ">5000" }`
D) `{ "amount": [ { "numeric": [ ">=", 5000 ] } ] }`

**Answer:** B

**Explanation:** EventBridge patterns use `detail` for nested fields and `numeric` operator with tuple syntax `[">", 5000]`. Options A, C, D have incorrect syntax.

### Question 4

A Firehose stream buffers 5 MiB or 300 seconds, whichever comes first. Records arrive at 100 KB/minute. How often will data be delivered to S3?

A) Every 5 minutes
B) Every 50 minutes
C) Every 300 seconds (5 minutes)
D) Every 1 minute

**Answer:** A

**Explanation:** At 100 KB/min, 5 MiB is reached in 50 minutes. But the interval (300 seconds = 5 minutes) expires first, triggering delivery every 5 minutes.

### Question 5

A Kinesis stream has 3 shards. Records are sent with partition keys: customer-A, customer-B, customer-C, customer-A, customer-A.

Which guarantee does Kinesis provide?

A) All records are ordered in the stream
B) Records for customer-A are ordered
C) All 5 records are on the same shard
D) Records are delivered to consumers in the order received

**Answer:** B

**Explanation:** Kinesis guarantees order per shard, not per stream. Customer-A records go to the same shard (same partition key) and are ordered. Other customers may go to different shards and can be processed in parallel.

### Question 6

An SNS filter policy is set to `{ "priority": ["HIGH"] }`. A message is published with message attribute `priority = "NORMAL"`.

What happens?

A) Message is delivered but flagged
B) Message is not delivered to subscriptions with this filter
C) Message is queued for later delivery
D) SNS rejects the message

**Answer:** B

**Explanation:** SNS filter policies drop non-matching messages at the subscription level. A NORMAL message does not match the HIGH filter, so subscriptions with this filter don't receive it.

### Question 7

An application processes SQS messages. Consumer code fails. The visibility timeout is 30 seconds. Max receives is 3. What happens to the message?

A) Message is immediately deleted
B) Message is immediately sent to DLQ
C) Message becomes visible after 30 seconds; consumer retries. After 4th receive (> max 3), it moves to DLQ
D) Message stays invisible forever

**Answer:** C

**Explanation:** Visibility timeout hides the message. If not deleted within timeout, it becomes visible again. This repeats. After the receive count exceeds max (3), the message moves to DLQ on the next attempt.

### Question 8

Which is NOT a valid EventBridge Scheduler feature?

A) One-time schedule that auto-deletes after execution
B) Recurring schedule with cron expression
C) Retry policy with maximum retries
D) Guaranteed message ordering across schedules

**Answer:** D

**Explanation:** EventBridge Scheduler provides one-time, recurring, retry, and DLQ features. It does NOT guarantee ordering across schedules (schedules are independent).

### Question 9

A company uses Kinesis to stream clickstream data to Firehose for S3 delivery. Why should partition key be based on customer ID, not timestamp?

A) Timestamps are too large
B) Timestamps don't partition data
C) Customer ID distributes load across shards; timestamp sends all events to one shard
D) Firehose doesn't accept timestamp partition keys

**Answer:** C

**Explanation:** Partition key determines shard assignment. Customer ID distributes across shards (parallelism). Timestamp sends all events to the same shard (hot shard, throttling). Distribution across shards is the goal.

### Question 10

An application needs to retry an EventBridge Scheduler task if it fails. Where is the retry configuration set?

A) On the SQS queue
B) On the EventBridge Scheduler schedule's retry policy
C) On the target Lambda function
D) In the SNS topic

**Answer:** B

**Explanation:** EventBridge Scheduler has its own retry policy. Retries are configured when creating the schedule, not on the target or other services.

## Summary Table: Week 9 Services

| Service | Pattern | Throughput | Order | Use Case |
|---|---|---|---|---|
| SQS Standard | Queue | Unlimited | Best-effort | High-volume tasks |
| SQS FIFO | Queue | 300/sec | Guaranteed/group | Order-critical workflows |
| SNS Standard | Pub/Sub | Unlimited | None | Broadcast notifications |
| EventBridge | Router | Unlimited | None | Event-driven workflows |
| Scheduler | Trigger | N/A | N/A | Scheduled tasks |
| Kinesis | Stream | On-demand/provisioned | Per-shard | Real-time analytics |
| Firehose | Pipeline | Buffered | Best-effort | Data lake delivery |
| MQ | Broker | High | Yes (broker) | RabbitMQ/ActiveMQ |
| MSK | Kafka | Very high | Per-partition | Kafka ecosystem |

