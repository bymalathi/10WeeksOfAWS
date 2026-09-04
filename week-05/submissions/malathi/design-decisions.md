# Week 5 Design Decisions

---

# Week 5 - Day 9: ALB-Backed Auto Scaling

## Decision Table

| Decision                          | Classroom Choice                    | Production Choice                                                                     | Reason                                                                                                                                          |
| --------------------------------- | ----------------------------------- | ------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **AWS Region**                    | `us-west-2` (Oregon)                | Region selected based on business, latency, compliance, and availability requirements | The lab was performed in `us-west-2` for the training environment. Production regions should be selected according to application requirements. |
| **Launch Template**               | `cloudadhar-day9-lt`                | Version-controlled Launch Template                                                    | A validated Launch Template provides a consistent configuration whenever the Auto Scaling Group launches a new instance.                        |
| **Launch Template version**       | Version 2                           | Approved/stable version                                                               | Using a known working version makes deployments predictable and provides a clear rollback point.                                                |
| **Load balancer**                 | Application Load Balancer           | Application Load Balancer                                                             | ALB provides HTTP/HTTPS Layer 7 routing and integrates directly with Auto Scaling and target health checks.                                     |
| **Target Group**                  | `cloudadhar-day9-tg`                | Dedicated target groups based on application architecture                             | Target groups allow the ALB to monitor backend instances and route traffic only to healthy targets.                                             |
| **Listener**                      | HTTP `80`                           | HTTPS `443`                                                                           | The classroom lab used HTTP for simplicity. Production applications should normally terminate TLS using an ACM certificate.                     |
| **Auto Scaling Group**            | `cloudadhar-day9-asg`               | Multiple instances across multiple Availability Zones                                 | Multiple instances improve availability and allow the application to continue operating when an individual instance fails.                      |
| **Scaling policy**                | Target tracking                     | CPU, request count, or custom CloudWatch metrics depending on workload                | CPU is useful for the lab, but production workloads may scale more accurately using request-based or application-specific metrics.              |
| **Scaling target**                | Average CPU `50%`                   | Workload-specific threshold                                                           | The 50% CPU target provides a simple demonstration of automatic scale-out and scale-in behavior.                                                |
| **Health checks**                 | EC2 + ELB                           | EC2 + ELB                                                                             | EC2 health checks detect instance-level failures while ELB health checks verify that the application is actually responding correctly.          |
| **Operating system / web server** | Amazon Linux + NGINX                | Hardened application image                                                            | The lab used NGINX to provide a simple HTTP workload that could be monitored through the ALB.                                                   |
| **Instance metadata**             | IMDSv2                              | IMDSv2 required                                                                       | IMDSv2 improves protection against metadata-related security risks compared with allowing unrestricted IMDSv1 access.                           |
| **Storage**                       | Encrypted gp3                       | Encrypted EBS volumes using an appropriate volume type                                | Encryption protects data at rest, while gp3 provides configurable performance and is suitable for many general workloads.                       |
| **Instance administration**       | AWS Systems Manager Session Manager | Session Manager / controlled administrative access                                    | Session Manager avoids the need for direct SSH access and provides a more controlled management approach.                                       |

---

# Failure Review

### 1. One application instance becomes unhealthy

The ALB continuously performs health checks against the registered targets.

If an instance fails the configured health check, the ALB marks the target as **Unhealthy** and stops sending normal traffic to it.

If the Auto Scaling Group is configured to use ELB health checks, the ASG can also identify the unhealthy instance and replace it.

### 2. Actual self-healing test

The lab demonstrated this behavior by terminating the unhealthy instance:

* Terminated instance: `i-0ee2a22f694d8eda2`
* Auto Scaling Group: `cloudadhar-day9-asg`
* Replacement instance launched: `i-0583d46bd934633bd`
* Replacement became **InService / Healthy**

This demonstrated the important Auto Scaling concept of **self-healing**: the desired capacity is maintained even when an individual EC2 instance fails.

### 3. A new instance fails its ALB health check

If a newly launched instance does not successfully serve the expected application response, the ALB keeps the instance out of normal traffic.

The ASG can replace the instance if it remains unhealthy.

This protects users from being routed to an incorrectly configured or failed application instance.

### 4. High CPU causes a scale-out event

When average CPU utilization reaches the configured target of **50%**, the target-tracking policy can increase the number of instances.

The new instance is launched using the configured Launch Template.

After the instance becomes healthy and is registered with the target group, the ALB can begin sending traffic to it.

### 5. Traffic decreases and a scale-in event occurs

When demand decreases, the Auto Scaling Group can reduce the number of running instances according to its configured capacity and scaling policy.

Before an instance is removed from service, the load balancer can use **deregistration delay** to allow existing connections to complete.

### 6. A bad Launch Template version is used

If a Launch Template version contains an incorrect AMI, application configuration, security setting, or startup configuration, newly launched instances may fail.

Using versioned Launch Templates makes it possible to identify the known-good configuration and roll the ASG back to a stable version.

The lab used:

**Launch Template:** `cloudadhar-day9-lt`

**Tested version:** `2`

### 7. Availability Zone failure

In production, the Auto Scaling Group should distribute instances across multiple Availability Zones.

If one AZ becomes unavailable, instances in the remaining AZs can continue serving traffic through the ALB.

The ASG can also launch replacement capacity when the affected infrastructure becomes available again.

---

# Key Learning - Day 9

Day 9 demonstrated how an **Application Load Balancer and Auto Scaling Group work together**.

The important flow was:

**Client → ALB → Target Group → Healthy EC2 Instances**

and:

**Unhealthy EC2 → ALB/ASG detects failure → Instance replaced → New instance becomes Healthy**

The most important practical lesson was the **self-healing test**, where terminating an instance resulted in Auto Scaling launching a replacement instance automatically.

---

# Week 5 - Day 10: ALB Blue/Green Routing and NLB

## Decision Table

| Decision                 | Classroom Choice                              | Production Choice                                   | Reason                                                                                                                  |
| ------------------------ | --------------------------------------------- | --------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **Deployment strategy**  | Manual Blue/Green                             | Automated Blue/Green or Canary deployment           | Automated progressive deployments reduce deployment risk and make rollback easier.                                      |
| **Application versions** | Blue and Green NGINX targets                  | Separate application environments/target groups     | Keeping versions separated allows the new version to be tested before directing all traffic to it.                      |
| **Traffic shifting**     | Manual weighted routing                       | Automated gradual traffic shifting                  | Gradual traffic shifting allows the new version to be validated with limited traffic before full rollout.               |
| **Routing method**       | Host-based / Path-based                       | Host-based / Path-based                             | ALB Layer 7 routing allows requests to be directed to different target groups based on the request.                     |
| **Weighted routing**     | Manual traffic distribution                   | Automated progressive release                       | Weighted routing provides a controlled way to move traffic from Blue to Green.                                          |
| **Target health checks** | `/health.html`                                | Application-specific health endpoint                | Health checks ensure that unhealthy application targets are removed from traffic.                                       |
| **Stickiness**           | Enabled for the lab                           | Enabled only when session affinity is required      | Stickiness can keep a client associated with the same backend target when the application requires session persistence. |
| **Connection draining**  | ALB deregistration delay                      | Tuned according to application behavior             | Existing connections can complete before a target is removed from service.                                              |
| **Load balancer**        | ALB + NLB                                     | ALB or NLB according to application requirements    | ALB is designed for Layer 7 HTTP/HTTPS routing, while NLB provides Layer 4 network load balancing.                      |
| **NLB listener**         | TCP                                           | TCP/TLS based on application requirements           | The Day 10 lab demonstrated NLB Layer 4 routing using TCP.                                                              |
| **NLB target group**     | TCP target group                              | Protocol selected according to application traffic  | NLB target groups support Layer 4 traffic patterns such as TCP.                                                         |
| **Backend instances**    | Blue and Green EC2/NGINX targets              | Multiple targets across multiple Availability Zones | Multiple targets improve availability and reduce the impact of individual instance failures.                            |
| **TLS**                  | HTTP for the classroom routing demonstration  | HTTPS/TLS using ACM where encryption is required    | Production applications should protect client traffic with TLS.                                                         |
| **DNS**                  | Load balancer DNS endpoint for lab validation | Route 53 Alias record                               | Route 53 provides a stable application DNS name without requiring users to know load balancer IP addresses.             |

---

# Failure Review

### 1. Blue targets become unhealthy

The ALB health check detects that a Blue target is unhealthy.

The unhealthy target is removed from normal traffic distribution, while healthy targets continue serving requests.

This prevents an unhealthy Blue instance from receiving new application traffic.

### 2. Green targets become unhealthy during a weighted release

During a Blue/Green release, only a portion of traffic may initially be sent to Green.

If Green becomes unhealthy, the ALB health checks identify the affected targets and stop routing traffic to them.

Traffic can then continue through healthy Blue targets while the Green environment is investigated.

### 3. Incorrect ALB routing rule

An incorrectly configured host-based or path-based rule can send requests to the wrong target group.

The listener rules should therefore be tested against both Blue and Green environments before increasing traffic to the new release.

### 4. Weighted traffic shift

The lab demonstrated the idea of gradually shifting traffic between Blue and Green.

For example:

**Blue → 80%**

**Green → 20%**

If Green performs correctly, traffic can gradually be increased.

If Green has a problem, traffic can be shifted back toward Blue.

This provides a simple demonstration of **progressive deployment**.

### 5. Connection draining during deployment

When a target is deregistered, the ALB does not necessarily terminate existing connections immediately.

The **deregistration delay** allows active requests to complete before the target is fully removed.

This reduces disruption during deployment, scaling, or target replacement.

### 6. NLB target becomes unhealthy

The NLB performs health checks against its registered targets.

If a target fails its health check, the NLB stops sending new connections to that unhealthy target and continues using healthy targets.

### 7. NLB requires Layer 4 connectivity

The Day 10 lab demonstrated that an NLB is different from an ALB.

The ALB works at **Layer 7**, understanding HTTP/HTTPS requests and supporting routing based on information such as the host or path.

The NLB works at **Layer 4**, forwarding network connections such as TCP traffic.

The lab therefore required an **NLB-compatible TCP target group** rather than reusing an HTTP/HTTPS target group.

### 8. One Availability Zone becomes unavailable

In a production environment, targets should be distributed across multiple Availability Zones.

If one AZ becomes unavailable, the load balancer can continue directing traffic toward healthy targets in the remaining AZs.

This improves application availability and fault tolerance.

---

# Key Learning - Day 10

Day 10 demonstrated two important AWS load-balancing concepts.

### ALB - Layer 7

**Client**

↓

**Application Load Balancer**

↓

**Listener Rules**

↓

**Blue / Green Target Groups**

↓

**Healthy EC2 NGINX Targets**

The ALB is useful when the application needs intelligent HTTP/HTTPS routing, Blue/Green releases, weighted traffic shifting, health checks, stickiness, and connection draining.

### NLB - Layer 4

**Client**

↓

**Network Load Balancer**

↓

**TCP Listener**

↓

**TCP Target Group**

↓

**Healthy EC2 Targets**

The NLB is appropriate when the application requires Layer 4 network load balancing and high-performance TCP/TLS traffic handling.

---

# Week 5 Overall Learning

Day 9 and Day 10 together demonstrated how AWS can provide both **scalability and high availability**.

### Day 9

**ALB + Auto Scaling**

* Automatically adds capacity when demand increases
* Removes unhealthy instances
* Launches replacement instances
* Uses health checks to protect application traffic
* Maintains application availability during instance failures

### Day 10

**ALB Blue/Green + NLB**

* Separates Blue and Green application versions
* Routes traffic using ALB listener rules
* Demonstrates weighted traffic shifting
* Uses health checks to protect users from unhealthy targets
* Uses connection draining during target removal
* Demonstrates NLB Layer 4 TCP load balancing

### Overall Architecture Concept

**Users**

↓

**ALB**

↓

**Routing / Traffic Distribution**

↓

**Blue / Green Target Groups**

↓

**Healthy EC2 Instances**

↓

**Auto Scaling**

↓

**Automatic replacement and capacity adjustment**

And for Layer 4 workloads:

**Users / Clients**

↓

**NLB**

↓

**TCP Listener**

↓

**TCP Target Group**

↓

**Healthy EC2 Targets**

The key production lesson from Week 5 is that **load balancing, health checks, Auto Scaling, and controlled deployments work together** to build applications that can handle changing traffic and recover automatically from individual infrastructure failures.
