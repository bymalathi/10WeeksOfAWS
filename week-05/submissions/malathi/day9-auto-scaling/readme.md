# Day 9 - Auto Scaling and Application Load Balancer

## Learner

* Name: Malathi Shetty
* GitHub: shettymalathib
* LinkedIn: [Add LinkedIn profile]
* Region: us-west-2

---

## Objective

The objective of Day 9 was to build a highly available web application using an Application Load Balancer (ALB) and an EC2 Auto Scaling Group (ASG).

The lab demonstrated:

* Launch Templates
* Application Load Balancer
* Target Groups
* Auto Scaling Groups
* Target Tracking scaling
* CloudWatch alarms
* Scale-out and scale-in
* ELB health checks
* Auto Scaling self-healing
* Session Manager access
* Multi-AZ deployment

---

# 1. VPC and Networking

A dedicated VPC and networking components were created in the `us-west-2` Region.

The environment included:

* VPC
* Internet Gateway
* Two subnets
* Route Table
* Subnet associations

### VPC Creation

<img src="./screenshots/01-01-CreateVpc-VPC-us-west-2.png" width="700">

### VPC Created

<img src="./screenshots/01-02-CreatedVpc-VPC-us-west-2.png" width="700">

### VPC DNS Enabled

<img src="./screenshots/01-03-vpc-dns-enabled.png" width="700">

<img src="./screenshots/01-4-vpc-dns-enabled-dashboard.png" width="700">

### Internet Gateway

<img src="./screenshots/02-01-creating-internet-gateway.png" width="700">

<img src="./screenshots/02-02-created-internet-gateway.png" width="700">

<img src="./screenshots/02-03-attaching-VPC.png" width="700">

<img src="./screenshots/02-04-attached-VPC.png" width="700">

<img src="./screenshots/02-05-attached-VPC-internet-gateway.png" width="700">

### Subnets

<img src="./screenshots/03-01-Create-subnet.png" width="700">

<img src="./screenshots/03-02-Create-subnet-2.png" width="700">

<img src="./screenshots/03-03-two-subnets-created.png" width="700">

### Route Table

<img src="./screenshots/04-01-CreateRouteTable-VPC-Console.png" width="700">

<img src="./screenshots/04-02-EditRouteTable-VPC-Console.png" width="700">

<img src="./screenshots/04-03-Add-the-Internet-route.png" width="700">

### Subnet Associations

<img src="./screenshots/05-01-edit-subnet-associations.png" width="700">

<img src="./screenshots/05-01-select-both-subnets.png" width="700">

<img src="./screenshots/05-02-two-Explicit-subnet-associations.png" width="700">

---

# 2. Security Group and IAM Role

A security group was configured for the Day 9 web application.

An IAM role was also configured for Systems Manager Session Manager access.

### Security Group

<img src="./screenshots/06-01-CreateSecurityGroup-EC2-us-west-2.png" width="700">

<img src="./screenshots/06-02-cloudadhar-day9-web-sg.png" width="700">

### IAM Role

<img src="./screenshots/06-03-cloudadhar-role-ec2-ssm.png" width="700">

---

# 3. Initial EC2 and NGINX Validation

An EC2 instance was launched to validate the NGINX web server before configuring the Auto Scaling environment.

<img src="./screenshots/07-Launch-an-instance-EC2-us-west-2.png" width="700">

### NGINX Validation

<img src="./screenshots/08-nginx-validation-successful.png" width="700">

---

# 4. Launch Template

Launch Template:

`cloudadhar-day9-lt`

Version:

`2`

Instance type:

`t3.micro`

AMI:

`ami-08b7b9fdd7a1edf3d`

### Security Configuration

* IMDSv2 required
* IAM role used for Session Manager
* Security group configured for the web application
* No SSH key pair required
* Root storage uses encrypted gp3

The Auto Scaling Group uses Launch Template version 2 to consistently launch new EC2 instances.

### Launch Template Creation

<img src="./screenshots/09-01-Create-launch-template-EC2-us-west-2.png" width="700">

<img src="./screenshots/09-02-Create-launch-template-EC2-us-west-2.png" width="700">

### Launch Template Configuration

<img src="./screenshots/16-Launch_Template_Configuration.png" width="700">

---

# 5. Target Group

Target Group:

`cloudadhar-day9-tg`

Target type:

`Instance`

Protocol:

`HTTP`

Port:

`80`

The target group performs health checks on the EC2 instances before allowing them to receive traffic.

### Target Group Creation

<img src="./screenshots/10-Step-01-Creating-target-group-EC2-us-west-2.png" width="700">

<img src="./screenshots/10-Step-02-Create-target-group-EC2-us-west-2-08-30-2026_04_00_PM.png" width="700">

<img src="./screenshots/10-Step-03-Create-target-group-EC2-us-west-2-08-30-2026_03_58_PM.png" width="700">

### Target Group Details

<img src="./screenshots/10-04-Target-group-details-EC2-us-west-2.png" width="700">

<img src="./screenshots/10-09-Target-group-details-EC2-us-west-2.png" width="700">

### Target Group Configuration

<img src="./screenshots/17-Target_Group_Configuration.png" width="700">

---

# 6. Application Load Balancer

Application Load Balancer:

`cloudadhar-day9-alb`

Listener:

`HTTP : 80`

The ALB receives HTTP requests and forwards them to healthy EC2 instances registered in the target group.

### ALB Creation

<img src="./screenshots/10-05-Create-application-load-balancer-EC2-us-west-2-08-30-2026_07_06_PM.png" width="700">

<img src="./screenshots/10-06-Load-balancer-details-EC2-us-west-2.png" width="700">

### ALB Configuration

<img src="./screenshots/18-Application_Load_Balancer.png" width="700">

### Register Targets

<img src="./screenshots/10-07-register-targets.png" width="700">

<img src="./screenshots/10-08-Register-targets-EC2-us-west-2-08-30-2026_08_01_PM.png" width="700">

---

# 7. Application Validation

The NGINX application was successfully served through the Application Load Balancer.

<img src="./screenshots/11-1-webpage-served-by-your-nginx-EC2.png" width="700">

### Health Endpoint

<img src="./screenshots/11-2-health-endpoint.png" width="700">

### ALB Website

<img src="./screenshots/13-1-ALB-website.png" width="700">

### ALB Application Output

<img src="./screenshots/23-ALB_Application_Output.png" width="700">

---

# 8. Auto Scaling Group

Auto Scaling Group:

`cloudadhar-day9-asg`

### Capacity

* Minimum: `1`
* Desired: `1`
* Maximum: `3`

### Availability Zones

* `us-west-2a`
* `us-west-2b`

The Auto Scaling Group uses Launch Template version 2 to launch EC2 instances.

### ASG Creation

<img src="./screenshots/12-1-Create-Auto-Scaling-group-EC2-us-west-2.png" width="700">

<img src="./screenshots/12-2-Create-Auto-Scaling-group-EC2-us-west-2.png" width="700">

<img src="./screenshots/12-3-Create-Auto-Scaling-group-EC2-us-west-2-08-30-2026_09_06_PM.png" width="700">

<img src="./screenshots/12-4-Create-Auto-Scaling-group-EC2-us-west-2.png" width="700">

<img src="./screenshots/12-5-Create-Auto-Scaling-group-EC2-us-west-2.png" width="700">

<img src="./screenshots/12-6-Create-Auto-Scaling-group-EC2-us-west-2.png" width="700">

<img src="./screenshots/12-7-Created-successfully-Auto-Scaling-group-EC2-us-west-2.png" width="700">

<img src="./screenshots/12-8-Auto-Scaling-group-details-verification.png" width="700">

### Auto Scaling Group Configuration

<img src="./screenshots/19-Auto_Scaling_Group.png" width="700">

---

# 9. Target Tracking Scaling Policy

Scaling policy:

`Target Tracking Policy`

Metric:

`Average CPU Utilization`

Target:

`50%`

Scale-in:

Enabled

Instance warm-up:

`300 seconds`

The target tracking policy automatically adjusts the Auto Scaling Group capacity to maintain approximately 50% average CPU utilization.

CloudWatch alarms were automatically created for the target tracking policy.

### Target Tracking Policy

<img src="./screenshots/21-Target_Tracking_Scaling_Policy.png" width="700">

---

# 10. Scale-Out

CPU load was generated to increase CPU utilization.

The target tracking policy detected the increased demand and the Auto Scaling Group launched an additional EC2 instance.

### Scale-Out Flow

```text
CPU utilization increases
        |
        v
Target Tracking evaluates CPU
        |
        v
Scale-out decision
        |
        v
ASG launches additional EC2
        |
        v
Instance registers with Target Group
        |
        v
ELB health check passes
        |
        v
Target becomes Healthy
```

### High CPU Alarm

<img src="./screenshots/22-08_High_CPU_Alarm_Triggered.png" width="700">

### Scale-Out Activity

<img src="./screenshots/24-Scale_out_Activity.png" width="700">

### Scale-Out Result

<img src="./screenshots/15-Day9-ASG-ScaleOut-2-Instances.png" width="700">

### Two Healthy Instances

<img src="./screenshots/20-Two_Healthy_EC2_Instances.png" width="700">

### ALB Load Balancing

<img src="./screenshots/14-Day9-ALB-LoadBalancing-Instance1.png" width="700">

<img src="./screenshots/14-Day9-ALB-LoadBalancing-Instance2.png" width="700">

<img src="./screenshots/14-Day9-ALB-LoadBalancing-Instance3.png" width="700">

### Load Balancer Serving Multiple Instances

<img src="./screenshots/21-Load_Balancer_Serving_Multiple_Instances.jpg" width="700">

---

# 11. Scale-In

After the CPU workload was stopped, CPU utilization decreased.

The target tracking policy detected that fewer instances were required and the Auto Scaling Group reduced capacity.

### Scale-In Flow

```text
CPU utilization decreases
        |
        v
Target Tracking evaluates CPU
        |
        v
Scale-in decision
        |
        v
ASG reduces capacity
        |
        v
EC2 instance removed
        |
        v
ASG returns toward desired capacity
```

### Low CPU / Scale-In Evidence

<img src="./screenshots/25-Scale_In_Activity.png" width="700">

---

# 12. Self-Healing / Unhealthy Target

The self-healing behavior of the Auto Scaling Group was tested by causing an application-level health check failure.

The Application Load Balancer detected that the target was unhealthy.

### Self-Healing Flow

```text
NGINX / application becomes unhealthy
        |
        v
ELB health check fails
        |
        v
Target becomes Unhealthy
        |
        v
ASG detects ELB health-check failure
        |
        v
Unhealthy EC2 instance terminated
        |
        v
ASG launches replacement
        |
        v
Replacement registers with Target Group
        |
        v
ELB health check passes
        |
        v
Replacement becomes Healthy
```

### Unhealthy Target Detected

<img src="./screenshots/27-Unhealthy_Target_Detected.png" width="700">

### Auto Scaling Replacement

<img src="./screenshots/26-Auto_Scaling_Replacement.png" width="700">

The Auto Scaling Activity History confirmed:

* The unhealthy instance was taken out of service because of an ELB system health check failure.
* A replacement EC2 instance was launched because an unhealthy instance needed to be replaced.

### Replacement Instance

The replacement instance successfully registered with the Target Group and became healthy.

---

# 13. Session Manager

EC2 instances were accessed using AWS Systems Manager Session Manager.

Session Manager provided command-line access without requiring:

* SSH
* An SSH key pair
* Inbound SSH port 22

Session Manager was used to validate the NGINX service and perform the application health testing during the self-healing test.

---

# 14. Health Checks

Two health check sources were used:

* EC2 health checks
* ELB health checks

The EC2 health check determines whether the underlying EC2 instance is functioning.

The ELB health check verifies whether the application target is responding correctly.

This distinction is important because an EC2 instance can be running while the application running on it is unhealthy.

---

# 15. Troubleshooting Lesson

One important troubleshooting lesson was understanding the difference between an EC2 instance being healthy and an application target being healthy.

An EC2 instance can be running while the application is not responding correctly.

In this lab, the ELB health check detected an unhealthy application target. The Auto Scaling Group then removed the unhealthy instance and launched a replacement.

The Auto Scaling Activity History was useful for confirming exactly why an instance was terminated and why a replacement was launched.

---

# 16. Evidence Summary

The Day 9 evidence demonstrates:

* VPC and networking
* Security Group
* IAM role
* Launch Template
* Launch Template version 2
* Target Group
* Application Load Balancer
* Auto Scaling Group
* Target Tracking scaling policy
* CloudWatch alarms
* High CPU alarm
* Scale-out
* Multiple EC2 instances
* ALB traffic distribution
* Scale-in
* Unhealthy target detection
* Auto Scaling replacement
* Replacement instance recovery
* Session Manager
* Working NGINX application
* Multi-AZ deployment

---

# Day 9 Architecture

## Architecture Flow
<img src="./diagram/day9-alb-asg-architecture.gif" width="900">

---

# Key Learning

The main learning from Day 9 was that the Application Load Balancer and Auto Scaling Group solve different problems.

The **Application Load Balancer** distributes incoming application traffic across healthy targets.

The **Auto Scaling Group** manages the number of EC2 instances based on demand and replaces unhealthy instances.

The **Launch Template** provides a consistent configuration for every new EC2 instance.

**Target Tracking** and **CloudWatch** provide automated scaling based on CPU utilization.

Together, these services provide:

* Load balancing
* Scalability
* High availability
* Fault tolerance
* Self-healing

The Day 9 lab demonstrated how these AWS services work together to create a resilient web application architecture.
