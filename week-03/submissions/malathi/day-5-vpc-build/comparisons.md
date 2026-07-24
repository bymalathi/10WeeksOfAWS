# Week 3 - Day 5 VPC Components Comparisons

## Overview

This document compares the core Amazon VPC networking components covered during
Day 5 while building a custom VPC across two Availability Zones.

The topics include:

- Public vs Private Subnets
- Route Tables
- Internet Gateway
- Main Route Table vs Custom Route Tables
- Single AZ vs Multi-AZ Architecture
- VPC CIDR vs Subnet CIDR

---

# 1. Public Subnet vs Private Subnet

A subnet is not inherently public or private. Its behavior depends on the route
table associated with it.

| Feature | Public Subnet | Private Subnet |
|----------|---------------|----------------|
| Route to Internet Gateway (IGW) | Yes | No |
| Default Route | `0.0.0.0/0 → IGW` | Local route only |
| Public IPv4 Address | Enabled (optional) | Disabled |
| Direct Internet Access | Yes | No |
| Inbound Internet Connectivity | Allowed (subject to Security Groups/NACLs) | Not allowed directly |
| Typical Workloads | Web Servers, Bastion Hosts, Load Balancers | Application Servers, Databases |
| Security Level | Lower (Internet-facing) | Higher (Internal only) |

### Key Points

- Route table association determines whether a subnet is public or private.
- Public subnets require an Internet Gateway route.
- Private subnets remain isolated from direct internet traffic.

---

# 2. Public Route Table vs Private Route Table vs Main Route Table

Route tables determine where network traffic is directed.

| Feature | Public Route Table | Private Route Table | Main Route Table |
|----------|-------------------|--------------------|------------------|
| Purpose | Internet connectivity | Internal communication | Default routing table |
| Local Route | Yes | Yes | Yes |
| Internet Gateway Route | Yes | No | No (by default) |
| Used By | Public Subnets | Private Subnets | Any subnet without explicit association |
| Internet Access | Yes | No | No (unless modified) |

### Example Routes

| Route Table | Destination | Target |
|-------------|------------|--------|
| Public | `10.10.0.0/16` | Local |
| | `0.0.0.0/0` | Internet Gateway |
| Private | `10.10.0.0/16` | Local |
| Main | `10.10.0.0/16` | Local |

### Key Points

- Every VPC contains one Main Route Table.
- Public and Private Route Tables are created for workload-specific routing.
- Keeping the Main Route Table local-only reduces accidental exposure.

---

# 3. Internet Gateway vs NAT Gateway

> **Note:** NAT Gateway is introduced on Day 6. It is included here only to
highlight the role of the Internet Gateway.

| Feature | Internet Gateway (IGW) | NAT Gateway |
|----------|------------------------|-------------|
| Primary Purpose | Provides internet connectivity for public resources | Provides outbound internet access for private resources |
| Attached To | VPC | Public Subnet |
| Public IP Required | Yes (for EC2 instance) | NAT Gateway uses an Elastic IP |
| Supports Inbound Internet Traffic | Yes | No |
| Supports Outbound Internet Traffic | Yes | Yes |
| Used By | Public Subnets | Private Subnets |

### Key Points

- Internet Gateway connects a VPC to the internet.
- Public subnets require an Internet Gateway route.
- NAT Gateway is covered in detail on Day 6.

---

# 4. Main Route Table vs Custom Route Tables

| Feature | Main Route Table | Custom Route Table |
|----------|------------------|--------------------|
| Created By | AWS automatically | User |
| Default Route Table | Yes | No |
| Initial Route | Local Route | User-defined |
| Purpose | Default routing | Dedicated routing for workloads |
| Best Practice | Keep local-only | Associate with required subnets |

### Key Points

Keeping the Main Route Table local-only helps:

- Prevent accidental internet exposure
- Maintain predictable routing
- Separate public and private network traffic

---

# 5. Single Availability Zone vs Multi-AZ Design

| Feature | Single AZ | Multi-AZ |
|----------|-----------|-----------|
| Availability | Lower | Higher |
| Fault Tolerance | No | Yes |
| High Availability | Limited | Improved |
| Cost | Lower | Slightly Higher |
| Production Readiness | Not Recommended | Recommended |
| Failure Impact | Entire workload affected | Traffic continues through another AZ |

### Key Points

Deploying resources across multiple Availability Zones provides:

- High availability
- Better resilience
- Improved fault tolerance

---

# 6. VPC CIDR vs Subnet CIDR

| Feature | VPC CIDR | Subnet CIDR |
|----------|----------|-------------|
| Purpose | Defines the IP address range for the VPC | Defines the IP range for an individual subnet |
| Size | Larger network | Smaller network segment |
| Relationship | Parent network | Child network |
| Example | `10.10.0.0/16` | `10.10.1.0/24` |

### Example Address Plan

| Resource | CIDR Block |
|----------|------------|
| VPC | `10.10.0.0/16` |
| Public Subnet A | `10.10.1.0/24` |
| Public Subnet B | `10.10.2.0/24` |
| Private Subnet A | `10.10.11.0/24` |
| Private Subnet B | `10.10.12.0/24` |

### Key Points

- A VPC CIDR block defines the complete private network.
- Subnets divide the VPC into smaller logical networks.
- Proper CIDR planning avoids overlapping IP ranges.

---

# Summary

| Concept | Key Takeaway |
|----------|--------------|
| Public vs Private Subnet | Route table determines subnet behavior. |
| Route Tables | Control network traffic within the VPC. |
| Internet Gateway | Enables internet access for public resources. |
| Main Route Table | Default route table; best kept local-only. |
| Multi-AZ | Improves availability and fault tolerance. |
| CIDR Planning | Organizes IP addressing efficiently. |

---

# References

| Resource | Link |
|----------|------|
| CIDR Calculator | https://cidr.xyz/ |
| AWS VPC Documentation | https://docs.aws.amazon.com/vpc/ |
| Amazon VPC User Guide | https://docs.aws.amazon.com/vpc/latest/userguide/ |
