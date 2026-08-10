# Day 11 Lab - Private, Versioned, and Protected Amazon S3

Build one end-to-end S3 workflow for private reports. AWS resource operations
use the AWS Management Console. CloudShell is not required for the core lab.

## What You Will Prove

1. The source and destination buckets remain private.
2. Versioning protects against a normal deletion.
3. A manual bucket-to-bucket copy creates an independent destination object.
4. The destination bucket applies SSE-KMS and an S3 Bucket Key.
5. A normal Object URL is denied while a short-lived presigned URL works.
6. Lifecycle configuration controls future transitions and cleanup.
7. Legal Hold prevents permanent deletion of a protected object version.

## Resources

Choose one suffix using your initials and four digits, for example `gu-0808`.
Replace `<unique-suffix>` consistently.

| Resource | Exact naming pattern |
|---|---|
| Source bucket | `cloudadhar-s3-day11-<unique-suffix>` |
| Destination bucket | `cloudadhar-s3-day11-copy-<unique-suffix>` |
| Object Lock bucket | `cloudadhar-s3-day11-lock-<unique-suffix>` |
| KMS alias | `alias/cloudadhar-s3-day11` |
| Lifecycle rule | `logs-transition-and-cleanup` |
| Region | Asia Pacific (Mumbai), `ap-south-1` |

Add these tags to every bucket:

| Key | Value |
|---|---|
| `Project` | `AWS-Zero-to-Hero` |
| `Module` | `Amazon S3 - Part 1` |
| `Environment` | `Training` |
| `Owner` | `CloudAdhar` |
| `ManagedBy` | `Manual` |
| `CleanupAfter` | `8-Aug-2026` |
| `DataClassification` | `Training-Only` |

Use the applicable project, module, environment, owner, and cleanup tags on the
KMS key.

## Safety Gate

Before creating resources:

- [ ] Sign in with a training role, not the root user.
- [ ] Confirm the AWS account and `ap-south-1` Region.
- [ ] Confirm all four account-level S3 Block Public Access settings are on.
- [ ] Prepare an incognito/private browser window.
- [ ] Use only synthetic files created for this class.
- [ ] Confirm a budget or billing alert exists.
- [ ] Understand that KMS keys, retained object versions, storage, requests,
      retrieval, and data transfer can create charges.

Never disable Block Public Access for this lab. Never expose a presigned URL,
account ID, ARN, access key, session token, email address, or private data in
screenshots.

## 1. Review the Synthetic Sample Pack

Use [day11_S3_Sample_Files](./day11_S3_Sample_Files/) and follow
[UPLOAD_INSTRUCTIONS.md](./day11_S3_Sample_Files/UPLOAD_INSTRUCTIONS.md).

The pack contains Day 11 documents, two versions of the versioning object,
storage-class examples, a lifecycle log, presigned-access content, website
files, and Object Lock content. Use only these synthetic files or equivalent
training-only data.

Both version uploads have the same basename and must use the S3 key:

```text
versions/version-demo.txt
```

## 2. Create the Customer Managed KMS Key

1. Open **Key Management Service**.
2. Confirm **Asia Pacific (Mumbai)**.
3. Choose **Customer managed keys -> Create key**.
4. Select:
   - Key type: Symmetric
   - Key usage: Encrypt and decrypt
   - Key material origin: KMS
   - Regionality: Single-Region key
5. Choose **Next**.
6. Set:
   - Alias: `cloudadhar-s3-day11`
   - Description: `Day 11 Amazon S3 SSE-KMS training key`
7. Add the lab tags.
8. Select only the intended training role as key administrator.
9. Select the intended training role for key usage.
10. Review the key policy and choose **Finish**.

Validate:

- Alias is `alias/cloudadhar-s3-day11`.
- Status is **Enabled**.
- Type is symmetric, usage is encrypt/decrypt, and Region is Mumbai.

The S3 bucket and KMS key must share a Region. Upload with SSE-KMS generally
needs `kms:GenerateDataKey`; download needs `kms:Decrypt`.

## 3. Create the Private Source Bucket

1. Open **Amazon S3 -> General purpose buckets -> Create bucket**.
2. Configure:
   - Region: Asia Pacific (Mumbai), `ap-south-1`
   - Bucket type: General purpose
   - Namespace: Global namespace when available for this reusable naming lab
   - Name: `cloudadhar-s3-day11-<unique-suffix>`
3. Under **Object Ownership**, select **ACLs disabled** and confirm
   **Bucket owner enforced**.
4. Keep **Block all public access** selected and confirm all four detailed
   controls remain selected.
5. Enable **Bucket Versioning**.
6. Add every mandatory bucket tag.
7. Select **SSE-S3** for default encryption.
8. Keep Object Lock disabled on this bucket.
9. Create the bucket.

Expected state:

| Control | Expected value |
|---|---|
| Ownership | Bucket owner enforced |
| ACLs | Disabled |
| Block Public Access | All four on |
| Versioning | Enabled |
| Default encryption | SSE-S3 |
| Object Lock | Disabled |

If AWS produces a complete account-Regional bucket name, record and use the
exact displayed name in every later step.

## 4. Create the SSE-KMS Destination Bucket

1. Create another General Purpose bucket in Mumbai named
   `cloudadhar-s3-day11-copy-<unique-suffix>`.
2. Keep ACLs disabled and Bucket owner enforced.
3. Keep all four Block Public Access controls enabled.
4. Enable versioning and add all mandatory tags.
5. For default encryption, choose **SSE-KMS**.
6. Choose from your AWS KMS keys and select
   `alias/cloudadhar-s3-day11`.
7. Enable **S3 Bucket Key**.
8. Keep Object Lock disabled and create the bucket.
9. Open **Properties** and verify versioning, SSE-KMS, the correct KMS key, and
   Bucket Key enabled.

## 5. Create Prefixes and Upload Storage-Class Examples

In the source bucket, create these folders through **Create folder**:

```text
documents/
versions/
logs/
storage/
presigned/
```

These are prefixes in object keys, not filesystem directories.

Upload:

1. `class-notes.txt` and `private-report.txt` into `documents/` using S3
   Standard and inherited SSE-S3.
2. `application.log` into `logs/` using S3 Standard.
3. `standard-demo.txt` into `storage/` using S3 Standard.
4. `intelligent-tiering-demo.txt` into `storage/` after selecting
   **S3 Intelligent-Tiering** under upload properties.

Open each object in `storage/` and verify its storage class under
**Properties**. Small objects under 128 KB remain in the Intelligent-Tiering
Frequent Access tier and are not automatically tiered.

## 6. Create Versions, Delete, and Recover

### Upload version 1

1. Open `versions/` in the source bucket.
2. Upload `day11_S3_Sample_Files/versions/v1/version-demo.txt`.
3. Open its properties and record the version ID.

### Upload version 2 under the same key

1. Upload `day11_S3_Sample_Files/versions/v2/version-demo.txt`, ensuring its S3
   destination key remains exactly `versions/version-demo.txt`.
2. Upload it into `versions/` and confirm the overwrite prompt.
3. Turn on **Show versions**.
4. Verify two data versions with different version IDs and Version 2 as the
   current version.

### Create and remove a delete marker

1. Turn **Show versions** off.
2. Select `version-demo.txt` and choose **Delete**.
3. Confirm the requested text and delete the object.
4. Confirm it disappears from the normal object list.
5. Turn **Show versions** on.
6. Find and select only the delete marker.
7. Permanently delete that delete marker.
8. Turn **Show versions** off and open the object.
9. Confirm the previous Version 2 data is current again.

Do not permanently delete either data version during the recovery test.

## 7. Copy the Private Report and Change Encryption

1. Open the source bucket and `documents/`.
2. Select `private-report.txt` and choose **Actions -> Copy**.
3. Under **Destination**, choose **Browse S3**.
4. Select `cloudadhar-s3-day11-copy-<unique-suffix>`.
5. Create or choose the `copied/` prefix.
6. Confirm the final destination resembles:

   ```text
   s3://cloudadhar-s3-day11-copy-<unique-suffix>/copied/
   ```

7. Under **Additional copy settings**, select **Don't specify settings** so
   the destination bucket default determines encryption.
8. Choose **Copy** and wait for success.
9. In the destination bucket, open `copied/private-report.txt`.
10. Under **Properties**, verify:
    - SSE-KMS encryption;
    - the Day 11 customer managed key;
    - an independent destination version ID; and
    - private access.

The source remains SSE-S3. The new destination object is independent and uses
the destination bucket's SSE-KMS default. This is manual copy, not S3
Replication.

Optional: copy `class-notes.txt` again while explicitly selecting
Intelligent-Tiering and SSE-KMS, using the destination key
`copied/class-notes-intelligent-tiering.txt`.

## 8. Prove Private Access and Use a Presigned URL

### Normal URL denial

1. Open `documents/private-report.txt` in the source bucket.
2. Copy its normal **Object URL**.
3. Open the URL in an incognito/private window.
4. Confirm `AccessDenied`; the object content must not load.

### Safe Block Public Access demonstration

Stop immediately if any Block Public Access setting is off.

1. Open the source bucket's **Permissions** tab.
2. Confirm bucket Block Public Access is **On** with all four controls.
3. Under **Bucket policy**, choose **Edit**.
4. Replace the bucket name and paste this controlled test policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ControlledPublicReadTest",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::cloudadhar-s3-day11-<unique-suffix>/*"
    }
  ]
}
```

5. Choose **Save changes**.
6. Confirm S3 rejects the policy or prevents it from granting public access
   because Block Public Access remains enabled.
7. Capture the sanitized denial.
8. Cancel or remove the test text, confirm no public statement remains, and
   reconfirm Block Public Access is on.

Never disable a Block Public Access control to force this test to succeed.

### Short-lived presigned GET

1. In `documents/`, select `private-report.txt`.
2. Choose **Actions -> Share with a presigned URL**.
3. Select the shortest practical expiry, approximately five minutes when
   available.
4. Create and privately copy the URL.
5. Do not display it in chat, screenshots, or recordings.
6. Open it in the incognito window and confirm the object opens or downloads.
7. Confirm the normal Object URL still returns `AccessDenied`.
8. After expiry, refresh the presigned URL and confirm it fails.

## 9. Configure Lifecycle Management

1. Open the source bucket's **Management** tab.
2. Under **Lifecycle rules**, choose **Create lifecycle rule**.
3. Name it `logs-transition-and-cleanup`.
4. Limit scope to the prefix `logs/`.
5. Select actions for:
   - current-version transitions;
   - noncurrent-version transitions;
   - current-version expiration;
   - permanent noncurrent-version deletion; and
   - expired delete-marker or incomplete multipart-upload cleanup.
6. Configure current versions:
   - transition to Standard-IA after 30 days;
   - transition to Glacier Flexible Retrieval after 90 days; and
   - expire after 365 days.
7. Configure noncurrent versions:
   - transition to Standard-IA after 30 days; and
   - permanently delete after 90 days.
8. Select expired delete-marker cleanup when the console offers it for the
   chosen rule combination.
9. Abort incomplete multipart uploads after 7 days.
10. Review the timeline and warnings, then create the rule.
11. Verify the rule is enabled and scoped only to `logs/`.

Do not wait for a transition during class. Lifecycle actions are asynchronous
and storage-duration charges still apply.

## 10. Demonstrate Object Lock with Legal Hold

Use a separate bucket to isolate irreversible retention settings.

### Create the lock bucket

1. Create a General Purpose bucket in Mumbai named
   `cloudadhar-s3-day11-lock-<unique-suffix>`.
2. Keep ACLs disabled, Bucket owner enforced, and all Block Public Access
   settings enabled.
3. Enable versioning and add the mandatory tags.
4. Keep default encryption as SSE-S3.
5. Under **Advanced settings**, enable **Object Lock** and acknowledge the
   warning.
6. Do not configure Compliance-mode default retention.
7. Create the bucket.

### Apply Legal Hold and test deletion

1. Create `lock/` and upload `retention-demo.txt`.
2. Select the exact object version and open **Properties**.
3. Edit **Object Lock legal hold**, set it to **On**, and save.
4. Attempt to permanently delete the protected object version.
5. Confirm deletion is denied while Legal Hold is on.
6. Return to its properties and set Legal Hold to **Off**.
7. Select the exact version and permanently delete it.
8. Confirm deletion succeeds when no retention period also protects it.

Do not use Compliance mode in this disposable environment. It cannot be
bypassed before expiry, including by the root user.

## Troubleshooting Order

| Symptom | Check |
|---|---|
| Bucket name already exists | Change only the unique suffix and record the complete name |
| Bucket is missing | Account, Region filter, and General Purpose bucket tab |
| Copy fails | Source `GetObject`, destination `PutObject`, and KMS permissions |
| Destination shows SSE-S3 | Destination default and **Don't specify settings** choice |
| SSE-KMS upload is denied | `kms:GenerateDataKey` on the intended key |
| SSE-KMS download is denied | `kms:Decrypt` on the intended key |
| Normal URL works anonymously | Stop, restore BPA, remove public policy/ACL, and inspect Access Analyzer |
| Presigned URL fails immediately | Expiry, exact key, signer S3 permission, and KMS permission |
| Version recovery fails | Ensure only the delete marker, not a data version, was deleted |
| Lifecycle transition is absent | Validate the rule; the minimum age has not passed |
| Locked bucket cannot be emptied | Remove Legal Holds and observe retention periods |
| Bucket deletion fails | Delete all versions, delete markers, and multipart uploads |

## Evidence Checklist

- [ ] Source bucket has Bucket owner enforced, BPA on, versioning, and SSE-S3.
- [ ] Destination has BPA on, versioning, SSE-KMS, and S3 Bucket Key enabled.
- [ ] Standard and Intelligent-Tiering properties are visible.
- [ ] Two version IDs and the delete marker were observed.
- [ ] The object was recovered by removing only the delete marker.
- [ ] `copied/private-report.txt` exists independently and uses the KMS key.
- [ ] Normal Object URL returns `AccessDenied`.
- [ ] Public-policy test fails safely while BPA remains on.
- [ ] Presigned GET works temporarily without exposing its URL.
- [ ] Lifecycle rule is enabled with `logs/` scope and full timeline.
- [ ] Legal Hold blocks deletion, then cleanup succeeds after hold removal.

Proceed to [06-cleanup.md](./06-cleanup.md) after capturing sanitized evidence.
