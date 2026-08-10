# Week 5 Submission Format

Create this folder in your fork:

```text
week-05/submissions/<github-username>/
├── README.md
├── architecture.png
└── evidence/
    ├── day9-auto-scaling/
    ├── day10-load-balancing/
    └── cleanup/
```

## README Template

```markdown
# Week 5 - Auto Scaling and Elastic Load Balancing

## Learner
- Name:
- GitHub:
- LinkedIn:
- Region:

## Day 9
- Launch Template version and security choices:
- ASG min/desired/max and AZs:
- Target tracking metric and target:
- Scale-out result:
- Scale-in result:
- Self-healing result:
- Troubleshooting lesson:

## Day 10
- Blue and Green target design:
- Host and path routing:
- Weighted release sample:
- Stickiness result:
- Health and draining result:
- NLB TCP result:
- ALB/NLB/GWLB decisions:

## Architecture Decision
Write 250-400 words.

## Cleanup
- Auto Scaling resources:
- Load balancers and target groups:
- Instances and storage:
- EIPs and public IPv4:
- Optional resources:
- Regions checked:

## Reflection
1. Which metric best represents demand for this application?
2. How do grace period, warmup, health checks, and draining differ?
3. Which load balancer requirement was easiest to confuse, and why?
```

## Evidence Checklist

- [ ] Tested Launch Template version with encrypted gp3 and IMDSv2 required
- [ ] ASG `1/1/2`, two AZs, target group, and propagated tags
- [ ] Healthy Day 9 target and working ALB page
- [ ] High alarm, scale-out Activity, and two instance IDs
- [ ] Stopped stress, low-alarm observation, and scale-in Activity
- [ ] Controlled self-healing or replacement result
- [ ] Blue and Green targets healthy in separate AZs
- [ ] Host routing and both path-routing results
- [ ] Approximate Blue 80 / Green 20 sample and explanation
- [ ] Cookie-based stickiness observation
- [ ] Health failure, recovery, and draining observation
- [ ] Healthy NLB targets and TCP responses
- [ ] ALB/NLB/GWLB decision table and architecture diagram
- [ ] Cleanup confirmation and LinkedIn link

Mask account IDs, ARNs, resource IDs, public/private IPs, sensitive DNS names,
metadata tokens, cookies, credentials, key material, certificates, console URLs,
and billing information.
