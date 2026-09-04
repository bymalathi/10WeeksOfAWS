# Week 9 Cleanup

Capture sanitized evidence first. Check SQS, SNS, EventBridge, EventBridge Scheduler,
Kinesis, Firehose, S3, and IAM in ap-south-1 (Mumbai) before declaring cleanup complete.

## Day 17 Resource Deletion Order

The order matters because resources depend on each other. Delete in this sequence:

### Firehose and Kinesis (First)

1. **Stop Firehose demo data** if it is still running (optional demo-data feature).
2. Delete the delivery stream `cloudadhar-clickstream-firehose-day17`.
   - Wait until it shows as `Deleted` in the console (may take 1-2 minutes).
3. Delete the Kinesis data stream `cloudadhar-clickstream-day17`.
   - Wait until it shows as `Deleting` or disappears.
4. Empty and delete the S3 bucket `cloudadhar-day17-streaming-051495879003-ap-south-1-an`.
   - Delete all objects (use console bulk delete or AWS CLI).
   - Confirm no versioning or object locks retain data.
   - Delete the bucket.

### EventBridge (Second)

5. Delete the EventBridge rule `cloudadhar-high-value-orders-rule-day17`.
   - Confirm it is removed from the custom bus `cloudadhar-orders-bus-day17`.
6. Delete the custom event bus `cloudadhar-orders-bus-day17`.
   - Confirm no remaining rules on this bus.
7. Verify the one-time schedule `cloudadhar-payment-reminder-day17` was **automatically deleted** after execution.
   - If it still exists (e.g., test schedule from the future), delete it manually.
   - No EventBridge Scheduler resources should remain.

### SNS and SQS (Third)

8. Delete SNS subscriptions:
   - Open the SNS topic `cloudadhar-orders-topic-day17`.
   - Delete the subscription whose endpoint is `cloudadhar-orders-standard-day17`.
   - Delete the subscription whose endpoint is `cloudadhar-priority-orders-day17`.
   - Confirm both subscriptions show `Deleted`.
9. Delete the SNS topic `cloudadhar-orders-topic-day17`.
   - Confirm it is gone from the Topics list.
10. Purge and delete SQS queues in this order:
    - **Priority queue first:** `cloudadhar-priority-orders-day17`
      - Action -> Purge queue.
      - Delete the queue.
    - **Standard queue second:** `cloudadhar-orders-standard-day17`
      - Edit to **disable** the dead-letter queue before deleting.
      - Purge the queue.
      - Delete the queue.
    - **DLQ last:** `cloudadhar-orders-dlq-day17`
      - Purge the queue.
      - Delete the queue.
    - Confirm all queues are gone from the Queues list.

### FIFO Queue

11. Delete the FIFO queue `cloudadhar-orders-fifo-day17.fifo`.
    - Purge first.
    - Delete the queue.
    - Confirm it is gone.

### IAM Roles and Policies

12. Delete generated execution roles (only if they are lab-specific):
    - **EventBridge rule execution role:** `ebrule-cloudadhar-high-value-orders-rule-day17-...`
    - **EventBridge Scheduler execution role:** `service-role/EventBridgeSchedulerRole-...`
    - **Firehose service role:** `service-role/aws-kinesisfirehose-...`
    - Confirm these roles contain only the day-17 policy permissions and are not shared.
    - Do NOT delete shared VPC, S3, or account-level roles.
13. Remove any inline policies attached to roles.
14. Confirm all created execution roles are deleted.

## Preserve Shared Resources

Do not delete:

- Shared VPCs, subnets, Security Groups, or VPC endpoints.
- Shared IAM roles used by other lab weeks or production workloads.
- Shared KMS keys or encryption resources.
- CloudWatch log groups used by other services or applications.
- Any resource tagged differently or from a different week.

## Verification Checklist

Use this checklist to confirm complete cleanup:

### SQS
- [ ] Standard orders queue deleted
- [ ] FIFO orders queue deleted
- [ ] Priority orders queue deleted
- [ ] Dead-letter queue deleted
- [ ] No queues named `cloudadhar-orders-*-day17` remain
- [ ] No queues named `cloudadhar-priority-orders-day17` remain

### SNS
- [ ] Both subscriptions deleted from topic
- [ ] Topic `cloudadhar-orders-topic-day17` deleted
- [ ] No SNS topics named `cloudadhar-orders-topic-day17` remain

### EventBridge
- [ ] Rule `cloudadhar-high-value-orders-rule-day17` deleted
- [ ] Custom bus `cloudadhar-orders-bus-day17` deleted
- [ ] One-time schedule automatically deleted or manually removed
- [ ] No EventBridge rules on default bus for day 17
- [ ] No custom buses for day 17 remain

### Kinesis and Firehose
- [ ] Firehose stream `cloudadhar-clickstream-firehose-day17` deleted
- [ ] Kinesis stream `cloudadhar-clickstream-day17` deleted
- [ ] S3 bucket `cloudadhar-day17-streaming-051495879003-ap-south-1-an` deleted (or alternative name)
- [ ] No S3 objects or versions remain for this bucket
- [ ] No data-lake prefixes for day 17 remain in shared buckets

### IAM
- [ ] EventBridge rule execution role deleted
- [ ] Firehose service role deleted
- [ ] Scheduler execution role deleted
- [ ] No day-17 inline policies remain in shared roles
- [ ] No day-17 managed policies remain

### Region Check
- [ ] All deletions confirmed in ap-south-1 (Mumbai)
- [ ] No day-17 resources accidentally created in other regions
- [ ] CloudWatch Logs cleaned up (optional but recommended)

## Final Confirmation

Run this command in AWS CloudShell (ap-south-1) to verify no resources remain:

```bash
# List all SQS queues for this account
aws sqs list-queues \
  --region ap-south-1 \
  --query 'QueueUrls[] | []' \
  --output text | grep day17

# List all SNS topics
aws sns list-topics \
  --region ap-south-1 \
  --query 'Topics[].TopicArn' \
  --output text | grep day17

# List all EventBridge event buses
aws events list-event-buses \
  --region ap-south-1 \
  --query 'EventBuses[].Name' \
  --output text | grep day17

# List all Kinesis streams
aws kinesis list-streams \
  --region ap-south-1 \
  --output text | grep day17

# List all Firehose delivery streams
aws firehose list-delivery-streams \
  --region ap-south-1 \
  --query 'DeliveryStreamNames[]' \
  --output text | grep day17
```

**Expected output:** Empty (no matches).

If any matches appear, continue deletion until all day-17 resources are gone.

## Post-Cleanup Verification

After deleting all resources:

1. Confirm the lab consumed resources are now gone.
2. Review your AWS bill to verify no surprise charges from retained resources.
3. Check CloudTrail for `day17` API calls and confirm they have stopped.
4. Document any lessons learned from the cleanup process.

