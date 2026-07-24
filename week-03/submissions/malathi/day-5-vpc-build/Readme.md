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

<img width="2231" height="990" alt="image" src="https://github.com/user-attachments/assets/86a8ab47-585b-40bd-b2d3-9b2816d1d180" />


### 2. Subnets Created

<img width="2545" height="462" alt="image" src="https://github.com/user-attachments/assets/6d11cbf4-8257-423d-b82f-cbb0907a6ad5" />


### 3. Internet Gateway Attached

<img width="2537" height="677" alt="image" src="https://github.com/user-attachments/assets/0febe2b7-27df-4cf1-829e-690cd8bce17c" />


### 4. Main Route Table

<img width="2225" height="651" alt="image" src="https://github.com/user-attachments/assets/c825bee6-44bd-43bd-b644-48d8c590b09e" />


### 5. Public Route Table

<img width="2542" height="862" alt="image" src="https://github.com/user-attachments/assets/f867e70c-a384-46b4-bd75-e5907d85abd1" />


### 6. Private Route Table

<img width="2530" height="762" alt="image" src="https://github.com/user-attachments/assets/dbc9f9c6-a3a7-4819-8145-3c2e141a6713" />
<img width="2490" height="632" alt="image" src="https://github.com/user-attachments/assets/eb1e9459-5814-4d86-91cc-b29168f5ca02" />

<img width="2502" height="927" alt="image" src="https://github.com/user-attachments/assets/ad7d72e7-07ac-4264-8636-bf37b45ffda0" />
<img width="2520" height="757" alt="image" src="https://github.com/user-attachments/assets/760ac900-1768-4818-97ee-ea32ef617636" />



### 7. VPC Resource Map

<img width="2180" height="755" alt="image" src="https://github.com/user-attachments/assets/6132fc53-0423-4e4c-8d5a-f8507b889d07" />


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

