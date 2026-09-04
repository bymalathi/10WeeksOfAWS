# Week 9 - Messaging, Streaming, and Event-Driven Architecture

AWS Zero To Hero - CloudAdhar x TrainWithShubham<br>
Sessions: Aug 29-30, 2026<br>
Course sessions: Day 17<br>
Exam focus: SAA-C03 Domains 1-4<br>
Main pillars: Integration, Reliability, Performance Efficiency

Week 9 focuses on asynchronous communication, event-driven patterns, and real-time
data streaming. Day 17 covers Amazon SQS (Standard and FIFO), Amazon SNS with
message filtering, AWS EventBridge with custom event buses and rules, EventBridge
Scheduler for one-time and recurring tasks, Amazon Kinesis Data Streams,
Amazon Data Firehose, with selection walkthroughs for Amazon MQ and Amazon MSK.

## Start Here

| Seq | Session | Focus | File |
|---:|---|---|---|
| 01 | Day 17 | Messaging concepts: SQS, SNS, queues, topics, visibility timeout, DLQ | [01-messaging-and-streaming-foundations.md](./01-messaging-and-streaming-foundations.md) |
| 02 | Day 17 | Hands-on practical: Build complete SQS, SNS, EventBridge, Kinesis workflow | [02-messaging-and-streaming-practical.md](./02-messaging-and-streaming-practical.md) |
| 03 | Week 9 | Design an event-driven architecture for your use case | [03-architecture-exercise.md](./03-architecture-exercise.md) |
| 04 | End | Remove Day 17 resources safely | [04-cleanup.md](./04-cleanup.md) |
| 05 | End | Submit Week 9 evidence | [05-submission-format.md](./05-submission-format.md) |
| 06 | Daily | Share learning progress | [06-linkedin-post.md](./06-linkedin-post.md) |
| 07 | Review | Revise Week 9 concepts and practice scenarios | [07-quick-revision.md](./07-quick-revision.md) |

Day 17 downloads:

- [Student guide (PDF)](./AWS_Zero_To_Hero_Day17_Messaging_and_Streaming_Student_Guide.pdf)

## Day 17 Required Outcomes

- Explain SQS Standard vs FIFO queues: ordering guarantees, deduplication, throughput.
- Configure visibility timeout, message retention, delivery delay, and receive wait time.
- Implement and test dead-letter queues (DLQ) with redrive policies.
- Understand SQS receive-and-delete vs receive-and-process patterns.
- Create SNS topics and SQS subscriptions with filter policies.
- Distinguish between Standard and FIFO SNS topics.
- Filter SNS messages by message attributes using JSON filter policies.
- Create EventBridge custom event buses and pattern-based rules.
- Write event patterns with numeric, string, and complex conditions.
- Route events from custom sources to multiple targets (SQS, Lambda, SNS).
- Create one-time and recurring schedules with EventBridge Scheduler.
- Configure retry policies, DLQs, and maximum event age.
- Create Kinesis Data Streams with on-demand and provisioned capacity.
- Publish records with partition keys and understand shard distribution.
- Build an end-to-end Kinesis → Firehose → S3 pipeline.
- Configure Firehose buffering, compression, and error handling.
- Understand Amazon MQ use cases (RabbitMQ, ActiveMQ) and MSK (Kafka) patterns.
- Design event-driven architectures combining multiple messaging services.
- Test visibility timeout, ordering, filtering, and delivery guarantees.

## Architecture Overview

```text
SQS Standard queue -> visibility timeout -> DLQ -> redrive
SQS FIFO queue -> message group -> deduplication

SNS topic
  +-> Standard orders queue (all messages)
  +-> Priority orders queue (HIGH priority only via filter)

Custom application event
  -> EventBridge custom bus
  -> amount > 5000 rule
  -> Priority SQS queue

One-time schedule
  -> EventBridge Scheduler
  -> Payment reminder in SQS

Real-time clickstream
  -> Kinesis Data Streams
  -> Data Firehose
  -> Private S3 bucket (encrypted, partitioned by date/hour)
```

## Minimum Submission for Day 17

- SQS Standard queue: visibility timeout proof, message in-flight state
- SQS FIFO queue: message ordering and deduplication validation
- Dead-letter queue proof and successful redrive to source
- SNS topic with two SQS subscriptions (standard and filtered)
- SNS filter policy test: NORMAL message to standard queue only, HIGH to both
- EventBridge custom bus and rule with numeric amount condition
- EventBridge rule target routing: amount > 5000 delivers to priority queue
- EventBridge Scheduler: one-time payment reminder at scheduled time
- Kinesis Data Stream: put-record proof and shard data viewer
- Firehose delivery stream: Kinesis source, S3 destination, successful delivery
- S3 objects from Kinesis records: CloudShell copy and data inspection
- Architecture diagram showing all eight AWS services
- Cleanup proof (all resources deleted)
- Public learning post on LinkedIn

## Cost and Safety

- Use the ap-south-1 (Mumbai) region for all services to minimize latency.
- S3 bucket names are globally unique; use account ID and region suffix to avoid conflicts.
- DLQ retention (14 days) is longer than source queue (4 days) to preserve failed messages.
- Visibility timeout must be long enough for consumer processing plus retry buffer.
- Kinesis on-demand capacity simplifies billing for practice workloads.
- Firehose buffer size (5 MiB) and interval (300 seconds) determine S3 delivery latency.
- EventBridge Scheduler automatically deletes one-time schedules after execution.
- All resources must be deleted in the correct order (Firehose → Kinesis → EventBridge).
- Never commit AWS account IDs, ARNs, or queue URLs to version control.
- Tag all resources with `Project = CloudAdhar-AWS-Zero-To-Hero` for cost tracking.

## Learning Path

**Week 8 Prerequisites:** You understand VPC, security groups, routing, and hybrid connectivity.

**Week 9 Builds On:** All previous weeks. You now decouple applications with messaging and events.

**Week 10 Applies:** Event-driven auto-scaling, Lambda with SQS/SNS triggers, cross-region replication.

## Exam + Pillar Mapping

| Topic | Exam Domain | Pillar | Best Practice |
|---|---|---|---|
| SQS vs SNS | Domain 3 | Integration | Choose queue vs topic by pattern |
| Visibility timeout | Domain 3 | Reliability | Prevent duplicate processing |
| DLQ | Domain 3 | Reliability | Preserve failed messages |
| FIFO guarantee | Domain 3 | Reliability | Order-critical workflows only |
| SNS filtering | Domain 3 | Efficiency | Reduce unnecessary subscriptions |
| EventBridge patterns | Domain 3 | Integration | Route by event content |
| EventBridge Scheduler | Domain 2 | Reliability | Replace cron jobs safely |
| Kinesis partitioning | Domain 3 | Performance | Distribute throughput by key |
| Firehose delivery | Domain 2 | Reliability | Batch and buffer for cost |
| Message deduplication | Domain 3 | Reliability | Idempotent consumers |

## Rules

- Do not share AWS account IDs, ARNs, access keys, or resource endpoints publicly.
- Use training AWS accounts only; never test on production.
- Delete all resources after the lab; do not leave queues, streams, or buckets running.
- Prefer AWS Management Console for this week; use CloudShell only for Kinesis CLI.
- Document all test results with timestamps and message counts.
- Explain your architecture decisions in the submission.

<div align="center">

[Home](../README.md) | [Week 8](../week-08/) | [Week 10](../week-10/)

</div>
