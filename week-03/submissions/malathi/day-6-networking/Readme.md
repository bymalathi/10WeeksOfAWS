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

1. NAT Gateway Available
<img width="2220" height="752" alt="image" src="https://github.com/user-attachments/assets/22861215-cb07-4994-88c8-0fe69ff042d5" />

2. Private EC2 Instance
<img width="2192" height="1050" alt="image" src="https://github.com/user-attachments/assets/96e4e371-9480-471b-b83c-0d7b895aceb8" />

3. Session Manager Connection
<img width="2511" height="841" alt="image" src="https://github.com/user-attachments/assets/562432e3-3767-4327-88f8-c8cc9c3744cf" />

4. Internet Connectivity Validation
<img width="2305" height="442" alt="image" src="https://github.com/user-attachments/assets/a598c26d-9c62-47d6-9cb8-dc0f129db986" />

5. AWS CLI Identity Validation
<img width="1137" height="155" alt="image" src="https://github.com/user-attachments/assets/b868a88c-c1d2-4047-adcb-ab910d89830d" />

6. Web Server Security Group
<img width="2222" height="991" alt="image" src="https://github.com/user-attachments/assets/a8d226cf-34b0-4c0f-8895-7772b57d9404" />

7. Web Server Running
<img width="2212" height="1026" alt="image" src="https://github.com/user-attachments/assets/f4df5ea2-0bbc-4342-8b72-0b879e5b3b06" />
<img width="686" height="142" alt="image" src="https://github.com/user-attachments/assets/021a29b4-f623-4d1c-a63a-5079a1f7ee39" />

8.Custom Network ACL & HTTP Blocked by Network ACL
<img width="2232" height="812" alt="image" src="https://github.com/user-attachments/assets/3b2f7e3f-293b-409a-bae0-efd7d5fc789f" />
<img width="2232" height="852" alt="image" src="https://github.com/user-attachments/assets/cc3865e4-74ba-479f-a27f-a47b526e64cf" />
<img width="1862" height="875" alt="image" src="https://github.com/user-attachments/assets/dab0a167-8c08-4679-8ac7-86da9786febc" />

9. Amazon S3 Gateway Endpoint
<img width="2251" height="820" alt="image" src="https://github.com/user-attachments/assets/ed063730-bd78-43f3-9f1b-73af808e72f3" />

10. S3 Prefix List Route
<img width="2202" height="752" alt="image" src="https://github.com/user-attachments/assets/002aab90-232f-45b2-b023-da2670776bfe" />

11. Amazon S3 Validation
<img width="965" height="196" alt="image" src="https://github.com/user-attachments/assets/2557a272-65f0-4aa3-bd2d-370cc01ceab9" />

12. EC2 Interface Endpoint

<img width="2232" height="1050" alt="image" src="https://github.com/user-attachments/assets/31da44c1-a98e-4f63-bf59-74a84fcdf493" />
<img width="2226" height="712" alt="image" src="https://github.com/user-attachments/assets/13d02a31-8226-4555-a681-5caed4596e24" />
<img width="2227" height="692" alt="image" src="https://github.com/user-attachments/assets/83d23e45-82cf-4caa-adf4-3ac2d8722e15" />

13. Private DNS Resolution
<img width="787" height="716" alt="image" src="https://github.com/user-attachments/assets/495167fa-6105-45c9-9365-385b46b7ef7b" />

14. VPC Flow Logs Configuration
<img width="2216" height="812" alt="image" src="https://github.com/user-attachments/assets/d8a00b20-9bb1-4514-9749-e6ee51893014" />

15. Flow Logs – REJECT Traffic
<img width="2533" height="1132" alt="image" src="https://github.com/user-attachments/assets/a2721efc-420b-47a8-80dc-cb4fb548ea92" />
```text
SOURCE "arn:aws:logs:us-west-2:138852020826:log-group:/aws/vpc/flowlogs/cloudadhar-day6" START=-604800s END=0s |
fields @timestamp, @message, action
| filter @message like /REJECT/
| sort @timestamp desc
| limit 20
```
<img width="2545" height="1232" alt="image" src="https://github.com/user-attachments/assets/218cade2-f991-46f3-9d3b-ae8e07fae7d9" />

16. Flow Logs – ACCEPT Traffic
```text
SOURCE "arn:aws:logs:us-west-2:138852020826:log-group:/aws/vpc/flowlogs/cloudadhar-day6" START=-604800s END=0s |
fields @timestamp, @message, action
| filter @message like /ACCEPT/
| sort @timestamp desc
| limit 20
```
<img width="2541" height="1126" alt="image" src="https://github.com/user-attachments/assets/a0430919-5ddb-455c-83be-3d5b5005f805" />


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
