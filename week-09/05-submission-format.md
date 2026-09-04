# Week 9 Submission Format

Document your Day 17 Messaging and Streaming practical implementation, test results,
architecture decisions, and cleanup verification.

```text
week-09/submissions/<github-username>/
├── README.md
├── architecture.png
└── evidence/
    ├── sqs-standard-visibility-dlq/
    ├── sqs-fifo-ordering/
    ├── sns-fanout-filtering/
    ├── eventbridge-routing/
    ├── scheduler-reminder/
    ├── kinesis-firehose-s3/
    └── cleanup/
```

## README Template

```markdown
# Week 9 - Messaging, Streaming, and Event-Driven Architecture

## Learner
- Name:
- GitHub:
- LinkedIn:
- Region: ap-south-1 (Mumbai)

## Day 17 - Amazon SQS

### Standard Queue and DLQ
- Dead-letter queue creation and configuration:
- Standard queue creation and DLQ attachment:
- Visibility timeout test result (message in flight, becomes visible, receive count increases):
- DLQ population after exceeding max receives:
- DLQ redrive result (message returned to source):
- Long polling configuration and benefits:

### FIFO Queue
- FIFO queue creation with deduplication ID:
- Message group ordering validation (message 1 and message 2 in order):
- Receipt handle and delete operation (same group, different messages):
- FIFO versus Standard trade-offs:

## Day 17 - Amazon SNS

### Topic and Subscriptions
- SNS Standard topic creation:
- Two SQS subscriptions (standard and priority queues):
- Subscription confirmation status:

### Message Filtering
- Filter policy added to priority queue subscription:
- Filter policy JSON (priority = HIGH):
- Test 1 result (NORMAL order: standard queue 1, priority queue 0):
- Test 2 result (HIGH order: standard queue 1, priority queue 1):
- SNS envelope structure explanation:

## Day 17 - Amazon EventBridge

### Custom Event Bus
- Custom event bus `cloudadhar-orders-bus-day17` created:
- Event bus configuration (encryption, logging, archiving):

### High-Value Orders Rule
- Event pattern with numeric condition (amount > 5000):
- Rule target: SQS priority queue:
- Sample event test (7500 matches, 2500 does not):

### Event Testing
- Negative test: amount 2500 (priority queue 0):
- Positive test: amount 7500 (priority queue 1):
- Event bus acceptance confirmation:

## Day 17 - EventBridge Scheduler

### One-Time Payment Reminder
- Schedule name and date/time (5-10 minutes in future):
- Target: SQS SendMessage to priority queue:
- Payload:
- Execution result (message arrived at scheduled time):
- Schedule status after completion (automatically deleted):
- Difference between Scheduler DLQ and SQS DLQ:

## Day 17 - Kinesis and Firehose

### Kinesis Data Stream
- Stream name `cloudadhar-clickstream-day17`:
- Capacity mode: On-demand:
- Record production (put-record with partition key `customer-C101`):
- Data viewer result (both records on same shard, increasing sequence numbers):
- Partition key distribution explanation:

### Firehose Delivery Stream
- Source: Kinesis data stream:
- Destination: S3 bucket:
- Buffer size: 5 MiB:
- Buffer interval: 300 seconds:
- Compression: Uncompressed:

### S3 Delivery Validation
- S3 bucket creation and encryption (SSE-S3):
- CloudShell `put-record` commands with new partition key:
- S3 object listing after buffer interval:
- S3 object path structure (YYYY/MM/dd/HH):
- Object content inspection (JSON records):
- UTC versus IST time explanation:

## Day 17 - Service Selection

### Amazon MQ Walkthrough
- Engines inspected (RabbitMQ, ActiveMQ):
- Configuration options reviewed:
- Use case: When existing application depends on RabbitMQ or ActiveMQ:

### Amazon MSK Walkthrough
- Provisioned and Serverless options inspected:
- Kafka versions and topics reviewed:
- Use case: When applications require Kafka consumer groups and offsets:

## Architecture Decision
Write 250-400 words covering:

- **SQS versus SNS:** When to choose queue versus topic pub/sub.
- **Visibility timeout:** Why it must be longer than processing time; recovery after failure.
- **FIFO ordering:** Trade-off between ordering guarantee and throughput (300 vs 1000s per second).
- **Dead-letter queues:** Why retention is 14 days for DLQ versus 4 days for source.
- **SNS filter policies:** How to reduce message volume versus routing all to queue.
- **EventBridge patterns:** Content-based routing advantage over SNS attribute filtering.
- **Scheduler versus Cron:** Replacement of cron jobs and automatic cleanup of one-time schedules.
- **Kinesis partitioning:** Why customer ID as partition key distributes records across shards.
- **Firehose buffering:** Trade-off between 5 MiB / 300 seconds and real-time ingestion.
- **Idempotent consumers:** How to handle duplicate messages safely.
- **Cost estimation:** SQS API calls, SNS deliveries, EventBridge invocations, Kinesis shards, Firehose GB, S3 storage.

## Cleanup Verification
- Firehose stream deleted:
- Kinesis stream deleted:
- S3 bucket emptied and deleted:
- EventBridge rule deleted:
- Custom event bus deleted:
- Scheduler schedule automatically removed:
- SNS topic and subscriptions deleted:
- All four SQS queues purged and deleted:
- Execution roles cleaned up:
- CloudShell verification commands run:
- All resources confirmed gone from console:

## Reflection
1. Why must SQS visibility timeout be longer than the expected processing time?
2. What is the difference between SQS Standard queue and SQS FIFO queue?
3. When would you use SNS filter policy versus EventBridge pattern matching?
4. How does EventBridge Scheduler automatically delete one-time schedules?
5. Why is the partition key important for Kinesis record distribution?
6. How does Firehose buffering affect S3 delivery latency and cost?
7. What makes a consumer idempotent, and why is it critical?
8. How would you monitor queue depth, message age, and DLQ messages in CloudWatch?
9. What is the difference between SQS DLQ and EventBridge Scheduler DLQ?
10. How would you scale this architecture to handle millions of orders per day?

## Troubleshooting Lessons
Document any issues you encountered:
- Problem:
- Root cause:
- Resolution:
- Prevention for next time:
```

## Submission Evidence Checklist

### SQS Standard Queue
- [ ] Queue created with 30-second visibility timeout
- [ ] DLQ configured with max receives = 3
- [ ] Message sent to queue
- [ ] Message "in flight" while invisible
- [ ] Message visible again after timeout expired
- [ ] Receive count increased after repeated polls
- [ ] Message moved to DLQ after exceeding max receives
- [ ] DLQ redrive successful (message returned to source)

### SQS FIFO Queue
- [ ] FIFO queue created with `.fifo` suffix
- [ ] Two messages sent with same message group ID
- [ ] Poll result shows correct order (message 1, then message 2)
- [ ] Message remains in flight if not deleted
- [ ] FIFO ordering preserved within message group
- [ ] Explanation of message group vs ordering

### SNS and SQS Integration
- [ ] SNS topic created
- [ ] Two SQS subscriptions confirmed
- [ ] Standard queue receives all messages
- [ ] Priority queue has HIGH filter policy
- [ ] Test 1 (NORMAL): Standard queue 1 message, Priority queue 0 messages
- [ ] Test 2 (HIGH): Standard queue 1 message, Priority queue 1 message
- [ ] Filter policy JSON shown

### EventBridge
- [ ] Custom event bus created
- [ ] Rule with numeric pattern (amount > 5000) created
- [ ] Sample event test: 7500 matches (rule fires)
- [ ] Sample event test: 2500 does not match (rule doesn't fire)
- [ ] Negative test: EventBridge event amount 2500 (priority queue 0)
- [ ] Positive test: EventBridge event amount 7500 (priority queue 1)
- [ ] Event bus acceptance confirmed

### EventBridge Scheduler
- [ ] One-time schedule created (5-10 minutes future)
- [ ] Target: SQS SendMessage configured
- [ ] Payload correct format
- [ ] Schedule state: Enabled
- [ ] At scheduled time: Message received in priority queue
- [ ] Schedule automatically deleted after execution
- [ ] Difference between Scheduler DLQ and SQS DLQ explained

### Kinesis and Firehose
- [ ] Kinesis stream on-demand mode
- [ ] put-record command executed with partition key
- [ ] Data viewer shows records on same shard (same partition key)
- [ ] Sequence numbers increasing
- [ ] S3 bucket created with SSE-S3 encryption
- [ ] Firehose stream created (Kinesis source, S3 destination)
- [ ] Firehose active before test records
- [ ] New put-record commands with different partition key
- [ ] S3 objects appear after buffer interval expires
- [ ] S3 path structure: `YYYY/MM/dd/HH/KDS-S3-...-YYYY-MM-dd-HH-mm-ss-UUID`
- [ ] CloudShell `aws s3 cp` shows JSON records
- [ ] Records uncompressed and readable

### Cleanup
- [ ] Firehose demo data stopped
- [ ] Firehose delivery stream deleted
- [ ] Kinesis data stream deleted
- [ ] S3 bucket emptied and deleted
- [ ] EventBridge rule deleted
- [ ] Custom event bus deleted
- [ ] Scheduler schedule gone (auto-deleted or manually removed)
- [ ] SNS subscriptions deleted
- [ ] SNS topic deleted
- [ ] All four SQS queues purged and deleted
- [ ] Execution roles cleaned up
- [ ] CloudShell verification shows no day-17 resources

### Learning
- [ ] Architecture diagram included (SQS, SNS, EventBridge, Kinesis, Firehose, S3)
- [ ] Decision reasoning documented (why SQS vs SNS vs EventBridge)
- [ ] DLQ and failure recovery explained
- [ ] FIFO ordering and deduplication explained
- [ ] Idempotent consumer pattern explained
- [ ] Partition key strategy explained
- [ ] Firehose buffering trade-offs documented
- [ ] Troubleshooting lesson recorded

## Submission Quality Tips

- **Sanitize evidence:** Hide AWS account IDs, endpoint URLs, and resource ARNs.
- **Annotate screenshots:** Add arrows and callouts to highlight key findings.
- **Show timestamps:** Capture test results with date/time to prove execution.
- **Explain failures:** Document what didn't work and why you adjusted.
- **Link AWS docs:** Reference official docs for concepts you learned.
- **Be concise:** Use bullet points and tables; avoid lengthy narratives.
- **Use consistent naming:** Keep resource names as specified in the practical.
- **Capture console state:** Screenshot queue metrics, stream details, and rule configurations.
- **Document costs:** Estimate the cost of this architecture if run for a full day.

