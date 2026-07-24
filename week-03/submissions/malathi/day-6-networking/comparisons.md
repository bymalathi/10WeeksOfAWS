# Week 3 – Day 6: VPC Components Comparisons

This document summarizes the networking concepts learned while extending the AWS VPC architecture with private subnet internet access, endpoint connectivity, traffic filtering, monitoring, and high availability.

---

# 1. NAT Gateway vs NAT Instance

Both NAT Gateway and NAT Instance allow resources in private subnets to access the internet without exposing them with public IP addresses.

| Feature | NAT Gateway | NAT Instance |
|----------|-------------|--------------|
| Type | AWS managed service | EC2 instance managed by the user |
| Deployment | Created by AWS | Launched as an EC2 instance |
| Management | Fully managed | User manages OS, patches, and updates |
| Availability | Highly available within an Availability Zone | Depends on EC2 instance health |
| Scaling | Automatically scales | Limited by instance size |
| Security Group | Cannot attach Security Group | Security Group can be attached |
| Route Table Target | NAT Gateway | EC2 Instance ID |
| Performance | AWS managed | Depends on instance resources |
| Cost | Hourly charge + data processing | EC2 + EBS + data transfer costs |
| Best Use Case | Production environments | Learning, testing, or custom NAT configurations |

---

# 2. Single NAT Gateway vs NAT Gateway Per Availability Zone

| Feature | Single NAT Gateway | NAT Gateway Per AZ (Recommended) |
|----------|-------------------|----------------------------------|
| Availability | Single point of failure | High availability |
| Fault Tolerance | Low | High |
| Cross-AZ Traffic | Higher | Minimal |
| Cost | Lower initial cost | Higher infrastructure cost |
| Production Ready | Not recommended | Recommended |
| AWS Best Practice | No | Yes |

**Why one NAT Gateway per AZ?**

- Eliminates single points of failure
- Reduces cross-AZ data transfer costs
- Improves application availability
- Each Availability Zone remains independent

---

# 3. Security Group vs Network ACL

Both Security Groups and Network ACLs filter network traffic but operate at different layers of the VPC.

| Feature | Security Group | Network ACL |
|----------|----------------|-------------|
| Scope | Instance / ENI level | Subnet level |
| Acts As | Virtual firewall | Subnet firewall |
| Stateful | Yes | No |
| Stateless | No | Yes |
| Supports Allow Rules | Yes | Yes |
| Supports Deny Rules | No | Yes |
| Return Traffic | Automatically allowed | Must be explicitly allowed |
| Rule Evaluation | All matching rules | Lowest rule number first |
| Default Behaviour | Deny inbound, allow outbound | Default NACL allows all traffic |
| Recommended Usage | Primary security layer | Additional subnet protection |

---

# 4. Stateful vs Stateless Firewall

| Feature | Stateful (Security Group) | Stateless (Network ACL) |
|----------|---------------------------|--------------------------|
| Tracks Connections | Yes | No |
| Return Traffic | Automatically allowed | Separate outbound rule required |
| Configuration | Simpler | Requires inbound and outbound rules |
| Example | Allow HTTP inbound only | Allow HTTP inbound **and** Ephemeral ports outbound |

---

# 5. Gateway Endpoint vs Interface Endpoint

VPC Endpoints allow private connectivity to AWS services without using the public internet.

| Feature | Gateway Endpoint | Interface Endpoint |
|----------|------------------|--------------------|
| Supported Services | Amazon S3, DynamoDB | Most AWS services |
| Technology | Route Table Entry | Elastic Network Interface (ENI) |
| Uses AWS PrivateLink | No | Yes |
| Creates ENI | No | Yes |
| Security Group Required | No | Yes |
| Private DNS | No | Yes |
| Route Table Update Required | Yes | No |
| Hourly Charges | No | Yes |
| Data Processing Charges | No | Yes |
| Best Use Case | S3 and DynamoDB | EC2 API, SSM, CloudWatch, Secrets Manager, etc. |

---

# 6. Accessing Amazon S3

| Without Gateway Endpoint | With Gateway Endpoint |
|---------------------------|-----------------------|
| Uses NAT Gateway | Direct private connection |
| Internet Gateway involved | No Internet Gateway required |
| NAT processing charges apply | No NAT charges |
| Longer network path | Private AWS backbone |
| Less secure | More secure |

---

# 7. VPC Flow Logs

| Feature | Description |
|----------|-------------|
| Purpose | Capture metadata about network traffic |
| Records | ACCEPT and REJECT traffic |
| Useful For | Troubleshooting connectivity |
| Security Analysis | Detect blocked traffic |
| Performance Monitoring | Analyze network communication |
| Stores Data In | CloudWatch Logs or Amazon S3 |

### Flow Log Actions

| Action | Meaning |
|---------|---------|
| ACCEPT | Traffic was permitted |
| REJECT | Traffic was blocked by Security Group, Network ACL, or routing |

---

# 8. Endpoint Selection Guide

| Requirement | Recommended Solution |
|-------------|----------------------|
| Private EC2 → Amazon S3 | Gateway Endpoint |
| Private EC2 → DynamoDB | Gateway Endpoint |
| Private EC2 → EC2 API | Interface Endpoint |
| Private EC2 → Systems Manager | Interface Endpoint |
| Private EC2 → Secrets Manager | Interface Endpoint |
| Private EC2 → CloudWatch | Interface Endpoint |
| Private EC2 → Internet | NAT Gateway |

---

# 9. High Availability Design

| Design Principle | Benefit |
|------------------|---------|
| Public Subnet in each Availability Zone | Redundancy |
| Private Subnet in each Availability Zone | Fault tolerance |
| NAT Gateway in every Availability Zone | Eliminates single point of failure |
| Separate Route Tables | Better traffic control |
| Multiple Availability Zones | High availability |
| VPC Endpoints | Private AWS service connectivity |

---

# 10. Important Networking Concepts

| Concept | Explanation |
|----------|-------------|
| Network Connectivity | Determines whether traffic can reach a destination. |
| Authorization | Determines whether AWS allows the requested action. |
| Connectivity + IAM | Both must succeed for access to work. |
| Example | Network path available but IAM permission missing results in **Access Denied**. |

---

# Summary

| Component | Primary Purpose |
|-----------|-----------------|
| NAT Gateway | Internet access for private subnets |
| Security Group | Stateful instance-level firewall |
| Network ACL | Stateless subnet-level firewall |
| Gateway Endpoint | Private access to Amazon S3 and DynamoDB |
| Interface Endpoint | Private access to AWS services using PrivateLink |
| VPC Flow Logs | Monitor and troubleshoot network traffic |
| Multi-AZ Design | Improve availability and fault tolerance |
