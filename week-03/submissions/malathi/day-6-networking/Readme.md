---

# Week 3 - Day 6: Amazon VPC Part 2

## Name

Malathi Shetty

---

# Tasks Completed

* [x] Extended Day 5 VPC architecture
* [x] Configured private subnet outbound access
* [x] Implemented VPC Endpoints
* [x] Configured Security Groups
* [x] Configured Network ACL testing
* [x] Enabled VPC Flow Logs
* [x] Completed validation
* [x] Documented findings

---

# Architecture

![Day 6 Extended VPC](diagrams/week-03-day6-extend-vpc.png)

---

# Architecture Decisions

## Why use NAT Gateway?

Private subnet resources do not have public IP addresses, but they may still require outbound internet access for:

* Package updates
* Software installation
* External API communication

A NAT Gateway provides outbound internet access while preventing inbound internet connections.

Traffic flow:

```
Private EC2
     |
     |
Private Route Table
     |
     |
NAT Gateway
     |
     |
Internet Gateway
     |
     |
Internet
```

---

# Why use NAT Gateway per Availability Zone?

Production architectures commonly deploy NAT Gateways per AZ because:

* Avoids a single point of failure.
* Keeps traffic inside the same Availability Zone.
* Reduces cross-AZ data transfer cost.
* Provides better resilience.

Example:

```
Private-A
   |
NAT-A
   |
IGW


Private-B
   |
NAT-B
   |
IGW
```

---

# Why use S3 Gateway Endpoint?

S3 Gateway Endpoint provides private connectivity from VPC resources to Amazon S3.

Benefits:

* No internet gateway path required.
* No NAT Gateway data processing charges.
* Traffic stays within AWS network.
* Supports endpoint policies.

Traffic path:

Before:

```
Private EC2
 |
NAT Gateway
 |
Internet Gateway
 |
S3
```

After:

```
Private EC2
 |
S3 Gateway Endpoint
 |
Amazon S3
```

---

# Security Group vs NACL

## Security Group

* Instance level firewall.
* Stateful.
* Automatically allows return traffic.
* Supports allow rules only.

Example:

```
Allow HTTPS 443
```

---

## Network ACL

* Subnet level firewall.
* Stateless.
* Requires inbound and outbound rules.
* Supports allow and deny rules.

Example:

```
Deny HTTP 80
```

---

# Result

Extended the VPC with secure private access, controlled networking, and monitoring.

---

# Resources Created

## NAT Gateway

```
cloudadhar-day6-nat-a
```

Used for private subnet outbound internet access.

---

## Private EC2

```
cloudadhar-day6-private-ec2
```

Details:

```
Private IP: 10.10.11.10
Public IP: None
Subnet: cloudadhar-private-a
```

Connected using AWS Systems Manager Session Manager.

---

## IAM Role

```
cloudadhar-day6-ssm-role
```

Policy:

```
AmazonSSMManagedInstanceCore
```

Used for secure EC2 management without SSH.

---

## S3 Gateway Endpoint

```
cloudadhar-day6-s3-gateway-endpoint
```

Validation:

```
aws s3api list-buckets
```

Successful response proved:

* Endpoint connectivity works.
* IAM permission works.
* S3 access does not require NAT.

---

## EC2 Interface Endpoint

```
cloudadhar-day6-ec2-endpoint
```

Created using:

```
com.amazonaws.us-west-2.ec2
```

Private DNS validation:

```
nslookup ec2.us-west-2.amazonaws.com
```

Result:

```
10.10.11.155
```

This proved EC2 API traffic resolved to a private endpoint IP instead of public internet.

---

# VPC Flow Logs Validation

Created:

```
cloudadhar-day6-flow-logs
```

Destination:

```
CloudWatch Logs
/aws/vpc/flowlogs/cloudadhar-day6
```

---

## ACCEPT Example

Observed successful traffic:

```
ACCEPT OK
```

Meaning:

* Security Group/NACL allowed traffic.
* Network path was successful.

---

## REJECT Example

Observed blocked traffic:

```
REJECT OK
```

Meaning:

* Traffic reached the network layer.
* A rule blocked the connection.

---

# Validation Completed

✅ Private EC2 without public IP
✅ Session Manager connection successful
✅ NAT Gateway outbound connectivity verified
✅ S3 Gateway Endpoint validated
✅ EC2 Interface Endpoint validated
✅ Security Group behavior verified
✅ NACL deny and recovery tested
✅ Flow Logs captured ACCEPT and REJECT traffic

---

# Screenshots

(Keep your screenshot names)

---

# Where I Got Stuck

During Session Manager setup, the private EC2 initially appeared offline.

Troubleshooting performed:

* Verified IAM role attachment.
* Checked SSM Agent status.
* Rebooted EC2 instance.
* Confirmed instance became online.

Another issue:

S3 access initially returned:

```
AccessDenied
s3:ListAllMyBuckets
```

After attaching the required S3 read permission, validation succeeded.

---

# Cleanup

Cleanup order:

1. Terminate EC2 instances.
2. Delete Interface Endpoint.
3. Delete NAT Gateway.
4. Release Elastic IP.
5. Delete S3 Gateway Endpoint.
6. Delete VPC Flow Logs.
7. Delete CloudWatch Log Group.
8. Remove custom NACL.
9. Remove temporary Security Groups.
10. Delete remaining VPC resources.

---

# LinkedIn Post

(Add your Day 6 LinkedIn URL)



This version is actually stronger than your friend's because it includes your **real troubleshooting story** (SSM offline + IAM AccessDenied + Endpoint validation), which interviewers like because it shows debugging ability.
