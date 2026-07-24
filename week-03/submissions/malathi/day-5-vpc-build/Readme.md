# Week 3 - Day 5: Amazon VPC Part 1

## Name

Malathi Shetty

---

## Tasks Completed

* [x] Watched/read the weekly content
* [x] Completed hands-on labs
* [x] Built a custom VPC from scratch
* [x] Added screenshots/proof
* [x] Documented architecture decisions
* [x] Posted learning update on LinkedIn

---

# Architecture

![VPC Architecture](diagrams/week-03-vpc-two-az.drawio.png)

---

# Architecture Decisions

## Why separate Public and Private Subnets?

Public and private subnets separate internet-facing resources from internal workloads.

* **Public subnets** are used for resources that require direct internet access, such as web servers or load balancers.
* **Private subnets** are used for internal workloads such as application servers and databases where direct internet exposure is not required.

This separation improves security by limiting direct internet access only to required resources.

---

## Why use separate Route Tables?

Separate route tables allow different traffic routing behavior for public and private workloads.

### Public Route Table

Contains:

```
10.10.0.0/16 → local
0.0.0.0/0 → Internet Gateway
```

This allows resources in public subnets to communicate with the internet.

---

### Private Route Table

Contains:

```
10.10.0.0/16 → local
```

Private resources do not have direct internet access.

---

## Why deploy resources across two Availability Zones?

Resources are distributed across two Availability Zones to improve:

* Availability
* Fault tolerance
* Disaster recovery capability

If one Availability Zone experiences an issue, workloads in another AZ can continue running.

---

## Why use /16 VPC CIDR with /24 Subnets?

The VPC uses:

```
10.10.0.0/16
```

because it provides a large address space for future expansion.

Each subnet uses:

```
/24
```

which provides enough IP addresses for individual workload tiers while keeping subnet planning simple.

---

## Why keep the Main Route Table local-only?

The main route table was kept with only:

```
10.10.0.0/16 → local
```

Dedicated public and private route tables were explicitly associated with subnets.

This makes routing behavior predictable and avoids accidental internet exposure.

---

# CIDR Plan

| Resource  | CIDR Block      | Total Addresses | AWS Usable Addresses |
| --------- | --------------- | --------------: | -------------------: |
| VPC       | `10.10.0.0/16`  |          65,536 |               65,531 |
| Public-A  | `10.10.1.0/24`  |             256 |                  251 |
| Public-B  | `10.10.2.0/24`  |             256 |                  251 |
| Private-A | `10.10.11.0/24` |             256 |                  251 |
| Private-B | `10.10.12.0/24` |             256 |                  251 |

All subnet CIDRs are:

* Within the VPC CIDR range
* Non-overlapping
* Planned for future expansion

---

# Public vs Private Subnet

A subnet becomes public when:

* Its route table has:

```
0.0.0.0/0 → Internet Gateway
```

* Instances can receive public IPv4 addresses.

---

A subnet becomes private when:

* It does not have an Internet Gateway route.
* It contains only local VPC routing.
* Instances do not receive public IPv4 addresses.

> A subnet name does not decide whether it is public or private. The route table association decides.

---

# Result

Successfully created a two Availability Zone VPC architecture.

## Resources Created

### VPC

```
cloudadhar-day5-vpc
CIDR: 10.10.0.0/16
```

---

### Subnets

| Subnet               | CIDR          | AZ         | Type    |
| -------------------- | ------------- | ---------- | ------- |
| cloudadhar-public-a  | 10.10.1.0/24  | us-west-2a | Public  |
| cloudadhar-private-a | 10.10.11.0/24 | us-west-2a | Private |
| cloudadhar-public-b  | 10.10.2.0/24  | us-west-2b | Public  |
| cloudadhar-private-b | 10.10.12.0/24 | us-west-2b | Private |

---

### Internet Gateway

```
cloudadhar-day5-igw
```

Attached successfully to the VPC.

---

### Route Tables

Main Route Table:

```
cloudadhar-main-rt-local-only
```

Local route only.

---

Public Route Table:

```
cloudadhar-public-rt
```

Routes:

```
10.10.0.0/16 → local
0.0.0.0/0 → Internet Gateway
```

Associated with public subnets.

---

Private Route Table:

```
cloudadhar-private-rt
```

Route:

```
10.10.0.0/16 → local
```

Associated with private subnets.

---

# Validation Completed

✅ VPC created successfully
✅ Four subnets created across two AZs
✅ Public subnet internet routing verified
✅ Private subnet isolation verified
✅ Route table associations verified
✅ VPC Resource Map checked

---

# Screenshots

### 1. VPC Created

![VPC Created](screenshots/01_VPC_Created.png)

### 2. Subnets Created

![Subnets Created](screenshots/02_Subnets_Created.png)

### 3. Internet Gateway Attached

![Internet Gateway](screenshots/03_Internet_Gateway_Attached.png)

### 4. Main Route Table

![Main Route Table](screenshots/04_Main_Route_Table.png)

### 5. Public Route Table

![Public Route Table](screenshots/05_Public_Route_Table.png)

### 6. Private Route Table

![Private Route Table](screenshots/06_Private_Route_Table.png)

### 7. VPC Resource Map

![Resource Map](screenshots/07_AWS_VPC_Resource_Map.png)

---

# Where I Got Stuck

Initially I worked with the default VPC route table instead of the custom VPC route table.

After checking VPC IDs and route table associations, I corrected the configuration and continued with the custom VPC.

---

# Cleanup

Resources cleaned after validation:

1. Deleted subnet associations.
2. Deleted custom subnets.
3. Deleted public and private route tables.
4. Detached Internet Gateway.
5. Deleted Internet Gateway.
6. Deleted custom VPC.

---

# LinkedIn Post

(Add your Day 5 LinkedIn URL)

---

