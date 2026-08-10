# Week 6 Cleanup

Capture sanitized evidence first. Cleanup must include every object version,
delete marker, multipart upload, bucket, and KMS dependency.

## 1. Expire Temporary Access

1. Allow the short-lived presigned URL to expire.
2. Remove it from local notes, shell history, chat, and screenshots.
3. Delete any disposable object used only for URL testing.
4. Confirm the source bucket contains no public bucket policy.
5. Confirm all four account- and bucket-level BPA settings remain enabled.

## 2. Empty and Delete the Object Lock Bucket

1. Open `cloudadhar-s3-day11-lock-<unique-suffix>`.
2. Remove every Legal Hold.
3. If Governance retention was optionally used, wait for expiry or use only a
   pre-approved and pre-tested authorized bypass.
4. Turn **Show versions** on.
5. Permanently delete every data version and delete marker.
6. Confirm no protected version remains.
7. Empty and delete the lock bucket.

Object Lock Compliance retention cannot be bypassed before expiry. If the
optional Day 12 make-up used Compliance mode, record pending cleanup and return
after the retain-until time.

## 3. Empty and Delete the Destination Bucket

1. Open `cloudadhar-s3-day11-copy-<unique-suffix>`.
2. Turn **Show versions** on.
3. Permanently delete all data versions and delete markers.
4. Abort any incomplete multipart uploads.
5. Confirm the bucket is empty and delete it.

## 4. Empty and Delete the Source Bucket

1. Remove any remaining controlled test policy text.
2. Delete the lifecycle rule if the bucket will not be deleted immediately.
3. Turn **Show versions** on.
4. Permanently delete all current and noncurrent versions and delete markers.
5. Abort incomplete multipart uploads.
6. Confirm the bucket is empty and delete it.

Deleting only the visible current objects is insufficient in a versioned
bucket.

## 5. Remove the KMS Key Safely

Only after the destination bucket and every SSE-KMS object are gone:

1. Open **KMS -> Customer managed keys**.
2. Select `alias/cloudadhar-s3-day11`.
3. Confirm no non-lab resource uses the key.
4. Disable it or schedule deletion according to the training account policy.
5. Use the minimum approved waiting period only when the account owner permits
   scheduled deletion.

KMS keys cannot be deleted immediately. Scheduling deletion is destructive;
never schedule a shared or production key.

## 6. Secure and Delete the Optional Website Bucket

1. Delete its public-read bucket policy.
2. Restore all four bucket-level BPA controls.
3. Restore all four account-level BPA controls.
4. Disable static website hosting.
5. Confirm the endpoint no longer serves the page publicly.
6. Turn **Show versions** on and permanently delete every version and delete
   marker.
7. Delete only the dedicated website bucket.

Do this immediately after evidence, before other Day 12 cleanup.

## 7. Stop Day 12 Replication and Acceleration

1. Open the Day 12 source bucket's **Management -> Replication rules**.
2. Disable or delete `srr-prefix-rule` and `crr-prefix-rule`.
3. Open **Properties -> Transfer acceleration** and disable or suspend it.
4. Delete `abort-incomplete-multipart-uploads` from Lifecycle rules.

Deleting replication rules does not delete replicas already stored.

## 8. Empty and Delete the Day 12 Buckets

Turn **Show versions** on and permanently delete all versions and delete
markers. Abort incomplete multipart uploads. Empty and delete:

1. `cloudadhar-day12-rep-source...`
2. `cloudadhar-day12-srr-dest...`
3. `cloudadhar-day12-crr-dest...`

Delete only the full account-specific bucket names created for the lab.

## 9. Delete the Generated Replication Role

1. Open **IAM -> Roles**.
2. Locate the S3 replication role generated specifically for the Day 12 source
   bucket.
3. Confirm no remaining replication rule uses it.
4. Delete only that lab-generated role.

Preserve shared VPCs, EFS, EC2 Security Groups, unrelated buckets, and shared
IAM roles. The Day 12 EFS, FSx, and hybrid-service tasks are reviews, not new
deployments.

## 10. Complete Compliance Cleanup After Expiry

If a protected Compliance-mode version remains:

1. Record the bucket, object version, and retain-until time in pending cleanup.
2. Return only after retention expires.
3. Confirm every Legal Hold is off.
4. Turn **Show versions** on and permanently delete the remaining versions and
   delete markers.
5. Delete the Object Lock bucket.

Do not attempt to bypass or shorten Compliance retention.

## Final Check

- [ ] No Day 11 or Day 12 disposable S3 bucket remains, except documented
      active Compliance retention.
- [ ] No current or noncurrent training object remains.
- [ ] No delete marker remains.
- [ ] No Legal Hold or retention-protected version remains.
- [ ] No incomplete multipart upload remains.
- [ ] No public bucket policy remains.
- [ ] All four account-level BPA controls remain on.
- [ ] No replication rule or lab-generated replication role remains.
- [ ] Transfer Acceleration is disabled.
- [ ] No incomplete-multipart lifecycle rule remains.
- [ ] No FSx, DataSync, Storage Gateway, Transfer Family, or duplicate EFS
      resource was created.
- [ ] The lab-only KMS key is disabled or scheduled according to policy.
- [ ] The bucket list and correct AWS account were checked.
- [ ] Billing and Cost Management will be reviewed after usage data arrives.

S3 storage, versions, incomplete multipart parts, retrieval, requests, data
transfer, and KMS can continue to create charges until dependencies are
removed.
