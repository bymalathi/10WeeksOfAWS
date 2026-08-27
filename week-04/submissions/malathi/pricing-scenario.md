# Week 4 – Pricing Scenarios

## Pricing Scenarios

| Requirement | Recommended Option | Reason |
|---|---|---|
| A new API has unpredictable demand. | **On-Demand Instances** | Suitable for workloads where usage is uncertain because there is no long-term commitment. |
| A checkpointed rendering fleet can tolerate interruptions. | **Spot Instances** | Provides substantial cost savings for workloads that can handle interruption and resume from checkpoints. |
| A company has steady compute usage across services. | **Compute Savings Plans** | Provides savings for consistent compute usage while offering flexibility across EC2, Fargate, and Lambda. |
| Licensed software requires visibility into a physical server. | **Dedicated Hosts** | Provides a dedicated physical server, which can help meet licensing, compliance, and regulatory requirements. |
| A stable EC2 fleet uses the same instance family in one Region. | **EC2 Instance Savings Plans** | Provides savings for predictable EC2 usage when the workload remains within a specific instance family and Region. |

## Summary

| Pricing Option | Best For |
|---|---|
| **On-Demand Instances** | Short-term, unpredictable, or variable workloads |
| **Spot Instances** | Fault-tolerant workloads that can tolerate interruption |
| **Compute Savings Plans** | Consistent compute usage across EC2, Fargate, and Lambda |
| **Dedicated Hosts** | Physical-server licensing and compliance requirements |
| **EC2 Instance Savings Plans** | Predictable EC2 workloads using a consistent instance family in one Region |