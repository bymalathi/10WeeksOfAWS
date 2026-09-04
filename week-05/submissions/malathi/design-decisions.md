# Week 5 Design Decisions

---

# Week 5 - Day 9: ALB-Backed Auto Scaling

## Decision Table

| Decision                          | Classroom Choice                    | Production Choice                                                                     | Reason                                                                                                                                          |
| --------------------------------- | ----------------------------------- | ------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **AWS Region**                    | `us-west-2` (Oregon)                | Region selected based on business, latency, compliance, and availability requirements | The lab was performed in `us-west-2` for the training environment. Production regions should be selected according to application requirements. |
| **Launch Template**               | `cloudadhar-day9-lt`                | Version-controlled Launch Template                                                    | A validated Launch Template provides a consistent configuration whenever the Auto Scaling Group launches a new instance.                        |
| **Launch Template Version**       | Version 2                           | Approved/stable version                                                               | Using a known working version makes deployments predictable and provides a clear rollback point.                                                |
| **Load Balancer**                 | Application Load Balancer           | Application Load Balancer                                                             | ALB provides Layer 7 HTTP/HTTPS routing and integrates with Auto Scaling and target health checks.                                              |
| **Target Group**                  | `cloudadhar-day9-tg`                | Dedicated target groups based on application architecture                             | Target groups allow the ALB to monitor backend instances and route traffic only to healthy targets.                                             |
| **Listener**                      | HTTP `80`                           | HTTPS `443`                                                                           | The classroom lab used HTTP for simplicity. Production applications should normally terminate TLS using an ACM certificate.                     |
| **Auto Scaling Group**            | `cloudadhar-day9-asg`               | Multiple instances across multiple Availability Zones                                 | Multiple instances improve availability and allow the application to continue operating when an individual instance fails.                      |
| **Scaling Policy**                | Target tracking                     | CPU, request count, or custom CloudWatch metrics depending on workload                | CPU is useful for the lab, but production workloads may scale more accurately using request-based or application-specific metrics.              |
| **Scaling Target**                | Average CPU `50%`                   | Workload-specific threshold                                                           | The 50% CPU target provides a simple demonstration of automatic scale-out and scale-in behavior.                                                |
| **Health Checks**                 | EC2 + ELB                           | EC2 + ELB                                                                             | EC2 health checks detect instance-level failures, while ELB health checks verify that the application is responding correctly.                  |
| **Operating System / Web Server** | Amazon Linux + NGINX                | Hardened application image                                                            | NGINX provided a simple HTTP workload that could be monitored through the ALB.                                                                  |
| **Instance Metadata**             | IMDSv2                              | IMDSv2 required                                                                       | IMDSv2 provides stronger protection against metadata-related security risks than unrestricted IMDSv1 access.                                    |
| **Storage**                       | Encrypted gp3                       | Encrypted EBS volumes using an appropriate volume type                                | Encryption protects data at rest, while gp3 provides configurable performance and is suitable for many general workloads.                       |
| **Instance Administration**       | AWS Systems Manager Session Manager | Session Manager / controlled administrative access                                    | Session Manager avoids the need for direct SSH access and provides a more controlled administration approach.                                   |

---

# Failure Review - Day 9

## 1. One Application Instance Becomes Unhealthy

The ALB continuously performs health checks against registered targets.

If an instance fails the configured health check, the ALB marks the target as **Unhealthy** and stops sending normal traffic to it.

When the Auto Scaling Group uses ELB health checks, the ASG can also identify the unhealthy instance and replace it.

---

## 2. Actual Self-Healing Test

The lab demonstrated Auto Scaling self-healing by terminating an instance:

* **Terminated instance:** `i-0ee2a22f694d8eda2`
* **Auto Scaling Group:** `cloudadhar-day9-asg`
* **Replacement instance:** `i-0583d46bd934633bd`
* **Replacement status:** InService / Healthy

This demonstrated an important Auto Scaling concept:

> **Self-healing** means the Auto Scaling Group maintains the configured desired capacity by replacing failed or unhealthy instances.

The failure-and-replacement flow was:

```text
EC2 Instance Failure
        |
        v
Auto Scaling detects reduced capacity
        |
        v
Replacement EC2 launched
        |
        v
Instance passes health checks
        |
        v
Instance becomes InService
```

---

## 3. A New Instance Fails Its ALB Health Check

If a newly launched instance does not successfully serve the expected application response, the ALB keeps the instance out of normal traffic.

If the instance remains unhealthy, the Auto Scaling Group can replace it.

This helps prevent users from being routed to an incorrectly configured or failed application instance.

---

## 4. High CPU Causes a Scale-Out Event

When average CPU utilization reaches the configured target of **50%**, the target-tracking policy can increase the number of instances.

The new instance is launched using the configured Launch Template.

After the instance becomes healthy and is registered with the target group, the ALB can begin sending traffic to it.

```text
High CPU
   |
   v
Target Tracking Policy
   |
   v
Scale Out
   |
   v
New EC2 Instance
   |
   v
Health Check Passes
   |
   v
ALB Sends Traffic
```

---

## 5. Traffic Decreases and a Scale-In Event Occurs

When demand decreases, the Auto Scaling Group can reduce the number of running instances according to its configured capacity and scaling policy.

Before an instance is removed from service, the load balancer can use **deregistration delay** to allow existing connections to complete.

This helps reduce disruption during scale-in events.

---

## 6. A Bad Launch Template Version Is Used

If a Launch Template version contains an incorrect AMI, application configuration, security setting, or startup configuration, newly launched instances may fail.

Using versioned Launch Templates makes it easier to identify a known-good configuration and roll the Auto Scaling Group back to a stable version.

The lab used:

* **Launch Template:** `cloudadhar-day9-lt`
* **Tested Version:** `2`

---

## 7. Availability Zone Failure

In production, an Auto Scaling Group should distribute instances across multiple Availability Zones.

If one AZ becomes unavailable, instances in the remaining AZs can continue serving traffic through the ALB.

The Auto Scaling Group can also launch replacement capacity as infrastructure becomes available again.

This improves application availability and fault tolerance.

---

# Key Learning - Day 9

Day 9 demonstrated how an **Application Load Balancer and Auto Scaling Group work together**.

The important traffic flow was:

```text
Client
   |
   v
ALB
   |
   v
Target Group
   |
   v
Healthy EC2 Instances
```

The self-healing flow was:

```text
Unhealthy / Failed EC2
        |
        v
ALB / ASG detects failure
        |
        v
Instance replaced
        |
        v
New instance becomes Healthy
```

The most important practical lesson was the **self-healing test**, where terminating an EC2 instance resulted in Auto Scaling launching a replacement instance automatically.

---

# Week 5 - Day 10: ALB Blue/Green Routing and NLB

## Decision Table

| Decision                 | Classroom Choice                              | Production Choice                                   | Reason                                                                                                                |
| ------------------------ | --------------------------------------------- | --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| **Deployment Strategy**  | Manual Blue/Green                             | Automated Blue/Green or Canary deployment           | Automated progressive deployments reduce deployment risk and make rollback easier.                                    |
| **Application Versions** | Blue and Green NGINX targets                  | Separate application environments / target groups   | Separating versions allows the new version to be tested before directing all traffic to it.                           |
| **Traffic Shifting**     | Manual weighted routing                       | Automated gradual traffic shifting                  | Gradual traffic shifting allows the new version to be validated with limited traffic before full rollout.             |
| **Routing Method**       | Path-based routing                            | Host-based and/or path-based routing                | ALB Layer 7 routing allows requests to be directed to different target groups based on request information.           |
| **Weighted Routing**     | Manual traffic distribution                   | Automated progressive release                       | Weighted routing provides a controlled way to move traffic from Blue to Green.                                        |
| **Target Health Checks** | `/`                                           | Application-specific health endpoint                | Health checks allow the load balancer to identify unhealthy targets and remove them from normal traffic distribution. |
| **Stickiness**           | Enabled for the lab                           | Enabled only when session affinity is required      | Stickiness can keep a client associated with the same backend target when session persistence is required.            |
| **Connection Draining**  | ALB deregistration delay                      | Tuned according to application behavior             | Existing connections can be allowed to complete before a target is fully removed from service.                        |
| **Load Balancer**        | ALB + NLB                                     | ALB or NLB according to application requirements    | ALB is designed for Layer 7 HTTP/HTTPS routing, while NLB provides Layer 4 network load balancing.                    |
| **NLB Listener**         | TCP                                           | TCP/TLS based on application requirements           | The Day 10 lab demonstrated NLB Layer 4 routing using TCP.                                                            |
| **NLB Target Group**     | TCP target group                              | Protocol selected according to application traffic  | The target group protocol should match the traffic pattern supported by the workload.                                 |
| **Backend Instances**    | Blue and Green EC2/NGINX targets              | Multiple targets across multiple Availability Zones | Multiple targets improve availability and reduce the impact of individual instance failures.                          |
| **TLS**                  | HTTP for the classroom demonstration          | HTTPS/TLS using ACM where encryption is required    | Production applications should protect client traffic with TLS.                                                       |
| **DNS**                  | Load balancer DNS endpoint for lab validation | Route 53 Alias record                               | Route 53 provides a stable application DNS name without requiring users to know the load balancer endpoint.           |

---

# Failure Review - Day 10

## 1. Blue Targets Become Unhealthy

The ALB health check detects when a Blue target becomes unhealthy.

The unhealthy target is removed from normal traffic distribution while healthy targets continue serving requests.

This prevents an unhealthy Blue instance from receiving new application traffic.

---

## 2. Green Targets Become Unhealthy During a Weighted Release

During a Blue/Green release, only a portion of traffic may initially be sent to Green.

If Green becomes unhealthy, ALB health checks identify the affected target and stop routing normal traffic to it.

Traffic can continue through healthy targets while the Green environment is investigated.

### Actual Green Target Health Test

The lab demonstrated this behavior by intentionally stopping NGINX on the Green EC2 instance:

```bash
sudo systemctl stop nginx
```

The ALB health check then detected the failure and the Green target became **Unhealthy**.

```text
Green EC2
    |
    | NGINX stopped
    v
ALB health check /
    |
    v
Green target → Unhealthy
```

NGINX was then started again:

```bash
sudo systemctl start nginx
```

After successful health checks, the Green target recovered to the **Healthy** state.

This demonstrated that the ALB continuously monitors registered targets and uses health-check results when determining which targets can receive traffic.

---

## 3. Incorrect ALB Routing Rule

An incorrectly configured host-based or path-based rule can send requests to the wrong target group.

Listener rules should therefore be tested against both Blue and Green environments before increasing traffic to a new release.

For example:

```text
GET /blue
    |
    v
Blue Target Group
```

and:

```text
GET /green
    |
    v
Green Target Group
```

---

## 4. Weighted Traffic Shift

The lab demonstrated controlled traffic distribution between Blue and Green.

For example:

```text
Blue  → 80%
Green → 20%
```

If Green performs correctly, traffic can gradually be increased.

If Green has a problem, traffic can be shifted back toward Blue.

This demonstrates the basic concept of **progressive deployment**.

In the actual lab, the `/canary` rule was configured with:

```text
Blue  → 50%
Green → 50%
```

---

## 5. Connection Draining During Deployment

When a target is deregistered, the ALB can allow existing connections to complete during the configured **deregistration delay**.

This gives active connections time to finish before the target is fully removed from service.

The lab demonstrated this by deregistering the Green target and observing its **Draining** state.

This behavior helps reduce disruption during deployment, scaling, and maintenance activities.

---

## 6. NLB Target Becomes Unhealthy

The NLB performs health checks against its registered targets.

If a target fails its health check, the NLB stops sending new connections to that unhealthy target and continues using healthy targets.

This provides basic protection against sending traffic to failed backend instances.

---

## 7. NLB Requires Layer 4 Connectivity

The Day 10 lab demonstrated the difference between ALB and NLB.

The ALB works at **Layer 7**, understanding HTTP/HTTPS requests and supporting routing based on information such as the host or path.

The NLB works at **Layer 4**, forwarding network traffic such as TCP connections.

The lab therefore required an **NLB-compatible TCP target group** rather than reusing the existing HTTP ALB target groups.

---

## 8. One Availability Zone Becomes Unavailable

In a production environment, targets should be distributed across multiple Availability Zones.

If one AZ becomes unavailable, the load balancer can continue directing traffic toward healthy targets in the remaining AZs.

This improves application availability and fault tolerance.

---

# Key Learning - Day 10

Day 10 demonstrated two important AWS load-balancing concepts.

## ALB - Layer 7

```text
Client
   |
   v
Application Load Balancer
   |
   v
Listener Rules
   |
   +----> Blue Target Group
   |             |
   |             v
   |         Blue EC2
   |
   +----> Green Target Group
                 |
                 v
             Green EC2
```

The ALB is useful when an application needs:

* HTTP/HTTPS-aware routing
* Path-based or host-based routing
* Blue/Green releases
* Weighted traffic shifting
* Health checks
* Target group stickiness
* Connection draining

---

## NLB - Layer 4

```text
Client
   |
   v
Network Load Balancer
   |
   v
TCP Listener
   |
   v
TCP Target Group
   |
   +----> Blue EC2
   |
   +----> Green EC2
```

The NLB is appropriate when an application requires Layer 4 network load balancing for traffic such as TCP/TLS connections.

---

# Week 5 Overall Learning

Day 9 and Day 10 together demonstrated how AWS can provide both **scalability and high availability**.

## Day 9 — ALB + Auto Scaling

* Automatically adds capacity when demand increases
* Removes or replaces unhealthy instances
* Launches replacement instances
* Uses health checks to protect application traffic
* Maintains desired capacity during instance failures
* Demonstrates automatic self-healing

The key flow was:

```text
Client
  |
  v
ALB
  |
  v
Target Group
  |
  v
Healthy EC2 Instances
  |
  v
Auto Scaling Group
  |
  +----> Scale Out
  |
  +----> Scale In
  |
  +----> Replace Failed Instances
```

---

## Day 10 — ALB Blue/Green + NLB

* Separates Blue and Green application versions
* Routes traffic using ALB listener rules
* Demonstrates path-based routing
* Demonstrates weighted traffic distribution
* Demonstrates canary-style testing
* Uses health checks to protect users from unhealthy targets
* Demonstrates target group stickiness
* Demonstrates target deregistration and connection draining
* Demonstrates NLB Layer 4 TCP load balancing
* Verifies NLB target health
* Reuses the same EC2 instances behind the NLB

---

# Overall Architecture Concept

Day 9 and Day 10 can be viewed as two complementary capabilities.

### Application Traffic and Scaling

```text
Users
  |
  v
ALB
  |
  v
Routing / Traffic Distribution
  |
  v
Target Groups
  |
  v
Healthy EC2 Instances
  |
  v
Auto Scaling
  |
  +----> Automatic replacement
  |
  +----> Capacity adjustment
```

### Layer 4 Network Traffic

```text
Users / Clients
      |
      v
     NLB
      |
      v
 TCP Listener
      |
      v
 TCP Target Group
      |
      v
Healthy EC2 Targets
```

---

# Final Week 5 Learning

The key production lesson from Week 5 is that **load balancing, health checks, Auto Scaling, and controlled deployments work together** to build more resilient applications.

```text
                    WEEK 5
                       |
        +--------------+--------------+
        |                             |
       Day 9                        Day 10
        |                             |
   ALB + Auto Scaling        ALB Blue/Green + NLB
        |                             |
        v                             v
 Scalability +                 Traffic Control +
 Self-Healing                  Layer 4 Networking
        |                             |
        +--------------+--------------+
                       |
                       v
              High Availability
              + Resilience
              + Controlled Releases
```

The biggest practical lessons from the week were:

1. **ALB** provides intelligent Layer 7 application routing.
2. **NLB** provides Layer 4 network load balancing.
3. **Auto Scaling** maintains application capacity and can replace failed instances.
4. **Health checks** prevent unhealthy targets from receiving normal traffic.
5. **Weighted routing** allows controlled traffic shifting between application versions.
6. **Stickiness** can provide session persistence when required.
7. **Connection draining** helps reduce disruption when targets are removed.
8. **Multiple Availability Zones** improve availability and fault tolerance.

Together, these capabilities provide a foundation for designing AWS applications that can **scale with demand, tolerate individual failures, and support safer application deployments**.
