# AWS Zero To Hero — Day 14 Practical
## DynamoDB Orders Application, Queries, TTL, Streams, Lambda and Temporary UI

**Session:** Day 14 — DynamoDB + ElastiCache<br>
**Date:** 16-Aug-2026<br>
**Duration:** 120 minutes<br>
**Brand:** CloudAdhar x TrainWithShubham<br>
**Region:** `ap-south-1`

Companion files in this week:

- [Day 14 student guide](./AWS_Zero_To_Hero_Day14_DynamoDB_and_ElastiCache_Student_Guide.pdf)
- [Standalone Lambda UI helper](./day14.py)

The standalone helper is provided as a deployable alternative to copying the
larger inline example from section 28. Review its environment variables and
permissions before deployment, and keep the temporary Function URL cleanup
requirements below.

---

## 1. Practical objective

In this practical we build a small order-tracking application from scratch and demonstrate:

- Access-pattern-first table design
- Composite partition and sort keys
- A Global Secondary Index named `GSI1`
- A Local Secondary Index named `LSI1`
- On-demand and provisioned capacity configurations
- Query versus Scan behavior
- Time to Live using `ExpiresAt`
- DynamoDB Streams using `NEW_AND_OLD_IMAGES`
- A Lambda Stream consumer
- A temporary browser UI served by a second Lambda
- The complete path from UI update to DynamoDB, Stream, Lambda and CloudWatch Logs
- Global Tables, DAX and ElastiCache decision points without creating expensive resources

The practical uses synthetic data only.

---

## 2. Final architecture

```text
                                      +---------------------------+
                                      | CloudWatch Logs           |
                                      | INSERT / MODIFY / REMOVE  |
                                      +-------------^-------------+
                                                    |
                                                    |
+---------+     temporary HTTPS      +-------------+-------------+
| Browser | -----------------------> | UI/API Lambda             |
| UI      |                          | cloudadhar-day14-ui        |
+---------+                          +-------------+-------------+
                                                    |
                                                    | GetItem / Query / UpdateItem
                                                    v
                                      +-------------+-------------+
CloudShell queries -----------------> | DynamoDB Orders Table     |
                                      | PK + SK + GSI1 + LSI1     |
                                      +-------------+-------------+
                                                    |
                                                    | DynamoDB Stream
                                                    v
                                      +-------------+-------------+
                                      | Stream Consumer Lambda    |
                                      | oldImage → newImage       |
                                      +---------------------------+
```

---

## 3. Resource names

| Resource | Name |
|---|---|
| Main DynamoDB table | `cloudadhar-orders-day14` |
| Global secondary index | `GSI1` |
| Local secondary index | `LSI1` |
| Optional provisioned table | `cloudadhar-capacity-demo-day14` |
| Stream Lambda | `cloudadhar-day14-stream-consumer` |
| UI/API Lambda | `cloudadhar-day14-ui` |
| TTL attribute | `ExpiresAt` |

---

## 4. Safety and cost rules

1. Do not perform the lab using the AWS account root user. Use an IAM administrator role for training, then reduce permissions for production.
2. Use only synthetic names, email addresses and order data.
3. Keep all resources in `ap-south-1` unless an instructor intentionally changes the design.
4. Do not create a DAX cluster, ElastiCache cache or Global Table replica merely to display the creation screen.
5. The optional UI uses a Lambda Function URL with `NONE` authentication. That URL is public.
6. Configure reserved concurrency, use an instructor write token and delete the Function URL immediately after the demonstration.
7. Run the cleanup checklist after class.
8. Mask account IDs, role ARNs and Function URLs in public screenshots or recordings.

---

# PART A — RESET AND REBUILD

## 5. Remove the earlier Day 14 lab before rebuilding

Only delete resources whose names exactly match this guide.

### Recommended console order

1. Open **Lambda → `cloudadhar-day14-ui` → Configuration → Function URL** and delete the URL if it exists.
2. Open **Lambda → `cloudadhar-day14-stream-consumer` → Configuration → Triggers** and delete the DynamoDB trigger.
3. Delete the two Lambda functions if they exist.
4. Open **DynamoDB → Tables → `cloudadhar-orders-day14`** and delete the table.
5. Delete `cloudadhar-capacity-demo-day14` if it exists.
6. Open IAM and remove the two generated Day 14 roles after confirming that no other Lambda uses them.

Wait until the table no longer appears before starting the rebuild.

### Read-only verification from CloudShell

```bash
aws dynamodb describe-table \
  --region ap-south-1 \
  --table-name cloudadhar-orders-day14 \
  --no-cli-pager
```

Expected before rebuilding:

```text
ResourceNotFoundException
```

---

## 6. Open CloudShell and define variables

```bash
export DAY14_REGION=ap-south-1
export DAY14_TABLE=cloudadhar-orders-day14
export DAY14_CAPACITY_TABLE=cloudadhar-capacity-demo-day14
export DAY14_STREAM_FUNCTION=cloudadhar-day14-stream-consumer
export DAY14_UI_FUNCTION=cloudadhar-day14-ui
export AWS_PAGER=""
```

Verify the identity:

```bash
aws sts get-caller-identity --no-cli-pager
```

The ARN should normally identify an IAM role or IAM user—not `:root`.

Verify the Region variable:

```bash
echo "$DAY14_REGION"
```

Expected:

```text
ap-south-1
```

---

## 7. Begin with the access patterns

Write these questions before creating the table:

1. Get customer `C101` profile.
2. List `C101` orders newest first.
3. Find order `O9001` without knowing its customer.
4. List `C101` orders by status.
5. Expire a temporary customer session.
6. React when an order changes.

Map them to keys:

| Access pattern | Key design |
|---|---|
| Customer profile | `PK=CUSTOMER#C101`, `SK=PROFILE` |
| Customer orders | `PK=CUSTOMER#C101`, `SK=ORDER#time#id` |
| Order by order ID | `GSI1PK=ORDER#id` |
| Customer orders by status | Same `PK`, `LSI1SK=STATUS#status#time` |
| Temporary session | `ExpiresAt` numeric TTL |
| React to update | Stream with old/new images |

Instructor explanation:

> The table schema is the result of the access patterns. We did not choose generic keys first and hope that the application queries would fit later.

---

## 8. Create the main table with GSI, LSI and Streams

The LSI must be created with the table. This command also creates the GSI, uses on-demand capacity and enables `NEW_AND_OLD_IMAGES` Streams.

```bash
aws dynamodb create-table \
  --region "$DAY14_REGION" \
  --table-name "$DAY14_TABLE" \
  --attribute-definitions \
    AttributeName=PK,AttributeType=S \
    AttributeName=SK,AttributeType=S \
    AttributeName=GSI1PK,AttributeType=S \
    AttributeName=GSI1SK,AttributeType=S \
    AttributeName=LSI1SK,AttributeType=S \
  --key-schema \
    AttributeName=PK,KeyType=HASH \
    AttributeName=SK,KeyType=RANGE \
  --local-secondary-indexes '[
    {
      "IndexName":"LSI1",
      "KeySchema":[
        {"AttributeName":"PK","KeyType":"HASH"},
        {"AttributeName":"LSI1SK","KeyType":"RANGE"}
      ],
      "Projection":{"ProjectionType":"ALL"}
    }
  ]' \
  --global-secondary-indexes '[
    {
      "IndexName":"GSI1",
      "KeySchema":[
        {"AttributeName":"GSI1PK","KeyType":"HASH"},
        {"AttributeName":"GSI1SK","KeyType":"RANGE"}
      ],
      "Projection":{"ProjectionType":"ALL"}
    }
  ]' \
  --billing-mode PAY_PER_REQUEST \
  --stream-specification \
    StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES \
  --tags \
    Key=Project,Value=AWS-Zero-To-Hero \
    Key=Day,Value=14 \
  --no-cli-pager
```

Wait for the table:

```bash
aws dynamodb wait table-exists \
  --region "$DAY14_REGION" \
  --table-name "$DAY14_TABLE"
```

Verify the design:

```bash
aws dynamodb describe-table \
  --region "$DAY14_REGION" \
  --table-name "$DAY14_TABLE" \
  --query 'Table.{
    Status:TableStatus,
    Billing:BillingModeSummary.BillingMode,
    BaseKey:KeySchema,
    GSI:GlobalSecondaryIndexes[].IndexName,
    LSI:LocalSecondaryIndexes[].IndexName,
    Stream:StreamSpecification.StreamViewType,
    StreamArn:LatestStreamArn
  }' \
  --no-cli-pager
```

Expected:

```text
Status   = ACTIVE
Billing  = PAY_PER_REQUEST
GSI      = GSI1
LSI      = LSI1
Stream   = NEW_AND_OLD_IMAGES
```

---

## 9. Insert the customer profile

```bash
aws dynamodb put-item \
  --region "$DAY14_REGION" \
  --table-name "$DAY14_TABLE" \
  --item '{
    "PK":{"S":"CUSTOMER#C101"},
    "SK":{"S":"PROFILE"},
    "Name":{"S":"Asha Student"},
    "Email":{"S":"asha@example.test"}
  }' \
  --no-cli-pager
```

The profile intentionally has no `GSI1PK` or `LSI1SK`. It does not need to appear in either index.

---

## 10. Insert two orders

### Order O9001

```bash
aws dynamodb put-item \
  --region "$DAY14_REGION" \
  --table-name "$DAY14_TABLE" \
  --item '{
    "PK":{"S":"CUSTOMER#C101"},
    "SK":{"S":"ORDER#2026-08-16T18:30:00Z#O9001"},
    "GSI1PK":{"S":"ORDER#O9001"},
    "GSI1SK":{"S":"CUSTOMER#C101"},
    "LSI1SK":{"S":"STATUS#PAID#2026-08-16T18:30:00Z"},
    "OrderId":{"S":"O9001"},
    "CreatedAt":{"S":"2026-08-16T18:30:00Z"},
    "Status":{"S":"PAID"},
    "Total":{"N":"2499"}
  }' \
  --no-cli-pager
```

### Order O9002

```bash
aws dynamodb put-item \
  --region "$DAY14_REGION" \
  --table-name "$DAY14_TABLE" \
  --item '{
    "PK":{"S":"CUSTOMER#C101"},
    "SK":{"S":"ORDER#2026-08-15T09:00:00Z#O9002"},
    "GSI1PK":{"S":"ORDER#O9002"},
    "GSI1SK":{"S":"CUSTOMER#C101"},
    "LSI1SK":{"S":"STATUS#OPEN#2026-08-15T09:00:00Z"},
    "OrderId":{"S":"O9002"},
    "CreatedAt":{"S":"2026-08-15T09:00:00Z"},
    "Status":{"S":"OPEN"},
    "Total":{"N":"899"}
  }' \
  --no-cli-pager
```

Verify the count:

```bash
aws dynamodb scan \
  --region "$DAY14_REGION" \
  --table-name "$DAY14_TABLE" \
  --select COUNT \
  --no-cli-pager
```

Expected immediately after these inserts:

```text
Count = 3
```

The table's **General information → Item count** can lag. Use an explicit request when you need to validate the current lab data.

---

# PART B — SHOW THE ACCESS PATTERNS

## 11. Access pattern 1: get the customer profile

Because both primary-key components are known, use `GetItem`.

```bash
aws dynamodb get-item \
  --region "$DAY14_REGION" \
  --table-name "$DAY14_TABLE" \
  --key '{
    "PK":{"S":"CUSTOMER#C101"},
    "SK":{"S":"PROFILE"}
  }' \
  --no-cli-pager
```

Explain:

> `GetItem` is an exact address. It needs the complete primary key.

---

## 12. Access pattern 2: list customer orders newest first

```bash
aws dynamodb query \
  --region "$DAY14_REGION" \
  --table-name "$DAY14_TABLE" \
  --key-condition-expression \
    'PK = :pk AND begins_with(SK, :prefix)' \
  --expression-attribute-values '{
    ":pk":{"S":"CUSTOMER#C101"},
    ":prefix":{"S":"ORDER#"}
  }' \
  --no-scan-index-forward \
  --return-consumed-capacity TOTAL \
  --no-cli-pager
```

Explain:

- `PK` selects one customer's item collection.
- `ORDER#` excludes the profile.
- ISO timestamps sort lexically.
- `--no-scan-index-forward` reverses ascending order and returns the newest order first.

---

## 13. Access pattern 3: find O9001 using GSI1

The request knows the order ID but not the customer ID.

```bash
aws dynamodb query \
  --region "$DAY14_REGION" \
  --table-name "$DAY14_TABLE" \
  --index-name GSI1 \
  --key-condition-expression 'GSI1PK = :order' \
  --expression-attribute-values '{
    ":order":{"S":"ORDER#O9001"}
  }' \
  --return-consumed-capacity TOTAL \
  --no-cli-pager
```

Explain:

```text
Base-table direction: CUSTOMER#C101 → orders
GSI direction:        ORDER#O9001   → customer
```

`GSI1` is a sparse index because only order items contain `GSI1PK` and `GSI1SK`.

---

## 14. Access pattern 4: list OPEN orders using LSI1

The request still targets one customer but uses status as the alternate sort dimension.

```bash
aws dynamodb query \
  --region "$DAY14_REGION" \
  --table-name "$DAY14_TABLE" \
  --index-name LSI1 \
  --key-condition-expression \
    'PK = :pk AND begins_with(LSI1SK, :status)' \
  --expression-attribute-values '{
    ":pk":{"S":"CUSTOMER#C101"},
    ":status":{"S":"STATUS#OPEN#"}
  }' \
  --consistent-read \
  --return-consumed-capacity TOTAL \
  --no-cli-pager
```

Explain:

- `LSI1` has the same `PK` as the base table.
- It uses `LSI1SK` instead of the base `SK` for ordering and conditions.
- An LSI query can request strong consistency.
- The LSI had to be created with the table.

---

## 15. Query versus Scan comparison

Run the targeted Query from section 12 and observe `ConsumedCapacity`.

Then run:

```bash
aws dynamodb scan \
  --region "$DAY14_REGION" \
  --table-name "$DAY14_TABLE" \
  --return-consumed-capacity TOTAL \
  --no-cli-pager
```

The sample table is tiny, so the capacity difference may also be tiny. Explain the scaling behavior:

> Query targets a known partition. Scan examines the table or index. A filter on Scan does not avoid the underlying read work.

---

# PART C — CAPACITY AND TTL

## 16. Show the main table's on-demand capacity

```bash
aws dynamodb describe-table \
  --region "$DAY14_REGION" \
  --table-name "$DAY14_TABLE" \
  --query 'Table.BillingModeSummary.BillingMode' \
  --output text \
  --no-cli-pager
```

Expected:

```text
PAY_PER_REQUEST
```

Console path:

```text
DynamoDB
→ Tables
→ cloudadhar-orders-day14
→ Settings
→ Read/write capacity
```

Explain:

- `PAY_PER_REQUEST` is the API name for on-demand capacity.
- It is a good starting point for unknown or variable traffic.
- The console's **Warm throughput** values describe immediately supportable throughput readiness; they are not a count of requests currently being consumed.
- Use the **Monitor** tab and CloudWatch consumed-capacity/throttling metrics to discuss actual activity.

---

## 17. Optional: create a small provisioned-capacity comparison table

This table is for configuration comparison only. Do not run a load test.

```bash
aws dynamodb create-table \
  --region "$DAY14_REGION" \
  --table-name "$DAY14_CAPACITY_TABLE" \
  --attribute-definitions AttributeName=Id,AttributeType=S \
  --key-schema AttributeName=Id,KeyType=HASH \
  --billing-mode PROVISIONED \
  --provisioned-throughput \
    ReadCapacityUnits=1,WriteCapacityUnits=1 \
  --tags \
    Key=Project,Value=AWS-Zero-To-Hero \
    Key=Day,Value=14 \
  --no-cli-pager
```

Wait and describe:

```bash
aws dynamodb wait table-exists \
  --region "$DAY14_REGION" \
  --table-name "$DAY14_CAPACITY_TABLE"

aws dynamodb describe-table \
  --region "$DAY14_REGION" \
  --table-name "$DAY14_CAPACITY_TABLE" \
  --query 'Table.{
    Status:TableStatus,
    RCU:ProvisionedThroughput.ReadCapacityUnits,
    WCU:ProvisionedThroughput.WriteCapacityUnits
  }' \
  --no-cli-pager
```

Expected:

```text
RCU = 1
WCU = 1
```

Teaching comparison:

| On-demand | Provisioned |
|---|---|
| Pay per request | Configure RCU/WCU |
| Unknown/spiky workload | Stable/measurable workload |
| Minimal planning | Capacity planning and Auto Scaling |

Delete the optional table during cleanup.

---

## 18. Enable TTL

```bash
aws dynamodb update-time-to-live \
  --region "$DAY14_REGION" \
  --table-name "$DAY14_TABLE" \
  --time-to-live-specification \
    'Enabled=true,AttributeName=ExpiresAt' \
  --no-cli-pager
```

Verify:

```bash
aws dynamodb describe-time-to-live \
  --region "$DAY14_REGION" \
  --table-name "$DAY14_TABLE" \
  --query 'TimeToLiveDescription.[TimeToLiveStatus,AttributeName]' \
  --output table \
  --no-cli-pager
```

---

## 19. Insert an expiring session

Create an epoch timestamp two hours in the future:

```bash
export DAY14_EXPIRES_AT=$(date -u -d '+2 hours' +%s)

echo "$DAY14_EXPIRES_AT"
date -u -d "@$DAY14_EXPIRES_AT"
```

Insert the session:

```bash
aws dynamodb put-item \
  --region "$DAY14_REGION" \
  --table-name "$DAY14_TABLE" \
  --item "{
    \"PK\":{\"S\":\"SESSION#S1001\"},
    \"SK\":{\"S\":\"META\"},
    \"ExpiresAt\":{\"N\":\"$DAY14_EXPIRES_AT\"},
    \"UserId\":{\"S\":\"C101\"}
  }" \
  --no-cli-pager
```

Read it:

```bash
aws dynamodb get-item \
  --region "$DAY14_REGION" \
  --table-name "$DAY14_TABLE" \
  --key '{
    "PK":{"S":"SESSION#S1001"},
    "SK":{"S":"META"}
  }' \
  --no-cli-pager
```

Explain:

- `ExpiresAt` is a Number containing epoch seconds.
- TTL cleanup is asynchronous.
- The item may remain visible after expiry until DynamoDB deletes it.
- Do not wait for deletion during the class.

Console path:

```text
DynamoDB → Table → Settings → Time to Live (TTL)
```

---

# PART D — STREAMS AND LAMBDA

## 20. Confirm the Stream

The table was created with Streams enabled.

```bash
aws dynamodb describe-table \
  --region "$DAY14_REGION" \
  --table-name "$DAY14_TABLE" \
  --query 'Table.{
    Enabled:StreamSpecification.StreamEnabled,
    ViewType:StreamSpecification.StreamViewType,
    StreamArn:LatestStreamArn
  }' \
  --no-cli-pager
```

Console path:

```text
DynamoDB
→ Tables
→ cloudadhar-orders-day14
→ Exports and streams
```

Explain:

> This page proves that change capture is enabled. It does not display the old/new record payload. We will see the payload after Lambda consumes it and writes it to CloudWatch Logs.

---

## 21. Create the Stream consumer Lambda

Open:

```text
AWS Console → Lambda → Create function
```

Use:

```text
Function name: cloudadhar-day14-stream-consumer
Runtime: Latest supported Python runtime
Architecture: x86_64
Permissions: Create a new role with basic Lambda permissions
```

Create the function.

### Attach Stream-read permissions

Open:

```text
Lambda
→ cloudadhar-day14-stream-consumer
→ Configuration
→ Permissions
→ Execution role name
```

In IAM, attach:

```text
AWSLambdaDynamoDBExecutionRole
```

The role should have CloudWatch Logs permissions and the DynamoDB Stream actions required by the event-source mapping.

### Deploy the code

Replace `lambda_function.py` with:

```python
import json


def lambda_handler(event, context):
    processed = 0

    for record in event.get("Records", []):
        dynamodb = record.get("dynamodb", {})

        change = {
            "eventName": record.get("eventName"),
            "keys": dynamodb.get("Keys"),
            "oldImage": dynamodb.get("OldImage"),
            "newImage": dynamodb.get("NewImage"),
        }

        print(json.dumps(change))
        processed += 1

    return {"processedRecords": processed}
```

Choose **Deploy**.

---

## 22. Add the DynamoDB trigger

Open:

```text
Lambda
→ cloudadhar-day14-stream-consumer
→ Add trigger
→ DynamoDB
```

Configure:

```text
DynamoDB table: cloudadhar-orders-day14
Activate trigger: Yes
Batch size: 10
Starting position: Latest
Batch window: 0 / None
Concurrent batches per shard: 1
```

Choose **Add**.

If Lambda reports missing `GetRecords`, `GetShardIterator`, `DescribeStream` or `ListStreams`, wait briefly for IAM propagation and confirm `AWSLambdaDynamoDBExecutionRole` is attached to the Lambda execution role.

Verify from CloudShell:

```bash
aws lambda list-event-source-mappings \
  --region "$DAY14_REGION" \
  --function-name "$DAY14_STREAM_FUNCTION" \
  --query 'EventSourceMappings[].{
    State:State,
    Result:LastProcessingResult,
    Reason:StateTransitionReason,
    UUID:UUID
  }' \
  --output table \
  --no-cli-pager
```

Expected:

```text
State  = Enabled
Result = OK or No records processed
```

---

## 23. Test the Stream with two CloudShell tabs

### Tab 1: follow Lambda logs

```bash
aws logs tail \
  "/aws/lambda/$DAY14_STREAM_FUNCTION" \
  --region "$DAY14_REGION" \
  --since 1m \
  --format short \
  --follow \
  --no-cli-pager
```

### Tab 2: update the status and LSI sort key together

```bash
aws dynamodb update-item \
  --region "$DAY14_REGION" \
  --table-name "$DAY14_TABLE" \
  --key '{
    "PK":{"S":"CUSTOMER#C101"},
    "SK":{"S":"ORDER#2026-08-16T18:30:00Z#O9001"}
  }' \
  --update-expression \
    'SET #status = :status, LSI1SK = :lsi' \
  --expression-attribute-names '{
    "#status":"Status"
  }' \
  --expression-attribute-values '{
    ":status":{"S":"SHIPPED"},
    ":lsi":{"S":"STATUS#SHIPPED#2026-08-16T18:30:00Z"}
  }' \
  --return-values ALL_NEW \
  --no-cli-pager
```

Expected log concept:

```text
eventName = MODIFY
oldImage.Status = PAID
newImage.Status = SHIPPED
```

Stop log following with `Ctrl+C`.

---

## 24. Where exactly did the change happen?

Use this sequence during the class.

### A. DynamoDB current item

Open:

```text
DynamoDB
→ Tables
→ cloudadhar-orders-day14
→ Explore table items
```

Choose **Query**, enter:

```text
PK = CUSTOMER#C101
```

Find `O9001` and show:

```text
Status = SHIPPED
LSI1SK = STATUS#SHIPPED#2026-08-16T18:30:00Z
```

Explain:

> The item explorer shows the current version. It no longer shows `PAID` as the current status.

### B. Index maintenance

Open:

```text
DynamoDB → Table → Indexes
```

Show `GSI1` and `LSI1`. Query `LSI1` again with the `STATUS#SHIPPED#` prefix to prove that changing `LSI1SK` changed the indexed access path.

### C. Stream configuration

Open:

```text
DynamoDB → Table → Exports and streams
```

Show:

```text
Stream status = On
View type = New and old images
Latest stream ARN = present
```

Explain:

> This is the change-capture configuration, not a record viewer.

### D. Event delivery

Open:

```text
Lambda
→ cloudadhar-day14-stream-consumer
→ Configuration
→ Triggers
```

Show:

```text
State = Enabled
Last processing result = OK
```

### E. Old and new values

Open:

```text
Lambda
→ Monitor
→ View CloudWatch logs
→ latest log stream
```

Show:

```text
oldImage.Status = PAID
newImage.Status = SHIPPED
```

This is the visible proof of change history for the lab.

### F. Monitoring

Open:

```text
DynamoDB → Table → Monitor
```

Explain that monitoring shows aggregated request, latency, throttling and error behavior—not complete item values.

---

# PART E — TEMPORARY UI DEMO

## 25. Why use a second Lambda for the UI?

The existing Stream consumer has one responsibility: process Stream records.

The UI Lambda has another responsibility:

- Serve the HTML page.
- Query customer orders from the base table.
- Filter customer orders through `LSI1`.
- Search an order through `GSI1`.
- Update order status and the denormalized `LSI1SK` value.

Keeping these functions separate makes the event-driven flow easier to explain.

```text
UI Lambda writes the item.
Stream Lambda reacts to the item change.
```

---

## 26. Create the UI Lambda

Open:

```text
AWS Console → Lambda → Create function
```

Use:

```text
Function name: cloudadhar-day14-ui
Runtime: Latest supported Python runtime
Architecture: x86_64
Permissions: Create a new role with basic Lambda permissions
```

Create the function.

### Environment variables

Open:

```text
Configuration → Environment variables → Edit
```

Add:

```text
TABLE_NAME = cloudadhar-orders-day14
DEMO_TOKEN = choose-a-random-instructor-token
```

Generate a token in CloudShell if required:

```bash
openssl rand -hex 12
```

Do not place the token in screenshots or the HTML source.

### Limit public-demo concurrency

Open:

```text
Configuration → Concurrency → Edit
```

Set:

```text
Reserved concurrency = 2
```

This is only a cost-control guardrail. It is not authentication.

---

## 27. Give the UI Lambda least-privilege DynamoDB permissions

Open the UI Lambda's execution role:

```text
Lambda
→ cloudadhar-day14-ui
→ Configuration
→ Permissions
→ Execution role
```

In IAM, add an inline policy. Replace `<ACCOUNT_ID>` with the current account ID.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Day14OrdersReadWrite",
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:UpdateItem"
      ],
      "Resource": [
        "arn:aws:dynamodb:ap-south-1:<ACCOUNT_ID>:table/cloudadhar-orders-day14",
        "arn:aws:dynamodb:ap-south-1:<ACCOUNT_ID>:table/cloudadhar-orders-day14/index/*"
      ]
    }
  ]
}
```

Policy name:

```text
CloudAdharDay14OrdersAccess
```

Do not give this function permission to create or delete tables.

---

## 28. Deploy the UI Lambda code

Replace `lambda_function.py` with the following code and choose **Deploy**.

```python
import json
import os
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key


TABLE_NAME = os.environ["TABLE_NAME"]
DEMO_TOKEN = os.environ["DEMO_TOKEN"]
TABLE = boto3.resource("dynamodb").Table(TABLE_NAME)

ALLOWED_STATUSES = {
    "OPEN",
    "PAID",
    "PROCESSING",
    "SHIPPED",
    "DELIVERED",
    "COMPLETED",
}


HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>CloudAdhar Day 14 Order Dashboard</title>
  <style>
    :root { color-scheme: dark; font-family: Inter, system-ui, sans-serif; }
    body { margin: 0; background: #08111f; color: #e5eefb; }
    header { padding: 28px; background: linear-gradient(120deg,#162b55,#5b2a86); }
    h1 { margin: 0 0 8px; }
    header p { margin: 0; color: #cbd5e1; }
    main { max-width: 1050px; margin: auto; padding: 24px; }
    .panel { background: #101c30; border: 1px solid #263957; border-radius: 14px;
             padding: 18px; margin-bottom: 18px; }
    .controls { display: flex; gap: 10px; flex-wrap: wrap; align-items: end; }
    label { display: grid; gap: 6px; color: #b8c7dd; font-size: 14px; }
    input, select, button { border-radius: 8px; border: 1px solid #405575;
                            padding: 10px 12px; font: inherit; }
    input, select { background: #07101d; color: #e5eefb; }
    button { background: #7c3aed; color: white; border: 0; cursor: pointer; }
    button.secondary { background: #2563eb; }
    .orders { display: grid; grid-template-columns: repeat(auto-fit,minmax(260px,1fr)); gap: 14px; }
    .order { border: 1px solid #324764; border-radius: 12px; padding: 15px; background: #0b1627; }
    .status { display: inline-block; padding: 4px 8px; border-radius: 999px;
              background: #164e63; color: #a5f3fc; font-weight: 700; }
    .muted { color: #94a3b8; }
    .message { min-height: 24px; color: #93c5fd; }
    code { color: #f0abfc; }
  </style>
</head>
<body>
  <header>
    <h1>CloudAdhar Day 14 — Order Dashboard</h1>
    <p>Base Query · LSI status filter · GSI order search · Stream-triggered Lambda</p>
  </header>
  <main>
    <section class="panel">
      <div class="controls">
        <label>Customer ID
          <input id="customer" value="C101">
        </label>
        <label>Status filter through LSI1
          <select id="filterStatus">
            <option value="">All orders — base table</option>
            <option>OPEN</option><option>PAID</option><option>PROCESSING</option>
            <option>SHIPPED</option><option>DELIVERED</option><option>COMPLETED</option>
          </select>
        </label>
        <button onclick="loadOrders()">Load orders</button>
      </div>
      <p id="accessPath" class="muted"></p>
    </section>

    <section class="panel">
      <div class="controls">
        <label>Order ID — searched through GSI1
          <input id="orderId" value="O9001">
        </label>
        <button class="secondary" onclick="findOrder()">Find order</button>
        <label>Instructor write token
          <input id="token" type="password" placeholder="Required only for updates">
        </label>
      </div>
      <p id="message" class="message"></p>
    </section>

    <section id="orders" class="orders"></section>
  </main>

  <script>
    const statuses = ["OPEN","PAID","PROCESSING","SHIPPED","DELIVERED","COMPLETED"];

    function escapeHtml(value) {
      return String(value ?? "")
        .replaceAll("&", "&amp;").replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;").replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function orderCard(order) {
      const options = statuses.map(status =>
        `<option ${status === order.Status ? "selected" : ""}>${status}</option>`
      ).join("");

      return `<article class="order">
        <h3>${escapeHtml(order.OrderId)}</h3>
        <p><span class="status">${escapeHtml(order.Status)}</span></p>
        <p>Total: ₹${escapeHtml(order.Total)}</p>
        <p class="muted">${escapeHtml(order.CreatedAt)}</p>
        <select id="status-${escapeHtml(order.OrderId)}">${options}</select>
        <button onclick='updateStatus(${JSON.stringify(order.PK)},${JSON.stringify(order.SK)},${JSON.stringify(order.OrderId)})'>Update</button>
      </article>`;
    }

    function showOrders(items) {
      document.getElementById("orders").innerHTML = items.length
        ? items.map(orderCard).join("")
        : `<div class="panel">No matching orders.</div>`;
    }

    async function readJson(url, options = {}) {
      const response = await fetch(url, options);
      const body = await response.json();
      if (!response.ok) throw new Error(body.message || `HTTP ${response.status}`);
      return body;
    }

    async function loadOrders() {
      const customer = document.getElementById("customer").value.trim();
      const status = document.getElementById("filterStatus").value;
      const url = `/api/orders?customerId=${encodeURIComponent(customer)}&status=${encodeURIComponent(status)}`;
      try {
        const result = await readJson(url);
        showOrders(result.items);
        document.getElementById("accessPath").textContent = `Access path: ${result.accessPath}`;
        document.getElementById("message").textContent = `Loaded ${result.count} order(s).`;
      } catch (error) {
        document.getElementById("message").textContent = error.message;
      }
    }

    async function findOrder() {
      const orderId = document.getElementById("orderId").value.trim();
      try {
        const result = await readJson(`/api/order?orderId=${encodeURIComponent(orderId)}`);
        showOrders(result.items);
        document.getElementById("accessPath").textContent = "Access path: GSI1";
        document.getElementById("message").textContent = `GSI1 returned ${result.count} order(s).`;
      } catch (error) {
        document.getElementById("message").textContent = error.message;
      }
    }

    async function updateStatus(pk, sk, orderId) {
      const status = document.getElementById(`status-${orderId}`).value;
      const token = document.getElementById("token").value;
      try {
        await readJson("/api/status", {
          method: "POST",
          headers: {"content-type": "application/json", "x-demo-token": token},
          body: JSON.stringify({pk, sk, status})
        });
        document.getElementById("message").textContent =
          `Updated ${orderId} to ${status}. Check DynamoDB and the Stream Lambda logs.`;
        await loadOrders();
      } catch (error) {
        document.getElementById("message").textContent = error.message;
      }
    }

    loadOrders();
  </script>
</body>
</html>"""


def decimal_default(value):
    if isinstance(value, Decimal):
        if value % 1 == 0:
            return int(value)
        return float(value)
    raise TypeError


def response(status_code, body, content_type="application/json"):
    if not isinstance(body, str):
        body = json.dumps(body, default=decimal_default)

    return {
        "statusCode": status_code,
        "headers": {
            "content-type": content_type,
            "cache-control": "no-store",
            "x-content-type-options": "nosniff",
        },
        "body": body,
    }


def lambda_handler(event, context):
    request_context = event.get("requestContext", {})
    method = request_context.get("http", {}).get("method", "GET")
    path = event.get("rawPath", "/")
    query = event.get("queryStringParameters") or {}

    if method == "GET" and path == "/":
        return response(200, HTML, "text/html; charset=utf-8")

    if method == "GET" and path == "/api/orders":
        customer_id = query.get("customerId", "C101").strip().upper()
        status = query.get("status", "").strip().upper()
        pk = f"CUSTOMER#{customer_id}"

        if status:
            if status not in ALLOWED_STATUSES:
                return response(400, {"message": "Unsupported status"})

            result = TABLE.query(
                IndexName="LSI1",
                KeyConditionExpression=(
                    Key("PK").eq(pk)
                    & Key("LSI1SK").begins_with(f"STATUS#{status}#")
                ),
                ScanIndexForward=False,
            )
            access_path = "LSI1"
        else:
            result = TABLE.query(
                KeyConditionExpression=(
                    Key("PK").eq(pk) & Key("SK").begins_with("ORDER#")
                ),
                ScanIndexForward=False,
            )
            access_path = "Base table PK/SK"

        return response(
            200,
            {
                "accessPath": access_path,
                "count": result.get("Count", 0),
                "items": result.get("Items", []),
            },
        )

    if method == "GET" and path == "/api/order":
        order_id = query.get("orderId", "").strip().upper()
        if not order_id:
            return response(400, {"message": "orderId is required"})

        result = TABLE.query(
            IndexName="GSI1",
            KeyConditionExpression=Key("GSI1PK").eq(f"ORDER#{order_id}"),
        )

        return response(
            200,
            {
                "accessPath": "GSI1",
                "count": result.get("Count", 0),
                "items": result.get("Items", []),
            },
        )

    if method == "POST" and path == "/api/status":
        headers = {
            str(key).lower(): value
            for key, value in (event.get("headers") or {}).items()
        }

        if headers.get("x-demo-token") != DEMO_TOKEN:
            return response(403, {"message": "Invalid instructor token"})

        try:
            payload = json.loads(event.get("body") or "{}")
        except json.JSONDecodeError:
            return response(400, {"message": "Request body must be JSON"})

        pk = str(payload.get("pk", ""))
        sk = str(payload.get("sk", ""))
        status = str(payload.get("status", "")).upper()

        if not pk.startswith("CUSTOMER#") or not sk.startswith("ORDER#"):
            return response(400, {"message": "Only order items can be updated"})

        if status not in ALLOWED_STATUSES:
            return response(400, {"message": "Unsupported status"})

        current = TABLE.get_item(Key={"PK": pk, "SK": sk}).get("Item")
        if not current:
            return response(404, {"message": "Order not found"})

        created_at = current["CreatedAt"]

        updated = TABLE.update_item(
            Key={"PK": pk, "SK": sk},
            UpdateExpression="SET #status = :status, LSI1SK = :lsi",
            ExpressionAttributeNames={"#status": "Status"},
            ExpressionAttributeValues={
                ":status": status,
                ":lsi": f"STATUS#{status}#{created_at}",
            },
            ReturnValues="ALL_NEW",
        )

        return response(200, {"item": updated["Attributes"]})

    return response(404, {"message": "Route not found"})
```

---

## 29. Create the temporary Function URL

Open:

```text
Lambda
→ cloudadhar-day14-ui
→ Configuration
→ Function URL
→ Create function URL
```

Choose:

```text
Auth type = NONE
CORS = not required because the page and API use the same origin
```

Save and open the Function URL.

### Security explanation

`NONE` means unauthenticated public invocation. The instructor token protects only the write route implemented in the sample code; it does not make the Function URL private. Use synthetic data and delete the URL immediately after class.

For production, use an authenticated architecture such as API Gateway with an authorizer, Amazon Cognito or another approved identity layer.

---

## 30. Demonstrate the UI access paths

### A. Base table query

1. Customer ID: `C101`
2. Status filter: `All orders`
3. Choose **Load orders**.

Expected UI message:

```text
Access path: Base table PK/SK
```

### B. LSI query

1. Select `OPEN` in the status filter.
2. Choose **Load orders**.

Expected:

```text
Access path: LSI1
O9002 is returned
```

### C. GSI query

1. Order ID: `O9001`
2. Choose **Find order**.

Expected:

```text
Access path: GSI1
O9001 is returned without supplying C101
```

### D. Status update

1. Enter the instructor `DEMO_TOKEN` into the token field.
2. Find `O9001`.
3. Change the status to `DELIVERED`.
4. Choose **Update**.

Expected:

```text
UI Lambda calls UpdateItem
DynamoDB changes Status and LSI1SK
DynamoDB Stream emits MODIFY
Stream consumer Lambda runs
CloudWatch Logs contains oldImage and newImage
```

---

## 31. Perform the complete UI-to-Stream demonstration

Before the class:

1. Reset `O9001` to `PAID` and update `LSI1SK` accordingly.
2. Verify the event-source mapping is `Enabled` and `OK`.
3. Open the DynamoDB item explorer on `O9001`.
4. Open the UI in another browser tab.
5. Open CloudShell log following in a third tab.

During the class:

```text
Step 1: Show Status=PAID in DynamoDB item explorer.
Step 2: In the UI, change PAID → SHIPPED.
Step 3: Refresh item explorer and show Status=SHIPPED.
Step 4: Show LSI1SK changed to STATUS#SHIPPED#...
Step 5: Show the CloudWatch log with oldImage=PAID.
Step 6: Show the CloudWatch log with newImage=SHIPPED.
Step 7: Filter SHIPPED orders in the UI to invoke LSI1.
Step 8: Search O9001 in the UI to invoke GSI1.
```

Instructor narration:

> The browser did not write directly to DynamoDB. It called the UI Lambda. That Lambda used a targeted UpdateItem request. DynamoDB updated its current item and maintained the indexes. The Stream captured the before-and-after change. The event-source mapping delivered the record to the consumer Lambda, and CloudWatch Logs made that record visible to us.

---

# PART F — GLOBAL TABLES, DAX AND ELASTICACHE

## 32. Global Tables console demonstration

Open:

```text
DynamoDB
→ Tables
→ cloudadhar-orders-day14
→ Global tables
```

Show that the table currently has one Region.

Explain:

```text
Mumbai replica     ⇄     Singapore replica
ap-south-1                ap-southeast-1
```

Discuss:

- Multi-Region availability
- Local access for global users
- Multi-Region writes
- Replicated write, storage and data-transfer considerations
- MREC versus MRSC consistency choices

Do not add a replica in the standard class. The teaching table contains TTL and an LSI, which makes it unsuitable for an MRSC conversion. Use a separate empty table for a future advanced MRSC practical.

---

## 33. DAX console and decision demonstration

Open:

```text
DynamoDB → DAX → Clusters
```

Do not create a cluster. Explain the request path:

```text
Application → DAX cache hit → result
Application → DAX cache miss → DynamoDB → cache → result
```

Choose DAX when:

- DynamoDB is the database.
- Reads repeat frequently.
- Eventual consistency is acceptable.
- Microsecond cached-read latency is required.

Do not choose DAX to fix:

- Hot partition keys
- Table scans caused by missing access patterns
- Write-heavy workloads
- General Redis data-structure requirements

---

## 34. ElastiCache console and engine decision demonstration

Open:

```text
Amazon ElastiCache → Create cache
```

Show the engine choices and cancel without creating a cache.

| Requirement | Choose |
|---|---|
| Leaderboard or sorted sets | Redis OSS/Valkey |
| Sessions | Redis OSS/Valkey |
| Counters or rate limiting | Redis OSS/Valkey |
| Pub/sub | Redis OSS/Valkey |
| Simple disposable object cache | Memcached |
| DynamoDB-native read acceleration | DAX |

Explain:

> DAX is specialized for DynamoDB. Redis OSS/Valkey provides richer cache data structures and messaging features. Memcached is a simpler distributed object cache.

---

# PART G — TROUBLESHOOTING

## 35. CloudShell container-role metadata error

Symptom:

```text
Error retrieving credentials from container-role
Received non 200 response 500 from container metadata
```

Actions:

1. Choose **CloudShell → Actions → Restart AWS CloudShell**.
2. Close duplicate CloudShell tabs.
3. Refresh and reopen CloudShell.
4. Run:

```bash
aws sts get-caller-identity --no-cli-pager
```

Do not run `aws configure` with long-lived access keys inside CloudShell.

---

## 36. `aws logs tail` returns no output

Check the mapping:

```bash
aws lambda list-event-source-mappings \
  --region "$DAY14_REGION" \
  --function-name "$DAY14_STREAM_FUNCTION" \
  --query 'EventSourceMappings[].{
    State:State,
    Result:LastProcessingResult,
    Reason:StateTransitionReason
  }' \
  --output table \
  --no-cli-pager
```

Then create a fresh update and retry with a wider window:

```bash
aws logs tail \
  "/aws/lambda/$DAY14_STREAM_FUNCTION" \
  --region "$DAY14_REGION" \
  --since 30m \
  --format short \
  --no-cli-pager
```

Blank output normally means no matching log events existed in that interval.

---

## 37. Trigger creation reports missing Stream permissions

Confirm that the Stream consumer Lambda's execution role has:

```text
AWSLambdaDynamoDBExecutionRole
```

Wait briefly for IAM propagation, then add the trigger again.

Do not attach Stream-read permissions to the UI Lambda unless that function also consumes a Stream.

---

## 38. GSI or LSI query returns no items

Check that the item contains the relevant index keys:

```text
GSI query requires GSI1PK and GSI1SK.
LSI query requires PK and LSI1SK.
```

After a status change, confirm that the application updated both:

```text
Status
LSI1SK
```

---

## 39. Function URL returns 403

Check:

1. Function URL auth type is intentionally `NONE` for the temporary lab.
2. The console-created resource policy contains public Function URL invocation permissions.
3. The URL belongs to `cloudadhar-day14-ui`.
4. For `POST /api/status`, the instructor token matches the `DEMO_TOKEN` environment variable.

Do not weaken a production policy to solve a classroom setup problem.

---

## 40. UI returns AccessDeniedException

Confirm that the UI Lambda execution role has the inline policy from section 27 and that:

- The account ID is correct.
- The Region is `ap-south-1`.
- Both the table ARN and `index/*` ARN are present.
- The function's environment variable is exactly `TABLE_NAME=cloudadhar-orders-day14`.

---

# PART H — CLEANUP

## 41. Delete the public Function URL first

Open:

```text
Lambda
→ cloudadhar-day14-ui
→ Configuration
→ Function URL
→ Delete
```

This is the most important immediate cleanup action because the lab URL used public invocation.

---

## 42. Delete the DynamoDB trigger

Open:

```text
Lambda
→ cloudadhar-day14-stream-consumer
→ Configuration
→ Triggers
→ DynamoDB trigger
→ Delete
```

Wait until the event-source mapping is removed.

---

## 43. Delete the Lambda functions

Delete only:

```text
cloudadhar-day14-ui
cloudadhar-day14-stream-consumer
```

Then open IAM and delete their generated execution roles only after confirming that the roles are not shared by other functions.

---

## 44. Delete the DynamoDB tables

Verify the exact table names first:

```bash
echo "$DAY14_TABLE"
echo "$DAY14_CAPACITY_TABLE"
```

Delete the main table:

```bash
aws dynamodb delete-table \
  --region "$DAY14_REGION" \
  --table-name "$DAY14_TABLE" \
  --no-cli-pager
```

If the optional capacity table was created, delete it:

```bash
aws dynamodb delete-table \
  --region "$DAY14_REGION" \
  --table-name "$DAY14_CAPACITY_TABLE" \
  --no-cli-pager
```

---

## 45. Final cleanup verification

```bash
aws dynamodb list-tables \
  --region "$DAY14_REGION" \
  --query 'TableNames[?contains(@, `day14`)]' \
  --no-cli-pager

aws lambda list-functions \
  --region "$DAY14_REGION" \
  --query 'Functions[?contains(FunctionName, `day14`)].FunctionName' \
  --no-cli-pager
```

Also verify manually:

- No Day 14 Function URL remains.
- No Day 14 Lambda trigger remains.
- No DAX cluster was created.
- No ElastiCache cache was created.
- No Global Table replica was created.
- No unused Day 14 IAM execution role remains.

---

# PART I — CLASSROOM CHECKLIST

## 46. Instructor pre-class checklist

- [ ] Signed in through an IAM role, not root
- [ ] Region is `ap-south-1`
- [ ] Main table status is `ACTIVE`
- [ ] `GSI1` and `LSI1` exist
- [ ] TTL status is `ENABLED`
- [ ] Stream view is `NEW_AND_OLD_IMAGES`
- [ ] Stream consumer trigger is `Enabled`
- [ ] Last processing result is `OK`
- [ ] UI Lambda environment variables are configured
- [ ] UI Lambda DynamoDB policy is attached
- [ ] Function URL opens successfully
- [ ] Instructor token is available privately
- [ ] `O9001` is reset to `PAID`
- [ ] `LSI1SK` matches the current status
- [ ] CloudShell log tail command is ready
- [ ] Cleanup section is ready for use after class

---

## 47. Student evidence checklist

Students should capture or explain:

- [ ] Table key schema
- [ ] GSI and LSI definitions
- [ ] Customer profile `GetItem`
- [ ] Customer-orders base Query
- [ ] GSI order lookup
- [ ] LSI status query
- [ ] On-demand billing mode
- [ ] Optional provisioned RCU/WCU configuration
- [ ] TTL enabled on `ExpiresAt`
- [ ] Stream enabled with old/new images
- [ ] Lambda trigger status
- [ ] CloudWatch `MODIFY` event
- [ ] UI base-query result
- [ ] UI GSI search
- [ ] UI LSI filter
- [ ] Current item versus old/new Stream images
- [ ] Global Tables decision
- [ ] DAX decision
- [ ] Redis OSS/Valkey versus Memcached decision

---

## 48. Final demonstration summary

```text
Access-pattern list
        ↓
PK/SK table design
        ↓
GSI reverse lookup + LSI local status lookup
        ↓
On-demand table + optional provisioned comparison
        ↓
TTL session
        ↓
UI or CLI UpdateItem
        ↓
DynamoDB current state and index maintenance
        ↓
Stream MODIFY record
        ↓
Lambda oldImage/newImage log
        ↓
Global Tables, DAX and ElastiCache decisions
```

---

## 49. Official references

- [DynamoDB secondary indexes](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/SecondaryIndexes.html)
- [Local secondary indexes](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/LSI.html)
- [On-demand capacity mode](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/on-demand-capacity-mode.html)
- [Provisioned capacity mode](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/provisioned-capacity-mode.html)
- [DynamoDB TTL](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/TTL.html)
- [DynamoDB Streams](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.html)
- [Using Lambda with DynamoDB Streams](https://docs.aws.amazon.com/lambda/latest/dg/with-ddb-example.html)
- [DynamoDB Global Tables](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GlobalTables.html)
- [DynamoDB Accelerator](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DAX.html)
- [ElastiCache engine selection](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/SelectEngine.html)
- [Lambda Function URL access control](https://docs.aws.amazon.com/lambda/latest/dg/urls-auth.html)
