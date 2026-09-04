# Week 9 Learn-in-Public Posts

Write in your own voice and publish only sanitized evidence.

## Day 17

```text
Week 9, Day 17 of #10WeeksOfAWS

Today I built an event-driven order-processing architecture using Amazon SQS,
SNS, EventBridge, EventBridge Scheduler, Kinesis, and Firehose.

My SQS standard queue design:
<Visibility timeout, DLQ configuration, receive-process-delete pattern, and
why consumers must be idempotent>

My SQS FIFO queue validation:
<Message ordering within message group, exact-once deduplication, and throughput
trade-off vs Standard queue>

My SNS fan-out and filtering:
<Topic with two SQS subscriptions, HIGH-priority filter policy test result,
and why SNS wraps the message in an envelope>

My EventBridge routing:
<Custom event bus, numeric pattern for amount > 5000, test results with 2500 and
7500, and how EventBridge differs from SNS>

My scheduling pattern:
<One-time payment reminder schedule, automatic cleanup after execution, and why
EventBridge Scheduler replaced cron jobs>

My real-time streaming pipeline:
<Kinesis partition key strategy by customer, Firehose buffering to S3,
UTC time-based partitioning, and partition key ordering guarantee per shard>

I removed the SQS queues, SNS topic, EventBridge bus and rules, Scheduler
schedule, Kinesis stream, Firehose stream, S3 bucket, and execution roles after
collecting sanitized evidence.

My key learning:
<Why you decouple applications with messaging and events instead of synchronous
API calls>

#AWS #AmazonSQS #AmazonSNS #EventBridge #KinesisDataStreams #EventDriven
#AWSMessaging #CloudAdhar #TrainWithShubham
```

## Alternative Format (Longer Version)

```text
Week 9, Day 17 of #10WeeksOfAWS - Messaging and Streaming

Today I learned why asynchronous messaging outscales synchronous API calls.

I built:
1. A Standard SQS queue with visibility timeout and DLQ for failed messages
2. A FIFO SQS queue that guarantees strict ordering within a message group
3. An SNS topic that fans out to multiple SQS queues with filter policies
4. An EventBridge custom bus that routes high-value orders by amount threshold
5. An EventBridge Scheduler that sends payment reminders at a specific time
6. A Kinesis stream that partitions clickstream events by customer ID
7. A Firehose pipeline that delivers Kinesis records to S3 for analytics

Why this matters:
- SQS decouples producers from consumers. If the consumer crashes, the message waits.
- FIFO ordering guarantees order-critical workflows like payments stay in sequence.
- SNS filter policies reduce SQS message volume. Only HIGH-priority orders reach the priority queue.
- EventBridge patterns allow content-based routing without code changes.
- Kinesis partitioning distributes high-throughput events across shards by customer.
- Firehose buffers and delivers to S3, enabling cheap, durable data lakes.

My test results:
- [Screenshot: SQS message invisible during visibility timeout]
- [Screenshot: Message moved to DLQ after 3 failed receives]
- [Screenshot: DLQ redrive returns message to source]
- [Screenshot: SNS HIGH-priority filter delivers to both queues]
- [Screenshot: EventBridge rule matches amount > 5000 and routes to SQS]
- [Screenshot: Scheduler message arrived at the exact scheduled time]
- [Screenshot: Kinesis records with same partition key on same shard]
- [Screenshot: S3 object with clickstream events in UTC path structure]

Cost lesson: On-demand SQS pays per API call. FIFO charges less per message but throughput
is 10x lower. Use Standard for high volume, FIFO for order-critical workflows only.

I removed all Day 17 resources (SQS queues, SNS topic, EventBridge bus, Kinesis, Firehose,
S3 bucket, and IAM roles) after collecting evidence.

#AWS #EventDriven #Messaging #Streaming #SQS #SNS #EventBridge #Kinesis #CloudArchitecture
#CloudAdhar #TrainWithShubham
```

## Key Talking Points

Choose 3-5 of these to highlight your learning:

1. **Decoupling:** "Messaging lets me build services that don't need to know about each other."
2. **Reliability:** "SQS DLQ preserves failed messages for investigation instead of losing them."
3. **Ordering:** "FIFO queues guarantee message order within a group, essential for payments."
4. **Filtering:** "SNS filter policies let me route by attributes without duplicating messages."
5. **Events:** "EventBridge patterns match on content (amount > 5000) not just message structure."
6. **Scheduling:** "EventBridge Scheduler replaced manual cron jobs and deletes completed schedules."
7. **Streaming:** "Kinesis partitions by customer ID to order events within a customer while parallelizing across customers."
8. **Analytics:** "Firehose delivers clickstream data to S3 for Athena or Redshift analysis."
9. **Scale:** "This architecture handles millions of orders per day without rewriting code."
10. **Cost:** "Pay per message sent, not per server. Scales from 10 to 10 million messages."

## Hashtag Suggestions

- #10WeeksOfAWS #AWS #CloudAdhar #TrainWithShubham
- #AmazonSQS #AmazonSNS #EventBridge #Kinesis #Firehose
- #EventDriven #Asynchronous #Messaging #Streaming #DataPipeline
- #CloudArchitecture #AWSSolutions #AWS-SAA-C03 #AWSCertification
- #CloudNative #Microservices #Decoupling #Scalability
- #AWSCommunity #CloudLearning #DevOps #BackendEngineering

## Post Timing

- Post on **Friday or Monday** for maximum visibility.
- Include a **4-week reflection** at Week 9 (halfway through).
- Tag **#CloudAdhar** and **#TrainWithShubham** for community engagement.
- Reference **specific AWS docs** to show you read official sources.
- Share a **lesson learned** or **mistake you made** for authenticity.

## Image Suggestions

Include at least one screenshot or diagram:

1. **Architecture diagram:** SQS, SNS, EventBridge, Kinesis, Firehose, S3
2. **Queue metrics:** Message count, visibility timeout, retention period
3. **SNS filter policy:** JSON showing `priority: ["HIGH"]`
4. **EventBridge rule:** Numeric pattern for `amount > 5000`
5. **Kinesis shard:** Both records with same partition key on same shard
6. **S3 path structure:** `2026/08/30/16/KDS-S3-...-...`
7. **CloudWatch metrics:** Queue depth over time
8. **Cleanup verification:** CloudShell showing no remaining resources

## Writing Tips

- **Start with a hook:** "I built an order system that handles millions of messages without crashing."
- **Show the problem:** "Synchronous APIs don't scale when loads spike."
- **Explain the solution:** "Messaging queues decouple producers from consumers."
- **Provide evidence:** Include 2-3 screenshots of key results.
- **End with learning:** "This week I learned why decoupling is the foundation of scalable systems."
- **Be authentic:** Share a mistake or challenge you faced.
- **Invite engagement:** "What's your favorite AWS messaging pattern?"

