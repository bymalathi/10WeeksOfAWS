# Week 5 Quick Revision

Use the Day 10 Student Guide for the full 30-question Mini-Mock. This page is a
fast decision review, not a copy of the mock.

## Recall

1. Launch Template defines how instances are built; ASG defines how many and
   where.
2. Minimum is the floor, desired is the current target, and maximum is the
   normal scaling ceiling.
3. Target tracking maintains a metric near a target; step scaling reacts to
   breach magnitude.
4. Scheduled scaling fits known events; predictive scaling fits recurring
   historical patterns.
5. Grace period protects initialization from premature health replacement;
   warmup delays use of new metrics.
6. EC2 health detects infrastructure failure; ELB health detects application
   endpoint failure.
7. A Launch Template change does not update existing instances by itself.
8. Instance Refresh rolls a fleet to the desired configuration.
9. ALB is Layer 7, NLB is Layer 4, and GWLB inserts compatible appliances.
10. ALB rule evaluation is ordered; the first matching non-default rule wins.
11. Weighted results are probabilistic and require an adequate sample.
12. Draining stops new requests while existing connections may finish.
13. GWLB uses GENEVE UDP `6081` and requires symmetric routing.

## Decision Table

| Requirement | Best direction |
|---|---|
| Repeatable modern EC2 definition | Launch Template with a tested version |
| Maintain average CPU near a target | Target tracking |
| Different scale amounts at thresholds | Step scaling |
| Known business-hours capacity | Scheduled scaling |
| Repeated daily demand | Predictive plus dynamic scaling |
| Slow initialization | Golden AMI and possibly a warm pool |
| Application fails but EC2 runs | ELB health checks |
| Gradual AMI rollout | Instance Refresh |
| Interruptible cost-sensitive fleet | Mixed Instances with diversified Spot |
| HTTP host/path/header/query routing | ALB |
| Static zonal IP or UDP | NLB |
| TLS pass-through | NLB TCP `443` |
| Transparent firewall fleet | GWLB |
| Blue/Green HTTP percentage | ALB weighted target groups |
| Graceful target removal | Deregistration delay |

## Important Traps

- Do not use legacy Launch Configurations for a new design.
- Updating a Launch Template default version does not replace running instances.
- Do not expose backend HTTP to the internet; source it from the LB SG.
- An `Unused` target can indicate an AZ or listener-association mismatch.
- Target-tracking scale-in is intentionally slower than scale-out.
- Do not expect a small weighted sample to exactly match `80/20`.
- An unhealthy weighted group does not automatically transfer its weight.
- Stickiness can hide poor session-state design and create imbalance.
- NLB cannot route by Host or path; ALB cannot serve arbitrary UDP.
- A TLS listener terminates TLS; TCP `443` provides pass-through.
- Do not use nginx as a GWLB appliance demonstration.
- Manual instance termination does not reduce desired capacity.

## Scenarios

### Scenario 1

CPU remains high, but no instance launches. Check that the policy is enabled,
the managed high alarm has enough datapoints, maximum capacity is not reached,
and the ASG Activity history has no launch failure.

### Scenario 2

The target is `Unused`. Confirm the target's AZ is enabled on the load balancer
and its target group is referenced by a listener rule.

### Scenario 3

A new AMI must roll out without replacing the whole fleet at once. Create and
test a Launch Template version, update desired configuration, then run Instance
Refresh with healthy-capacity safeguards and rollback.

### Scenario 4

One ALB must serve `api.example.com` and `/shop/*`. Use ordered host and path
rules, ensuring a broad low-number rule does not shadow a specific rule.

### Scenario 5

A partner requires fixed public IP allowlisting for a TCP service. Use an
internet-facing NLB with one EIP per enabled AZ when appropriate.

### Scenario 6

Traffic must pass transparently through a third-party firewall fleet. Use GWLB,
compatible GENEVE appliance targets, endpoints, and symmetric route design.

## Final Check

- [ ] I can explain Launch Template, ASG, target group, ALB, and scaling policy.
- [ ] I can choose a scaling method from the workload signal.
- [ ] I can distinguish grace period, warmup, lifecycle hook, and draining.
- [ ] I can explain self-healing and Instance Refresh.
- [ ] I can choose ALB, NLB, or GWLB from hard requirements.
- [ ] I can explain weighted routing and both stickiness types.
- [ ] I can troubleshoot listener, rule, AZ, target, and application failures.
- [ ] I know every billable Week 5 resource that must be removed.
