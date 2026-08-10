# Day 12 Lab - S3 Replication, Transfer, and Hybrid Storage

Use the AWS Management Console for this practical. The core replication lab
uses one AWS account, Mumbai for the source and SRR destination, and Tokyo for
the CRR destination.

## Resources

| Purpose | Base name | Region |
|---|---|---|
| Replication source | `cloudadhar-day12-rep-source` | Mumbai, `ap-south-1` |
| SRR destination | `cloudadhar-day12-srr-dest` | Mumbai, `ap-south-1` |
| CRR destination | `cloudadhar-day12-crr-dest` | Tokyo, `ap-northeast-1` |
| SRR rule | `srr-prefix-rule` | Source bucket |
| CRR rule | `crr-prefix-rule` | Source bucket |
| Multipart cleanup rule | `abort-incomplete-multipart-uploads` | Source bucket |
| Optional compliance bucket | `cloudadhar-day11-object-lock` | Mumbai |
| Optional website bucket | `cloudadhar-day11-static-site` | Mumbai |

Account Regional namespace names include an AWS-generated account and Region
suffix. Always use the complete name displayed by your account, but mask it in
public evidence.

Tag Day 12 resources with `Project=AWS-Zero-To-Hero`, `Day=12`,
`Environment=Training`, and `Owner=<your-name>`.

## Sample Files

Use [day12-S3_Sample-Files](./day12-S3_Sample-Files/) and follow
[README_UPLOAD_ORDER.md](./day12-S3_Sample-Files/README_UPLOAD_ORDER.md).
Every file contains synthetic training data.

Important pre-rule mapping:

```text
01-before-rule/before-rule.txt -> srr/before-rule.txt
01-before-rule/before-rule.txt -> crr/before-rule.txt
```

The same local file is uploaded twice under different source keys before the
rules exist.

## Safety and Cost Gate

- Keep all three replication buckets private with ACLs disabled and BPA on.
- Do not enable Replication Time Control or paid replication metrics.
- Use SSE-S3 for the replication lab; SSE-KMS replication needs additional key
  permissions and configuration.
- CRR adds destination storage, requests, and inter-Region transfer charges.
- Transfer Acceleration adds charges when its endpoint is used.
- Do not deploy FSx, Storage Gateway, DataSync, Snow, or Transfer Family
  resources; review their selection only.
- Reuse an existing EFS filesystem for review; do not create a duplicate.
- The optional public website must use a separate disposable bucket in an
  isolated sandbox and must be secured immediately after evidence.
- Compliance retention cannot be bypassed. Use the shortest instructor-approved
  retain-until date and record pending cleanup.

## Optional Make-Up A - Object Lock Compliance

Use this only if the Compliance demonstration was missed on Day 11. It must use
a dedicated bucket, not a replication or website bucket.

### Create and configure the bucket

1. Open **S3 -> General purpose buckets -> Create bucket**.
2. Configure:
   - Region: Mumbai
   - Namespace: Account Regional namespace
   - Base name: `cloudadhar-day11-object-lock`
   - Object Ownership: Bucket owner enforced / ACLs disabled
   - Block all public access: On
   - Versioning: Enabled
   - Default encryption: SSE-S3
   - Object Lock: Enabled
3. Accept the Object Lock acknowledgement and create the bucket.
4. Do not set a long bucket-level default retention period.

### Prove exact-version protection

1. Upload
   `day11_S3_Sample_Files/lock/retention-demo.txt`.
2. Record its Version ID.
3. Under **Properties -> Object Lock retention -> Edit**, enable Compliance
   mode until the shortest instructor-approved lab date, such as the next
   calendar day.
4. Keep Legal Hold disabled on this object.
5. From the normal object list, delete `retention-demo.txt` without selecting a
   Version ID.
6. Confirm the normal delete succeeds by creating a delete marker.
7. Turn on **Show versions** and locate both the delete marker and protected
   data version.
8. Select only the retained data version and attempt permanent deletion.
9. Confirm `AccessDenied` and zero successfully deleted versions.

Object Lock protects the data version, not the visible key. A normal delete can
still add a delete marker. Compliance retention cannot be removed or bypassed
before expiry, including by root.

## Optional Make-Up B - Native S3 Static Website

This controlled lab intentionally demonstrates a public HTTP website endpoint.
Perform it only in an isolated sandbox with instructor approval. A production
design keeps S3 private and uses CloudFront Origin Access Control with HTTPS.

### Build the isolated website

1. Create `cloudadhar-day11-static-site` in Mumbai using Account Regional
   namespace, Bucket owner enforced, versioning, SSE-S3, and BPA on initially.
2. Upload these Day 11 samples directly to the bucket root:
   - `day11_S3_Sample_Files/website/index.html`
   - `day11_S3_Sample_Files/website/error.html`
3. Confirm both objects use `Content-Type: text/html`.
4. Open the plain Object URL in incognito and confirm `AccessDenied`.
5. Under **Properties -> Static website hosting**, enable **Host a static
   website** with `index.html` and `error.html`.
6. Copy the generated website endpoint and confirm it still returns 403 before
   public-read permission is configured.

### Temporarily allow only public GET

1. At the account level, keep both public-ACL protections on, but temporarily
   turn off only the two public-policy blockers required by this isolated lab.
2. Apply the same combination to the website bucket.
3. Add this bucket policy after inserting the exact full bucket name:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadForStaticWebsiteDemo",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::<FULL-WEBSITE-BUCKET-NAME>/*"
    }
  ]
}
```

Do not grant list, upload, or delete permissions.

4. Open the HTTP website endpoint in incognito and confirm `index.html`
   renders without `X-Amz-*` signed parameters.
5. Request `/missing-page.html` and confirm the custom error page renders.
6. Capture sanitized evidence.
7. Immediately delete the public bucket policy, restore all four bucket-level
   and account-level BPA controls, and disable website hosting.
8. Confirm the public endpoint no longer serves the page.

Never place private, replication, or locked data in this website bucket.

## Part 1 - Create Three Private Versioned Buckets

Create all three buckets from **S3 -> General purpose buckets -> Create
bucket**.

For every bucket:

- Bucket type: General purpose
- Namespace: Account Regional namespace
- Object Ownership: ACLs disabled / Bucket owner enforced
- Block all public access: On
- Versioning: Enabled
- Default encryption: SSE-S3
- Object Lock: Disabled
- Data: synthetic training files only

Use:

1. `cloudadhar-day12-rep-source` in Mumbai.
2. `cloudadhar-day12-srr-dest` in Mumbai.
3. `cloudadhar-day12-crr-dest` in Tokyo.

If Tokyo is unavailable, choose another enabled Region different from Mumbai
and record it. Verify every bucket's Region, versioning, encryption, ownership,
and BPA settings before continuing.

## Part 2 - Upload Objects Before the Rules

1. In the source bucket, create `srr/` and `crr/` prefixes.
2. Upload `01-before-rule/before-rule.txt` as:
   - `srr/before-rule.txt`
   - `crr/before-rule.txt`
3. Confirm both objects exist in the source before creating either rule.

These objects deliberately match the future filters but will prove that live
replication is not retroactive.

## Part 3 - Create the SRR Rule

1. Open **Source bucket -> Management -> Replication rules -> Create
   replication rule**.
2. Configure:
   - Name: `srr-prefix-rule`
   - Status: Enabled
   - Scope: Limit using filters
   - Prefix: `srr/`
   - Destination: bucket in this account
   - Destination bucket: the Mumbai SRR bucket
   - IAM role: Create new role
3. Leave unselected:
   - SSE-KMS/DSSE-KMS replication
   - destination storage-class change
   - Replication Time Control
   - replication metrics
   - delete-marker replication
   - replica modification sync
4. Save the rule.
5. When asked about existing objects, choose **No, do not replicate existing
   objects**.

## Part 4 - Create the CRR Rule

Repeat the rule flow with:

```text
Rule name: crr-prefix-rule
Status: Enabled
Prefix: crr/
Destination: Tokyo CRR bucket
IAM role: Create new role
Existing objects: No, do not replicate existing objects
```

Leave the same paid, KMS, delete-marker, and replica-modification options off.

Verify the source shows two enabled rules:

| Rule | Prefix | Destination |
|---|---|---|
| `srr-prefix-rule` | `srr/` | Mumbai SRR bucket |
| `crr-prefix-rule` | `crr/` | Tokyo CRR bucket |

Do not create a Batch Replication job during this lab.

## Part 5 - Validate SRR Version 1

1. Upload
   `02-srr/version-1/cloudadhar-srr-demo.txt` to the source key
   `srr/cloudadhar-srr-demo.txt`.
2. Open the source object's **Properties -> Replication status**.
3. Observe `PENDING` progressing to `COMPLETED`.
4. Open the Mumbai SRR destination and confirm:

```text
srr/cloudadhar-srr-demo.txt  -> present
srr/before-rule.txt          -> absent
```

The destination object can report `REPLICA`.

## Part 6 - Validate CRR Version 1

1. Upload
   `03-crr/version-1/cloudadhar-crr-demo.txt` to the source key
   `crr/cloudadhar-crr-demo.txt`.
2. Wait for `COMPLETED` on the source object.
3. Open the Tokyo destination and confirm:

```text
crr/cloudadhar-crr-demo.txt  -> present
crr/before-rule.txt          -> absent
```

## Part 7 - Validate Later Versions

### SRR Version 2

1. Upload `02-srr/version-2/cloudadhar-srr-demo.txt` using the same source key
   `srr/cloudadhar-srr-demo.txt`.
2. Wait for replication to complete.
3. Turn on **Show versions** in source and SRR destination.
4. Confirm both contain Version 1 and Version 2, while the pre-rule object is
   source-only.

### CRR Version 2

1. Upload `03-crr/version-2/cloudadhar-crr-demo.txt` using the same source key
   `crr/cloudadhar-crr-demo.txt`.
2. Wait for completion.
3. Turn on **Show versions** in source and CRR destination.
4. Confirm both versions replicated and the pre-rule object remains
   source-only.

## Part 8 - Prove Prefix Filtering

1. Create `other/` in the source bucket.
2. Upload `04-filter-control/no-replication-demo.txt` using the key
   `other/no-replication-demo.txt`.
3. Confirm it has no replication-status section because no rule matches.
4. Confirm it appears in neither destination.

## Part 9 - Review Existing-Object Replication

Open **Source -> Management -> Replication rules** and locate **Create
replication job**. Do not start it.

```text
New eligible versions -> live SRR or CRR
Existing or failed eligible versions -> S3 Batch Replication
```

## Part 10 - Inspect Transfer Acceleration

1. Open **Source -> Properties -> Transfer acceleration -> Edit**.
2. Enable it and save.
3. Record the accelerated endpoint pattern without publishing the full
   account-specific name.
4. Explain that the client must actually use the accelerated endpoint.
5. Confirm the bucket name contains no periods.

The sample file is conceptual; a small console upload does not prove that
Transfer Acceleration was used or improved performance.

## Part 11 - Abort Incomplete Multipart Uploads

1. Open **Source -> Management -> Lifecycle rules -> Create lifecycle rule**.
2. Configure:
   - Name: `abort-incomplete-multipart-uploads`
   - Scope: all objects
   - Action: delete incomplete multipart uploads
   - Age: 7 days
3. Leave transitions, completed-object expiration, noncurrent deletion, and
   expired delete-marker cleanup unselected.
4. Create and verify the rule.

This removes unfinished parts, not successfully completed objects.

## Part 12 - Review Existing EFS

Do not create another filesystem. Open the EFS filesystem from the earlier lab
and record:

- Regional or One Zone;
- General Purpose or Max I/O performance mode;
- Elastic, Provisioned, or Bursting throughput;
- VPC and mount-target subnets;
- mount-target Security Group and NFS TCP `2049` flow; and
- Access Points, if any.

If the earlier EFS lab was fully cleaned up, complete this as a design review
from the console creation screens and cancel without deploying resources.

## Part 13 - Review the FSx Family

Open **Amazon FSx -> Create file system**, review, and cancel:

| Choice | Workload signal |
|---|---|
| Windows File Server | SMB, Windows, Active Directory |
| Lustre | HPC, ML, parallel processing |
| NetApp ONTAP | Enterprise NAS and NetApp compatibility |
| OpenZFS | Managed ZFS for Linux workloads |

Do not create a filesystem.

## Part 14 - Hybrid Storage Decisions

Review service landing pages only:

| Requirement | Select |
|---|---|
| Cached NFS/SMB access to S3 | S3 File Gateway |
| Cloud-backed iSCSI volumes | Volume Gateway |
| Virtual backup tapes | Tape Gateway |
| Automated online movement | DataSync |
| Offline migration or edge compute | Snow Family |
| Managed SFTP/FTPS/FTP/AS2 into S3/EFS | Transfer Family |

Do not deploy these paid resources.

## Troubleshooting

| Symptom | Check |
|---|---|
| No replication status | Prefix match, enabled rule, and upload time after rule creation |
| Status remains `PENDING` | Asynchronous delay and destination Region availability |
| Status becomes `FAILED` | Versioning, service role, destination, and KMS permissions if used |
| Pre-rule objects are absent | Expected; live replication is not retroactive |
| Corrected failed object does not retry | Upload a new version or use Batch Replication |
| Acceleration cannot be enabled | Bucket dots, Region support, and IAM permission |
| Destination has one version | Verify Version 2 used the identical source key |
| Unmatched object replicated | Recheck rule scope and prefix filter |

## Validation Checklist

- [ ] Optional Compliance version rejected permanent deletion.
- [ ] Optional website loaded over the native HTTP endpoint.
- [ ] Website policy was removed and all BPA controls were restored.
- [ ] Three private, versioned SSE-S3 buckets exist in the correct Regions.
- [ ] Both prefix rules are enabled with the intended destinations.
- [ ] SRR Versions 1 and 2 reached Mumbai.
- [ ] CRR Versions 1 and 2 reached Tokyo.
- [ ] Both pre-rule objects remained source-only.
- [ ] The `other/` object matched no rule and remained source-only.
- [ ] Transfer Acceleration configuration was inspected.
- [ ] Seven-day incomplete multipart cleanup exists.
- [ ] Existing EFS configuration was reviewed without duplication.
- [ ] FSx and hybrid choices were reviewed without deploying resources.

After evidence, follow [06-cleanup.md](./06-cleanup.md).
