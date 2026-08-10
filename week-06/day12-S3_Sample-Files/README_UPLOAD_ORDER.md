# AWS Zero To Hero - Day 12 Sample Files

CloudAdhar x TrainWithShubham

Topic: Amazon S3 Replication, Transfer and Hybrid Storage

All files in this pack contain synthetic training data only.

## Upload order

1. Before creating replication rules, upload `01-before-rule/before-rule.txt` twice: once with the key `srr/before-rule.txt` and once with the key `crr/before-rule.txt`.
2. Create the SRR rule with prefix `srr/` and the CRR rule with prefix `crr/`.
3. Upload `02-srr/version-1/cloudadhar-srr-demo.txt` to the source bucket with the key `srr/cloudadhar-srr-demo.txt`.
4. Upload `03-crr/version-1/cloudadhar-crr-demo.txt` to the source bucket with the key `crr/cloudadhar-crr-demo.txt`.
5. Verify replication status and destination objects.
6. Upload `02-srr/version-2/cloudadhar-srr-demo.txt` using the same key `srr/cloudadhar-srr-demo.txt`.
7. Upload `03-crr/version-2/cloudadhar-crr-demo.txt` using the same key `crr/cloudadhar-crr-demo.txt`.
8. Turn on Show versions in the source and destination buckets.
9. Upload `04-filter-control/no-replication-demo.txt` with the key `other/no-replication-demo.txt`. It should not match either replication rule.
10. Use the remaining files for Transfer Acceleration, multipart-upload and service-selection explanations.

## Expected results

- `srr/before-rule.txt` and `crr/before-rule.txt` do not automatically appear in either destination.
- `srr/cloudadhar-srr-demo.txt` appears only in the Mumbai SRR destination.
- `crr/cloudadhar-crr-demo.txt` appears only in the Tokyo CRR destination.
- Both versions of the SRR and CRR demonstration objects are replicated.
- `other/no-replication-demo.txt` remains only in the source bucket.

## Important

The included multipart file is intentionally small. It is suitable for explaining object content and lifecycle cleanup, but it does not prove that the S3 client used multipart upload. A real multipart test requires a sufficiently large object or an explicit CLI/SDK multipart operation.
