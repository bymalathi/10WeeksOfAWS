# CloudAdhar x TrainWithShubham

## AWS Zero To Hero — Day 11 S3 Sample Files

All files in this package contain synthetic training data. They are safe for the Day 11 Amazon S3 practical and must not be replaced with personal, customer or production data.

## Upload map

| Local file | S3 object key | Storage class | Practical |
|---|---|---|---|
| `documents/class-notes.txt` | `documents/class-notes.txt` | S3 Standard | Basic upload and metadata |
| `documents/private-report.txt` | `documents/private-report.txt` | S3 Standard | Private access, copy and presigned URL |
| `versions/v1/version-demo.txt` | `versions/version-demo.txt` | S3 Standard | Upload first |
| `versions/v2/version-demo.txt` | `versions/version-demo.txt` | S3 Standard | Upload second to create a new version |
| `logs/application.log` | `logs/application.log` | S3 Standard | Lifecycle prefix demonstration |
| `storage/standard-demo.txt` | `storage/standard-demo.txt` | S3 Standard | Storage-class comparison |
| `storage/intelligent-tiering-demo.txt` | `storage/intelligent-tiering-demo.txt` | S3 Intelligent-Tiering | Auto-tiering explanation |
| `presigned/presigned-demo.txt` | `presigned/presigned-demo.txt` | S3 Standard | Short-lived presigned GET URL |
| `website/index.html` | `website/index.html` | S3 Standard | Private HTML preview |
| `lock/retention-demo.txt` | `lock/retention-demo.txt` | S3 Standard | Object Lock Legal Hold |

## Versioning sequence

1. Open the source bucket and enter the `versions/` prefix.
2. Upload `versions/v1/version-demo.txt`.
3. Upload `versions/v2/version-demo.txt` to the same S3 prefix.
4. Both local files have the same basename, so the S3 object key is `versions/version-demo.txt` for both uploads.
5. Turn on **Show versions** and confirm two version IDs.
6. Delete the current object normally, then remove only the delete marker to recover it.

## Destination copy

Copy this source object:

```text
documents/private-report.txt
```

Into the destination key:

```text
copied/private-report.txt
```

The `copied/` prefix is generated during the practical; it is intentionally not included as a preloaded sample folder.

## Safety

- Keep Block Public Access enabled.
- Keep ACLs disabled and Bucket owner enforced.
- Do not expose a generated presigned URL.
- Use Legal Hold only on the dedicated Object Lock bucket.
- Delete all object versions and delete markers after class.
