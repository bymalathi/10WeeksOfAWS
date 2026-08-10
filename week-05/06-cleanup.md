# Week 5 Cleanup

Capture sanitized evidence first. Check `ap-south-1` and every other Region
used.

## Day 9

1. Stop `stress-ng` on every instance and confirm no process remains.
2. Delete optional schedules, predictive policies, lifecycle hooks, warm pools,
   instance refreshes, and Mixed Instances experiments.
3. Set ASG minimum, desired, and maximum to zero, or delete the ASG.
4. Wait for managed instances to terminate and targets to deregister.
5. Delete `cloudadhar-day9-alb`.
6. Delete `cloudadhar-day9-tg`.
7. Delete `cloudadhar-day9-asg` if it was retained at zero.
8. Delete `cloudadhar-day9-lt` and its versions when no longer needed.
9. Delete Day 9 Security Groups after dependencies disappear.
10. Remove lab-only alarms, notifications, logs, volumes, snapshots, roles, and
    instance profiles when unused.

## Day 10

1. Remove optional UDP and TLS listeners, services, rules, and target groups.
2. Delete `cloudadhar-day10-nlb` and release any Elastic IP addresses.
3. Delete non-default ALB rules and `cloudadhar-day10-alb`.
4. Deregister targets when needed and delete all Day 10 target groups.
5. Terminate `cloudadhar-day10-blue-ec2` and
   `cloudadhar-day10-green-ec2`.
6. Delete Day 10 Security Groups after dependencies disappear.
7. Delete temporary cookies, certificates, and test files if an instance is
   intentionally retained.
8. Remove lab-only access logs and CloudWatch log groups when no longer needed.

## Final Check

- [ ] No Week 5 Auto Scaling group, warm pool, or scaling schedule remains.
- [ ] No Week 5 load balancer or target group remains.
- [ ] No Week 5 EC2 instance is running or stopped.
- [ ] No allocated Elastic IP or unintended public IPv4 remains.
- [ ] No Week 5 EBS volume or snapshot remains.
- [ ] No lab-only alarm, log group, Security Group, role, or profile remains.
- [ ] Optional TLS, UDP, lifecycle, Spot, and GWLB review resources are gone.
- [ ] Every Region used was checked.

Load balancers, public IPv4 addresses, Elastic IPs, EBS, snapshots, warm pools,
logs, and data processing can create charges. Review billing later because
usage data can arrive after deletion.
