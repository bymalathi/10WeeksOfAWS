# 🌐 CIDR Planning – Week 3 VPC

## Introduction

Classless Inter-Domain Routing (CIDR) is used in Amazon Virtual Private Cloud (Amazon VPC) to define the range of private IPv4 addresses available within a network. Proper CIDR planning is essential for designing scalable, secure, and highly available cloud infrastructures.

For this implementation, a VPC with a **`/16` CIDR block** was created and divided into multiple **`/24` subnets** across two Availability Zones. This design separates public and private resources while leaving sufficient address space for future expansion.

---

# VPC CIDR Block

The VPC was created with the CIDR block **`10.10.0.0/16`**, providing a large private IPv4 address space that can be divided into multiple subnets as the infrastructure grows.

| Resource            | CIDR Block   | Total IPv4 Addresses |
| ------------------- | ------------ | -------------------: |
| cloudadhar-day5-vpc | 10.10.0.0/16 |               65,536 |

> **Note:** AWS does **not** reserve IP addresses at the VPC level. IP address reservation applies only to subnets.

---

# VPC Address Space

```text
VPC
10.10.0.0/16
│
├── Public Subnet A      10.10.1.0/24
├── Public Subnet B      10.10.2.0/24
├── Private Subnet A     10.10.11.0/24
└── Private Subnet B     10.10.12.0/24
```

The remaining address space is intentionally left unused to allow additional subnets to be created in the future without redesigning the VPC.

---

# Subnet CIDR Allocation

The VPC is divided into four `/24` subnets distributed across two Availability Zones to support high availability and network isolation.

| Subnet               | Availability Zone | CIDR Block    | Total IPv4 Addresses | AWS Usable IPv4 Addresses |
| -------------------- | ----------------- | ------------- | -------------------: | ------------------------: |
| cloudadhar-public-a  | AZ-A              | 10.10.1.0/24  |                  256 |                       251 |
| cloudadhar-public-b  | AZ-B              | 10.10.2.0/24  |                  256 |                       251 |
| cloudadhar-private-a | AZ-A              | 10.10.11.0/24 |                  256 |                       251 |
| cloudadhar-private-b | AZ-B              | 10.10.12.0/24 |                  256 |                       251 |

---

# Address Allocation Strategy

The subnet ranges were selected to maintain a simple and organized addressing scheme.

* Public subnets use lower IP address ranges.
* Private subnets use separate higher IP address ranges.
* The gap between public and private subnet ranges is intentional, allowing additional subnets to be created later without modifying existing subnet allocations.

This approach improves readability, simplifies troubleshooting, and supports future network expansion.

---

# Network Design Goals

The VPC network was designed with the following objectives:

* Provide secure network segmentation.
* Separate public and private workloads.
* Support high availability across multiple Availability Zones.
* Allow future network expansion.
* Avoid overlapping CIDR ranges.
* Follow AWS networking best practices.

---

# CIDR Design Decisions

## Why use a `/16` CIDR block for the VPC?

A `/16` CIDR block provides **65,536 IPv4 addresses**, making it suitable for both learning environments and production-style architectures.

### Benefits

* Large address space for future growth
* Supports multiple Availability Zones
* Allows creation of many subnets
* Simplifies network planning
* Supports additional AWS services such as Amazon RDS, NAT Gateway, Load Balancers, EKS, ECS, and VPC Endpoints
* Eliminates the need for early VPC redesign

---

## Why use `/24` CIDR blocks for subnets?

Each subnet uses a `/24` CIDR block.

A `/24` subnet provides:

* 256 total IPv4 addresses
* 251 usable IPv4 addresses in AWS
* Sufficient capacity for small to medium-sized workloads
* Easy subnet identification and management
* Supports EC2 instances, Load Balancers, NAT Gateways, Auto Scaling Groups, and databases

---

# CIDR Hierarchy

```text
10.10.0.0/16
│
├── 10.10.1.0/24
│      Public Subnet - AZ A
│
├── 10.10.2.0/24
│      Public Subnet - AZ B
│
├── 10.10.11.0/24
│      Private Subnet - AZ A
│
└── 10.10.12.0/24
       Private Subnet - AZ B
```

---

# High Availability Design

The subnets are distributed across two Availability Zones to improve fault tolerance and increase application availability.

```text
                 VPC
            10.10.0.0/16
                  │
      ┌───────────┴───────────┐
      │                       │
     AZ-A                   AZ-B
      │                       │
 ┌────┴────┐             ┌────┴────┐
 │         │             │         │
Public   Private      Public   Private
10.10.1 10.10.11     10.10.2 10.10.12
```

If one Availability Zone experiences a failure, resources in the other Availability Zone can continue serving application traffic.

---

# Understanding CIDR Notation

CIDR (Classless Inter-Domain Routing) specifies how many bits of an IPv4 address represent the network portion.

| CIDR | Network Bits | Host Bits |
| ---- | -----------: | --------: |
| /16  |           16 |        16 |
| /24  |           24 |         8 |
| /26  |           26 |         6 |
| /28  |           28 |         4 |

A smaller prefix length creates a larger network, while a larger prefix length creates a smaller network.

---

# CIDR Calculation Formula

The total number of IPv4 addresses is calculated using the following formula:

```text
Total IPv4 Addresses = 2^(32 − Prefix Length)
```

---

## Example 1 – VPC (`/16`)

```text
CIDR Block = 10.10.0.0/16

Total IPv4 Addresses

= 2^(32 − 16)

= 2^16

= 65,536 IPv4 Addresses
```

---

## Example 2 – Subnet (`/24`)

```text
CIDR Block = 10.10.1.0/24

Total IPv4 Addresses

= 2^(32 − 24)

= 2^8

= 256 IPv4 Addresses

AWS reserves 5 IPv4 addresses in every subnet.

Usable IPv4 Addresses

= 256 − 5

= 251
```

---

# Subnet Mask Reference

| CIDR | Subnet Mask     | Total IPv4 Addresses | AWS Usable IPv4 Addresses |
| ---- | --------------- | -------------------: | ------------------------: |
| /16  | 255.255.0.0     |               65,536 |           N/A (VPC Level) |
| /24  | 255.255.255.0   |                  256 |                       251 |
| /26  | 255.255.255.192 |                   64 |                        59 |
| /28  | 255.255.255.240 |                   16 |                        11 |

---

# Binary Representation

Example subnet:

```text
10.10.1.0/24
```

Binary representation:

```text
IP Address

00001010.00001010.00000001.00000000

Subnet Mask

11111111.11111111.11111111.00000000
```

The first **24 bits** represent the network portion, while the remaining **8 bits** are available for host addresses.

---

# AWS Reserved IPv4 Addresses

AWS reserves **five IPv4 addresses** in every subnet.

| Reserved Address              | Purpose                                                                           |
| ----------------------------- | --------------------------------------------------------------------------------- |
| x.x.x.0                       | Network address                                                                   |
| x.x.x.1                       | VPC Router                                                                        |
| x.x.x.2                       | Amazon DNS Server                                                                 |
| x.x.x.3                       | Reserved for future AWS use                                                       |
| Last IP address of the subnet | Reserved by AWS (traditional IPv4 broadcast addresses are not used in Amazon VPC) |

### Example

Subnet:

```text
10.10.1.0/24
```

Reserved addresses:

| IP Address  | Purpose                     |
| ----------- | --------------------------- |
| 10.10.1.0   | Network address             |
| 10.10.1.1   | VPC Router                  |
| 10.10.1.2   | Amazon DNS Server           |
| 10.10.1.3   | Reserved for future AWS use |
| 10.10.1.255 | Reserved by AWS             |

---

# Future Expansion

The `/16` VPC leaves sufficient unused address space for future network growth.

Example subnet allocation:

| Future Resource         | Suggested CIDR |
| ----------------------- | -------------- |
| Database Subnet A       | 10.10.21.0/24  |
| Database Subnet B       | 10.10.22.0/24  |
| Monitoring Subnet       | 10.10.31.0/24  |
| Management Subnet       | 10.10.41.0/24  |
| Kubernetes Worker Nodes | 10.10.51.0/24  |
| Shared Services         | 10.10.61.0/24  |

---

# Network Design Considerations

The network follows AWS networking best practices by:

* Using non-overlapping CIDR ranges.
* Separating public and private workloads.
* Deploying subnets across multiple Availability Zones.
* Providing sufficient address space for future expansion.
* Maintaining a simple and organized IP addressing scheme.
* Supporting scalable application deployment.

---

# Validation

The network configuration was validated to ensure correct CIDR allocation.

* ✔ All subnet CIDRs fall within the VPC CIDR range.
* ✔ No subnet CIDR overlaps exist.
* ✔ Public and private subnets are clearly separated.
* ✔ Each subnet provides **251 usable IPv4 addresses**.
* ✔ Multi-AZ deployment supports high availability.
* ✔ Address space remains available for future subnet expansion.

---

# Summary

| Component                            | Configuration |
| ------------------------------------ | ------------- |
| VPC CIDR                             | 10.10.0.0/16  |
| Total IPv4 Addresses                 | 65,536        |
| Public Subnets                       | 2             |
| Private Subnets                      | 2             |
| Availability Zones                   | 2             |
| CIDR per Subnet                      | /24           |
| Total IPv4 Addresses per Subnet      | 256           |
| AWS Usable IPv4 Addresses per Subnet | 251           |

---

# References

* AWS VPC User Guide: [https://docs.aws.amazon.com/vpc/](https://docs.aws.amazon.com/vpc/)
* CIDR Calculator: [https://cidr.xyz/](https://cidr.xyz/)

---

### Note

* AWS reserves **5 IP addresses per subnet**, **not per VPC**.
* `/16` provides **65,536 IPv4 addresses**.
* `/24` provides **256 total** and **251 usable** IPv4 addresses in AWS.
* The subnet mask and CIDR calculations are correct.
* The reserved IP address explanations match the AWS VPC documentation.
