# Day 17 - Messaging and Streaming Practical

**AWS account:** `051495879003`  
**Region:** `ap-south-1` (Mumbai)  
**Live class:** Sunday, 30 August 2026, 8:00 PM IST  
**Project tag:** `Project = CloudAdhar-AWS-Zero-To-Hero`

This practical uses the AWS Management Console wherever possible. AWS CloudShell is used only to produce test records for Kinesis Data Streams and inspect the S3 result.

---

## 1. What We Will Build

```text
SQS Standard queue -> visibility timeout -> DLQ -> redrive
SQS FIFO queue -> message group -> deduplication

SNS topic
  +-> Standard orders queue: receives every message
  +-> Priority orders queue: receives only priority=HIGH

Custom application event
  -> EventBridge custom bus
  -> amount > 5000 rule
  -> Priority SQS queue

One-time schedule
  -> EventBridge Scheduler
  -> Payment reminder in SQS

Clickstream producer
  -> Kinesis Data Streams
  -> Amazon Data Firehose
  -> Private S3 bucket
```

Amazon MQ and Amazon MSK are selection walkthroughs only. Do not create a broker or cluster for this class.

---

## 2. Resource Names

| Resource | Name |
|---|---|
| SQS dead-letter queue | `cloudadhar-orders-dlq-day17` |
| SQS Standard queue | `cloudadhar-orders-standard-day17` |
| SQS FIFO queue | `cloudadhar-orders-fifo-day17.fifo` |
| SQS priority queue | `cloudadhar-priority-orders-day17` |
| SNS topic | `cloudadhar-orders-topic-day17` |
| EventBridge custom bus | `cloudadhar-orders-bus-day17` |
| EventBridge rule | `cloudadhar-high-value-orders-rule-day17` |
| Scheduler schedule | `cloudadhar-payment-reminder-day17` |
| Kinesis data stream | `cloudadhar-clickstream-day17` |
| Firehose stream | `cloudadhar-clickstream-firehose-day17` |
| S3 bucket | `cloudadhar-day17-streaming-051495879003-ap-south-1-an` |

S3 bucket names are globally unique. If the proposed name is unavailable, use:

```text
cloudadhar-day17-streaming-051495879003-ap-south-1-live
```

---

# Part A - Amazon SQS

## 3. Create the Dead-Letter Queue

Open:

```text
Amazon SQS -> Queues -> Create queue
```

Configure:

```text
Type: Standard
Name: cloudadhar-orders-dlq-day17
Visibility timeout: 30 seconds
Message retention: 14 days
Delivery delay: 0 seconds
Maximum message size: 1024 KiB
Receive message wait time: 20 seconds
Server-side encryption: Enabled
Encryption key: Amazon SQS key (SSE-SQS)
```

Keep the default owner-only access policy. Add the project tag and create the queue.

Why retain DLQ messages for 14 days? Failed messages should remain available long enough to investigate even if the source queue has a shorter retention period.

---

## 4. Create the Standard Orders Queue

Create another queue:

```text
Type: Standard
Name: cloudadhar-orders-standard-day17
Visibility timeout: 30 seconds
Message retention: 4 days
Delivery delay: 0 seconds
Maximum message size: 1024 KiB
Receive message wait time: 20 seconds
Server-side encryption: SSE-SQS
```

For the first creation, leave **Dead-letter queue** disabled. Add the project tag and create the queue.

Now open the new queue and choose **Edit**. Under **Dead-letter queue**, enable:

```text
cloudadhar-orders-dlq-day17
Maximum receives: 3
```

Save the changes.

The DLQ's separate **Redrive allow policy** can remain unset for this same-account demonstration. The source queue's dead-letter queue configuration is the setting that controls when failed messages move to the DLQ.

---

## 5. Test Visibility Timeout and DLQ

Open:

```text
cloudadhar-orders-standard-day17 -> Send and receive messages
```

Send:

```json
{
  "eventId": "EVT-SQS-1001",
  "orderId": "O-1001",
  "status": "PROCESSING_FAILED"
}
```

Poll for messages but do not delete the message.

Observe:

- the message becomes **in flight**;
- it is hidden during the visibility timeout;
- it becomes visible again if it is not deleted;
- each new receive increases the receive count;
- after the configured maximum receive count is exceeded, SQS moves it to the DLQ.

Poll the source queue, let the 30-second visibility timeout expire, and poll again. Repeat without deleting the message. In the console, the message may remain displayed even when **Messages available** becomes zero; that displayed row is the copy received during the last poll.

After the receive count exceeds `3`, wait briefly and open:

```text
cloudadhar-orders-dlq-day17 -> Send and receive messages
```

The failed message should be present.

### Redrive the message

From the DLQ, choose:

```text
Start DLQ redrive -> Redrive to source queue(s)
```

Confirm the redrive. Verify that the task completes successfully and the message returns to the Standard source queue.

The successful practice result was:

```text
Percent processed: 100%
Status: Successfully completed
Redrive destination: Source queue(s)
```

### Important explanation

```text
Receive -> temporarily invisible -> process -> delete
```

If the consumer succeeds, it deletes the message. If it fails or its receipt handle expires, the message can become visible again. Consumers must be idempotent.

---

## 6. Demonstrate Long Polling

The Standard queue already has:

```text
Receive message wait time: 20 seconds
```

Open **Send and receive messages**, choose **Edit poll settings**, and explain:

- short polling returns immediately and may return empty responses;
- long polling waits for a message or until the wait time expires;
- long polling reduces empty receives and unnecessary API calls.

The console polling duration is not the same as the queue's receive-message wait time. The queue attribute controls each `ReceiveMessage` request.

---

## 7. Create and Test the FIFO Queue

Create:

```text
Type: FIFO
Name: cloudadhar-orders-fifo-day17.fifo
Visibility timeout: 120 seconds
Message retention: 4 days
Content-based deduplication: Disabled
Server-side encryption: SSE-SQS
```

Send the first message:

```text
Message body: Payment received
Message group ID: order-O-2001
Message deduplication ID: payment-O-2001-v1
```

Send the second message:

```text
Message body: Order shipped
Message group ID: order-O-2001
Message deduplication ID: shipping-O-2001-v1
```

### Validate FIFO ordering clearly

1. Choose **Edit poll settings** and set **Maximum message count** to `1`.
2. Poll once. The first message should be `Payment received`.
3. Do not delete it yet. It remains in flight for the visibility timeout.
4. Poll again. `Order shipped` from the same message group should not be released while the first message is still in flight.
5. Poll again after the first message becomes visible, select its newly received copy and delete it immediately.
6. Poll once more. The second message should now be `Order shipped`.
7. Delete the second message using its current receipt handle.

This validates ordering inside `order-O-2001`.

If deletion fails with `receipt handle has expired`, the console is holding an old receipt handle. Poll again, select the newly received copy and delete it before the visibility timeout expires.

Explain that FIFO ordering is scoped to a message group. Several groups enable safe parallelism; one global group can become a bottleneck.

---

## 8. Create the Priority Queue

Create:

```text
Type: Standard
Name: cloudadhar-priority-orders-day17
Visibility timeout: 30 seconds
Message retention: 4 days
Receive message wait time: 20 seconds
Server-side encryption: SSE-SQS
```

Add the project tag and create the queue.

Before every major test, delete existing messages or use **Actions -> Purge** so the expected result is clear.

---

# Part B - Amazon SNS

## 9. Create the SNS Topic

Open:

```text
Amazon SNS -> Topics -> Create topic
```

Configure:

```text
Type: Standard
Name: cloudadhar-orders-topic-day17
```

Add the project tag and create the topic.

---

## 10. Create Two SQS Subscriptions

Create the first subscription:

```text
Protocol: Amazon SQS
Endpoint: ARN of cloudadhar-orders-standard-day17
Raw message delivery: Disabled
Filter policy: None
```

Create the second subscription:

```text
Protocol: Amazon SQS
Endpoint: ARN of cloudadhar-priority-orders-day17
Raw message delivery: Disabled
```

Both subscriptions should show `Confirmed`.

The console normally updates the SQS access policy so the selected SNS topic can call `sqs:SendMessage`. If delivery fails, verify the queue policy uses the exact topic ARN as its source condition.

---

## 11. Add the HIGH-Priority Filter

Open the subscription whose endpoint is:

```text
cloudadhar-priority-orders-day17
```

Choose **Edit**. Under **Subscription filter policy**:

```text
Filter policy scope: Message attributes
```

Enter:

```json
{
  "priority": ["HIGH"]
}
```

Save the changes. Leave the Standard queue subscription unfiltered.

---

## 12. Test SNS Fanout and Filtering

### Test 1 - NORMAL order

Open the SNS topic and choose **Publish message**.

Message body:

```json
{
  "source": "SNS",
  "orderId": "O-3001",
  "amount": 2499,
  "priority": "NORMAL"
}
```

Add a message attribute:

```text
Type: String
Name: priority
Value: NORMAL
```

Expected result:

| Queue | Messages |
|---|---:|
| Standard orders queue | 1 |
| Priority orders queue | 0 |

### Test 2 - HIGH order

Publish:

```json
{
  "source": "SNS",
  "orderId": "O-3002",
  "amount": 7500,
  "priority": "HIGH"
}
```

Message attribute:

```text
Type: String
Name: priority
Value: HIGH
```

Expected result:

| Queue | Messages |
|---|---:|
| Standard orders queue | 1 |
| Priority orders queue | 1 |

With raw delivery disabled, SNS wraps the application message in an SNS notification envelope and includes `MessageAttributes`. That is expected.

---

# Part C - Amazon EventBridge

## 13. Create the Custom Event Bus

Open:

```text
Amazon EventBridge -> Event buses -> Create event bus
```

Configure:

```text
Name: cloudadhar-orders-bus-day17
Description: Custom order events for Day 17
Encryption: AWS owned key
Logs: Disabled
Archive: Disabled
Schema discovery: Disabled
```

Add the project tag and create the bus.

---

## 14. Create the High-Value Order Rule

Open:

```text
EventBridge -> Rules -> Create rule -> Advanced builder
```

Configure:

```text
Rule name: cloudadhar-high-value-orders-rule-day17
Event bus: cloudadhar-orders-bus-day17
Activation: Active
Rule type: Rule with an event pattern
Event source: Other
Creation method: Custom pattern (JSON editor)
```

Event pattern:

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

Use this optional sample event to test the pattern:

```json
{
  "version": "0",
  "id": "e00c66cb-fe7a-4fcc-81ad-58eb60f5d96b",
  "detail-type": "OrderCreated",
  "source": "cloudadhar.orders",
  "account": "051495879003",
  "time": "2026-08-30T15:00:00Z",
  "region": "ap-south-1",
  "resources": [],
  "detail": {
    "eventId": "EVT-EB-4002",
    "orderId": "O-4002",
    "amount": 7500,
    "priority": "HIGH"
  }
}
```

`7500` should match. Change the sample amount to `2500`; it should not match.

### Target

Configure:

```text
Target type: AWS service
Target: SQS queue
Target location: This account
Queue: cloudadhar-priority-orders-day17
Message group ID: Blank
Permissions: Create default execution role
Target input: Matched event
Retry policy: Default
Target DLQ: None for this short demonstration
```

Add the project tag and create the rule.

On the Rules page, select `cloudadhar-orders-bus-day17`; the default bus view will not display this custom-bus rule.

---

## 15. Send Real EventBridge Events

Purge the priority queue. Open:

```text
EventBridge -> Event buses -> Send events
```

### Negative test

```text
Event bus: cloudadhar-orders-bus-day17
Event source: cloudadhar.orders
Detail type: OrderCreated
```

Event detail:

```json
{
  "eventId": "EVT-EB-4001",
  "orderId": "O-4001",
  "amount": 2500,
  "priority": "NORMAL"
}
```

Expected: zero messages in the priority queue.

### Positive test

```json
{
  "eventId": "EVT-EB-4002",
  "orderId": "O-4002",
  "amount": 7500,
  "priority": "HIGH"
}
```

Expected: one message containing the complete EventBridge envelope and the matching `detail` object.

`Event(s) sent successfully` means the event bus accepted the event. The SQS result proves whether the rule matched and delivered it.

---

# Part D - EventBridge Scheduler

## 16. Create a One-Time Payment Reminder

Open:

```text
EventBridge -> Scheduler -> Schedules -> Create schedule
```

Configure:

```text
Name: cloudadhar-payment-reminder-day17
Description: Send a payment reminder to SQS
Schedule group: default
Occurrence: One-time
Date and time: 5-10 minutes in the future
Time zone: Asia/Calcutta or Asia/Kolkata
Flexible time window: Off
```

Target:

```text
Templated target: Amazon SQS SendMessage
Queue: cloudadhar-priority-orders-day17
```

Payload:

```json
{
  "source": "EventBridge Scheduler",
  "type": "PaymentReminder",
  "orderId": "O-5001",
  "message": "Payment is pending"
}
```

Settings:

```text
Schedule state: Enabled
Action after completion: DELETE
Maximum event age: 1 hour
Maximum retries: 3
Scheduler DLQ: None
Encryption: AWS managed/default key
Execution role: Create a new role for this schedule
```

At the selected time, poll the priority queue. The received body should match the supplied payload. The one-time schedule should disappear automatically after completion.

The Scheduler DLQ would capture a failure to invoke the target. The SQS source-queue DLQ demonstrated earlier captures repeated consumer-processing failures. They solve different problems.

---

# Part E - Kinesis Data Streams and Data Firehose

## 17. Create the Kinesis Data Stream

Open:

```text
Amazon Kinesis -> Data streams -> Create data stream
```

Configure:

```text
Name: cloudadhar-clickstream-day17
Capacity mode: On-demand
Warm throughput: Disabled
Maximum record size: 1024 KiB
Retention: 1 day
Enhanced monitoring: Disabled
```

Add the project tag and create the stream. Wait until it becomes `Active`.

---

## 18. Produce and View Kinesis Records

Open AWS CloudShell in `ap-south-1`.

```bash
aws kinesis put-record \
  --stream-name cloudadhar-clickstream-day17 \
  --partition-key customer-C101 \
  --data '{"event":"PRODUCT_VIEWED","customerId":"C101","productId":"P100"}' \
  --cli-binary-format raw-in-base64-out \
  --region ap-south-1
```

```bash
aws kinesis put-record \
  --stream-name cloudadhar-clickstream-day17 \
  --partition-key customer-C101 \
  --data '{"event":"ADD_TO_CART","customerId":"C101","productId":"P100"}' \
  --cli-binary-format raw-in-base64-out \
  --region ap-south-1
```

Open:

```text
Kinesis stream -> Data viewer -> choose the returned shard -> Trim horizon -> Get records
```

Both records should be on the same shard because they use the same partition key. They have increasing sequence numbers. Ordering is guaranteed within a shard, not across an entire multi-shard stream.

---

## 19. Create the S3 Destination Bucket

Create:

```text
Bucket: cloudadhar-day17-streaming-051495879003-ap-south-1-an
Region: ap-south-1
Object Ownership: ACLs disabled
Block all public access: Enabled
Versioning: Disabled for this disposable practice
Default encryption: SSE-S3
```

Add the project tag.

---

## 20. Create the Firehose Stream

From the Kinesis stream, choose **Process with Firehose stream**, or open Data Firehose and create a stream.

Configure:

```text
Source: Amazon Kinesis Data Streams
Source stream: cloudadhar-clickstream-day17
Destination: Amazon S3
Firehose name: cloudadhar-clickstream-firehose-day17
S3 bucket: cloudadhar-day17-streaming-051495879003-ap-south-1-an
Data transformation: Disabled
Record format conversion: Disabled
Decompression: Disabled
New-line delimiter: Disabled
Dynamic partitioning: Disabled
Compression: Uncompressed for easy inspection
Buffer size: 5 MiB
Buffer interval: 300 seconds
Error logging: Enabled
IAM role: Let the console create a service role
```

Leave the S3 prefix blank. Firehose will create a UTC path similar to `YYYY/MM/dd/HH`. For example, a record delivered at 10:10 PM IST can appear under the UTC hour folder `16`.

Add the project tag and create the stream.

If creation initially fails because Firehose cannot assume the newly created IAM role, wait 1-2 minutes and retry using the same role. Do not create multiple roles and do not attach AdministratorAccess.

Wait until Firehose becomes `Active` before sending test records.

---

## 21. Test Kinesis to Firehose to S3

Send new records after Firehose becomes active:

```bash
aws kinesis put-record \
  --stream-name cloudadhar-clickstream-day17 \
  --partition-key customer-C102 \
  --data '{"event":"PRODUCT_VIEWED","customerId":"C102","productId":"P200"}' \
  --cli-binary-format raw-in-base64-out \
  --region ap-south-1
```

```bash
aws kinesis put-record \
  --stream-name cloudadhar-clickstream-day17 \
  --partition-key customer-C102 \
  --data '{"event":"CHECKOUT_STARTED","customerId":"C102","productId":"P200"}' \
  --cli-binary-format raw-in-base64-out \
  --region ap-south-1
```

Because the practice stream used the default `5 MiB / 300 seconds` buffer, wait up to five minutes, then list objects:

```bash
aws s3 ls \
  s3://cloudadhar-day17-streaming-051495879003-ap-south-1-an/ \
  --recursive \
  --human-readable \
  --region ap-south-1
```

The successful live-account test produced objects under a path similar to:

```text
2026/08/30/16/KDS-S3-...-2026-08-30-16-38-00-...
2026/08/30/16/KDS-S3-...-2026-08-30-16-40-11-...
```

Copy an object S3 URI and inspect it in CloudShell:

```bash
aws s3 cp \
  s3://cloudadhar-day17-streaming-051495879003-ap-south-1-an/<object-key> \
  - \
  --region ap-south-1
```

Because **New-line delimiter** was disabled during the practice, the JSON records appear one after another. This is expected:

```text
{"event":"PRODUCT_VIEWED","customerId":"C102","productId":"P200"}{"event":"CHECKOUT_STARTED","customerId":"C102","productId":"P200"}
```

If the bucket is still empty, use **Firehose -> Test with demo data -> Start sending demo data**. Keep the page open while it is running, wait for an S3 object, and then choose **Stop sending demo data**. Demo data proves Firehose-to-S3 delivery, while the two `put-record` commands prove the complete Kinesis-to-Firehose-to-S3 path.

---

# Part F - Amazon MQ and Amazon MSK Selection

## 22. Amazon MQ Walkthrough Only

Open:

```text
Amazon MQ -> Brokers -> Create broker
```

Inspect but do not create:

- RabbitMQ and ActiveMQ engines;
- broker size;
- single-instance and highly available deployment options;
- VPC, subnets and security groups;
- private access;
- users and authentication;
- encryption and maintenance.

Use Amazon MQ when an existing application depends on RabbitMQ or ActiveMQ protocols and broker semantics and migration with fewer code changes is important.

---

## 23. Amazon MSK Walkthrough Only

Open:

```text
Amazon MSK -> Clusters -> Create cluster
```

Inspect but do not create:

- MSK Provisioned and MSK Serverless;
- Kafka versions;
- topics, partitions and consumer groups;
- VPC networking;
- IAM, SASL/SCRAM and TLS authentication;
- encryption and monitoring;
- Multi-AZ architecture.

Use Amazon MSK when applications require Apache Kafka APIs, Kafka clients, consumer groups, offsets, retained topics or Kafka ecosystem compatibility.

---

## 24. Expected Final Result

| Test | Expected result |
|---|---|
| Standard SQS receive without deletion | Message becomes visible again |
| DLQ test | Repeated failure moves message to DLQ |
| DLQ redrive | Message returns to source queue |
| FIFO test | Same-group messages retain order |
| SNS NORMAL | Standard queue only |
| SNS HIGH | Standard and priority queues |
| EventBridge amount 2500 | No priority message |
| EventBridge amount 7500 | One priority message |
| Scheduler | Payment reminder appears at selected time |
| Kinesis | Same partition key reaches same shard |
| Firehose | New Kinesis records appear in an encrypted S3 object |

---

## 25. Cleanup

Delete resources in this order:

1. Stop Firehose demo data if it is running.
2. Delete `cloudadhar-clickstream-firehose-day17`.
3. Delete `cloudadhar-clickstream-day17`.
4. Empty and delete the S3 bucket.
5. Delete the EventBridge rule.
6. Delete the custom event bus.
7. Confirm the one-time schedule was automatically deleted.
8. Delete the SNS subscriptions and topic.
9. Purge and delete all four SQS queues.
10. Delete generated execution roles only after confirming no remaining resource uses them.
11. Confirm no Amazon MQ broker or Amazon MSK cluster was created.

---

## 26. Official AWS References

- [Amazon SQS Developer Guide](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html)
- [SQS visibility timeout](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html)
- [SQS dead-letter queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html)
- [SQS long polling](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-short-and-long-polling.html)
- [SNS subscription filtering](https://docs.aws.amazon.com/sns/latest/dg/sns-message-filtering.html)
- [EventBridge event buses](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-event-bus.html)
- [EventBridge event patterns](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-event-patterns.html)
- [EventBridge Scheduler](https://docs.aws.amazon.com/scheduler/latest/UserGuide/what-is-scheduler.html)
- [Kinesis Data Streams](https://docs.aws.amazon.com/streams/latest/dev/introduction.html)
- [Amazon Data Firehose](https://docs.aws.amazon.com/firehose/latest/dev/what-is-this-service.html)
- [Firehose with a Kinesis source](https://docs.aws.amazon.com/firehose/latest/dev/writing-with-kinesis-streams.html)
- [Amazon MQ](https://docs.aws.amazon.com/amazon-mq/latest/developer-guide/welcome.html)
- [Amazon MSK](https://docs.aws.amazon.com/msk/latest/developerguide/what-is-msk.html)
