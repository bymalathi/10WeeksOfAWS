# Week 8 Cleanup

Collect sanitized evidence first, then remove resources in dependency order.
Check both `ap-south-1` and `us-east-1`, plus global service consoles.

## Day 15 - Remove Access and DNS Dependencies

1. Return the WAF test rule from Block to Count, verify access, then delete the
   rule and learner IP set.
2. Delete Route 53 weighted, latency, simple, and failover lab records.
3. Delete Day 15 health checks after no records reference them.
4. Delete the delegated lab hosted zone if it was created only for this lab;
   remove its parent-zone delegation records afterward.
5. Remove the CloudFront custom domain and certificate association if required
   before distribution deletion.
6. Disable and delete the CloudFront distribution; wait for each state change.
7. Delete its lab-only Origin Access Control after no origin references it.
8. Delete the trusted key group, CloudFront public key, and any CloudShell
   private/public signing-key files.
9. Delete the WAF web ACL only if it was created exclusively for this lab and
   is no longer associated.
10. Empty every object version and delete marker from the Day 15 S3 bucket, then
   delete the bucket.
11. Terminate both Regional EC2 endpoints and delete their dedicated Security
    Groups after dependencies disappear.
12. Remove lab application DNS records at the authoritative provider.
13. Decide whether the ACM certificate will be retained. If deleting it, first
    confirm it is unused, delete it, and remove its validation `CNAME`. If
    retaining it, keep the validation record for managed renewal.
14. If the entire practice domain was moved from Hostinger or another registrar
    to Route 53 name servers, deliberately choose one final state:
    - retain Route 53 authoritative DNS and the required hosted zone/records;
    - restore the previous name servers only after recreating all required
      records at the previous provider; or
    - let a disposable domain expire only after disabling unintended renewal.
    Never delete the active hosted zone before changing the registrar's name
    servers, or the domain becomes unavailable.

Do not delete a shared parent hosted zone, shared certificate, production DNS
record, shared WAF ACL, default VPC, or default Security Group.

## Day 16 - Remove Restored and Backup Resources

1. Delete optional Route 53 failover records and health checks.
2. Terminate the N. Virginia restored instance and Mumbai source instance.
3. Confirm their lab-only EBS volumes and public IPv4 resources are gone.
4. In N. Virginia, delete the copied recovery point from
   `<PREFIX>-day16-dr-vault`.
5. Delete the empty destination vault.
6. In Mumbai, delete the source recovery point from
   `<PREFIX>-day16-primary-vault`.
7. Delete the empty source vault.
8. Delete optional private hosted-zone records/associations and then the zone.
9. Delete the optional S3 gateway endpoint and verify its route-table entry is
   removed.
10. Delete Day 16 Security Groups after all ENIs are gone.
11. Schedule deletion of `alias/<PREFIX>-day16-dr-backup-key`'s KMS key only
    if it was created solely for this lab and no retained recovery point or
    other resource requires it. Remove the alias as appropriate.
12. Delete lab-only AWS Backup IAM roles only after confirming no other backup
    or restore uses them.

AWS Backup recovery points can retain underlying snapshots and charges even
after EC2 instances are terminated. Inspect vaults, not just EC2.

## Final Check

- [ ] No Day 15 EC2 instance, public IPv4, EBS volume, or lab SG remains
- [ ] No Day 15 Route 53 record, health check, or unused hosted zone remains
- [ ] No CloudFront distribution, OAC policy dependency, or invalidation work remains
- [ ] No Day 15 WAF rule, IP set, or lab-only web ACL remains
- [ ] No signing private key, public key, or trusted key group remains
- [ ] No S3 object version, delete marker, or Day 15 bucket remains
- [ ] ACM certificate and validation-record retention are deliberate
- [ ] No Day 16 EC2 instance, EBS volume, public IPv4, or lab SG remains
- [ ] No source or destination recovery point remains
- [ ] Both AWS Backup vaults are empty and removed
- [ ] No optional private hosted zone, endpoint, record, or health check remains
- [ ] Lab KMS key deletion is scheduled only when safe
- [ ] Billing and Cost Explorer will be reviewed after usage arrives

Do not publish cleanup screenshots containing account IDs, ARNs, IP addresses,
hosted-zone IDs, recovery-point IDs, or billing information.
