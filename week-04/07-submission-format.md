# Week 4 Submission Format

```text
week-04/submissions/<github-username>/
├── README.md
├── architecture.png
└── evidence/
    ├── day7-ec2/
    ├── day8-storage/
    └── cleanup/
```

## README Template

```markdown
# Week 4 - EC2 Essentials, EBS, and Pricing

## Learner
- Name:
- GitHub:
- LinkedIn:
- Region:

## Day 7
- Instance selection:
- User Data result:
- IMDSv1 expected-deny:
- IMDSv2 result:
- Golden AMI validation:
- Pricing decisions:

## Day 8
- Instance and volume AZ:
- Filesystem and mount:
- Stop/start persistence:
- Resize and XFS growth:
- Snapshot recovery:
- Cross-Region encrypted copy:
- DLM policy or review:
- EFS clients and shared-file proof:
- Storage decisions:
- Placement decisions:

## Architecture Decision
Write 200-300 words.

## Cleanup
- Instances:
- Volumes:
- EFS:
- AMIs:
- Snapshots:
- DLM policies:
- Fast Snapshot Restore:
- Placement groups:
- Regions checked:

## Reflection
1. What EC2 decision mattered most?
2. What makes the formatting step dangerous?
3. What would you automate in production?
```

## Evidence Checklist

- [ ] Builder role and IMDSv2 required
- [ ] nginx and cloud-init success
- [ ] Tokenless `401` and token-based metadata success
- [ ] Golden AMI v2 available
- [ ] Test instance serves nginx without User Data
- [ ] Same-AZ EC2 and EBS
- [ ] `lsblk`, XFS, UUID mount, and persistence
- [ ] EBS resize from 2 GiB to 4 GiB and XFS growth
- [ ] Completed snapshot and recovered file
- [ ] Post-snapshot data is absent from the restored point-in-time copy
- [ ] Encrypted snapshot copy completed or was verified in Sydney
- [ ] DLM targets only the tagged training volume
- [ ] Optional FSR, Multi-Attach, and Instance Store resources were cleaned up
- [ ] EFS mount targets and TCP `2049` security-group rule
- [ ] Two EC2 hostnames mounted the same EFS ID
- [ ] Each EFS client read a file written by the other client
- [ ] Persistent EFS mount validation
- [ ] Placement-group strategies
- [ ] Architecture, cleanup, and LinkedIn link

Mask account IDs, ARNs, IPs, instance/volume/AMI/snapshot IDs, metadata tokens,
credentials, private keys, billing information, and organization URLs.
