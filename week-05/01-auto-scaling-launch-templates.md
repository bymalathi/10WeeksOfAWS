# Auto Scaling and Launch Templates

## Core Model

| Component | Responsibility |
|---|---|
| Launch Template | Defines how an EC2 instance is built |
| Auto Scaling group | Defines how many instances should exist and where |
| Target group | Measures application health and receives traffic |
| Application Load Balancer | Sends requests only to healthy targets |
| Scaling policy | Changes desired capacity from a metric or schedule |

Use Launch Templates for new designs. They support versions and current EC2
features; Launch Configurations are legacy. Treat AMI, instance type, User Data,
storage, IAM, Security Group, and metadata changes as versioned deployments.
Pin a tested version when repeatability matters, keep a known-good version for
rollback, and confirm which version the ASG actually references.

## Capacity, Availability, and Health

| Setting | Meaning | Classroom value |
|---|---|---:|
| Minimum | Lowest capacity the ASG maintains | 1 |
| Desired | Capacity the ASG currently attempts to maintain | 1 initially |
| Maximum | Normal scaling ceiling | 2 |

Span at least two Availability Zones. During replacement or AZ rebalancing,
Auto Scaling may briefly launch extra capacity before terminating old capacity
to protect availability.

- EC2 health checks detect instance and system impairment.
- ELB health checks detect a failed application endpoint on a running instance.
- The grace period allows boot, User Data, application start, and initial health
  checks to finish.
- Instance warmup delays use of a new instance's metrics until it stabilizes.
- The ALB and ASG must use compatible VPCs, subnets, and enabled AZs.
- The backend Security Group should accept HTTP from the ALB Security Group,
  not from the internet.

## Scaling Policy Selection

| Workload signal | Policy | Why |
|---|---|---|
| Maintain a utilization or throughput target | Target tracking | Manages capacity around a target and creates its alarms |
| Different actions for small and large breaches | Step scaling | Adjustment follows alarm-breach magnitude |
| Known business event | Scheduled scaling | Changes capacity at a defined time |
| Repeated daily or weekly pattern | Predictive plus dynamic scaling | Forecasts the baseline; dynamic scaling handles surprises |

Choose a metric that changes with fleet capacity. Average CPU works when work
is distributed across instances; ALB request count per target often fits web
traffic. Do not manually edit target-tracking alarms. Scale-out favors
availability, while scale-in is deliberately conservative.

## Lifecycle and Fleet Controls

- A launch lifecycle hook pauses at `Pending:Wait` for initialization or
  validation. A termination hook pauses at `Terminating:Wait` for draining,
  log shipping, or graceful shutdown. Send heartbeats and always complete or
  abandon the action before timeout.
- A warm pool keeps initialized instances stopped, running, or hibernated.
  Use one only when measured startup latency justifies its cost and complexity.
- A termination policy selects an eligible scale-in victim after Auto Scaling
  first considers Availability Zone balance.
- Scale-in protection temporarily protects selected instances from normal
  scale-in.
- An instance maintenance policy controls healthy capacity during replacement.
- Instance Refresh gradually moves a fleet to a new Launch Template version;
  use appropriate healthy percentages, warmup, checkpoints, and rollback.

## Mixed Instances Policy

A Mixed Instances group can combine compatible instance types, On-Demand
baseline capacity, and Spot burst capacity. Diversify instance types and AZs,
prefer capacity-aware Spot allocation, enable Capacity Rebalancing when useful,
and keep application state outside instances. Spot is appropriate only when the
workload tolerates interruption.

## Exam Cues

| Requirement | Preferred direction |
|---|---|
| Versioned EC2 launch settings | Launch Template |
| Maintain average utilization | Target tracking |
| Known time-based peak | Scheduled scaling |
| Slow first boot | Golden AMI and possibly a warm pool |
| Running EC2 but failed application | ELB health checks |
| Gradual AMI rollout | Instance Refresh |
| Flexible, interruptible fleet | Diversified Mixed Instances group with Spot |

## Official References

- [Launch Templates](https://docs.aws.amazon.com/autoscaling/ec2/userguide/launch-templates.html)
- [Auto Scaling groups](https://docs.aws.amazon.com/autoscaling/ec2/userguide/auto-scaling-groups.html)
- [Scaling methods](https://docs.aws.amazon.com/autoscaling/ec2/userguide/scaling-overview.html)
- [Target tracking](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-scaling-target-tracking.html)
- [Lifecycle hooks](https://docs.aws.amazon.com/autoscaling/ec2/userguide/lifecycle-hooks.html)
- [Instance Refresh](https://docs.aws.amazon.com/autoscaling/ec2/userguide/asg-instance-refresh.html)
- [Mixed Instances groups](https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-mixed-instances-groups.html)
