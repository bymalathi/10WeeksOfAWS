**Important:** Since **NAT Gateway** and **Interface Endpoints** cost money, don't create them until you're ready, and delete them when finished.

---

# Before Part 1 – Let's Check What You Already Have

Before creating anything, we need to make sure Day 5 resources still exist.

## Step 1: Verify your AWS account

Open **CloudShell** (or your terminal if AWS CLI is configured).

Run:

```bash
aws sts get-caller-identity
```

You should see something like:

```json
{
  "UserId": "...",
  "Account": "123456789012",
  "Arn": "arn:aws:iam::123456789012:..."
}
```

### Why?

This confirms:

* ✅ AWS CLI works
* ✅ You're logged into the correct account
* ✅ Credentials are valid

---

## Step 2: Check your Region

Run:

```bash
echo $AWS_REGION
```

or

```bash
echo $REGION
```

If nothing appears, run:

```bash
export REGION=ap-south-1
```

Then verify:

```bash
echo $REGION
```

Expected:

```text
ap-south-1
```

---

## Step 3: Confirm the VPC exists

Open the AWS Console.

Go to:

**VPC → Your VPCs**

Look for:

```
cloudadhar-day5-vpc
```

Do you see it?

✅ Yes → Continue.

---

## Step 4: Confirm the subnets

Go to:

**VPC → Subnets**

You should have four subnets:

```
cloudadhar-public-a

cloudadhar-public-b

cloudadhar-private-a

cloudadhar-private-b
```

---

## Step 5: Confirm the Internet Gateway

Go to:

**VPC → Internet Gateways**

You should see one attached to your VPC.

Something like:

```
cloudadhar-day5-igw
```

Status:

```
Attached
```

---

## Step 6: Confirm Route Tables

Go to:

**VPC → Route Tables**

You should already have:

* Public Route Table
* Main Route Table (default)
* (Private route table will be created in Part 1)

Open the **Public Route Table**.

Look under **Routes**.

You should see:

| Destination  | Target           |
| ------------ | ---------------- |
| 10.10.0.0/16 | local            |
| 0.0.0.0/0    | Internet Gateway |

This is important because the NAT Gateway will rely on this route to reach the internet.

***

# Part 1 – Create NAT Gateway

## First, remember WHY we're doing this.

Yesterday, your network looked like this:

```text
                    Internet
                        |
                       IGW
                        |
        -------------------------------
        |       Public Subnet A       |
        |                             |
        -------------------------------
                |
        -------------------------------
        |      Private Subnet A       |
        |        (No Internet)        |
        -------------------------------
```

Your **Private EC2 cannot reach the Internet**.

Today we'll build this:

```text
                    Internet
                        |
                       IGW
                        |
        -------------------------------
        |      Public Subnet A        |
        |                             |
        |      NAT Gateway            |
        -------------------------------
                |
        -------------------------------
        |      Private Subnet A       |
        |            EC2              |
        -------------------------------
```

Now the EC2 can go **out** to the internet.

---

# Step 1 – Open NAT Gateways

Go to

**AWS Console**

↓

**VPC**

↓

**NAT Gateways**

You'll probably see:

```text
No NAT Gateways
```

That's expected.

---

# Step 2 – Click Create NAT Gateway

Click

```text
Create NAT Gateway
```

You'll see a form.

Let's fill it carefully.

---

# Step 3 – Name

Name tag

Enter

```text
cloudadhar-day6-nat-a
```

### Why?

Just a friendly name.

AWS identifies the NAT by its ID, but names make it easy for us.

---

# Step 4 – Select Subnet ⭐⭐⭐

This is VERY important.

Choose

```text
cloudadhar-public-a
```

NOT

```text
cloudadhar-private-a
```

## Why?

Remember our story?

The NAT Gateway must be able to talk to the Internet.

Only a **Public Subnet** has a route to the Internet Gateway.

So NAT **must** live in a Public Subnet.

---

# Step 5 – Connectivity Type

You'll see

```text
Connectivity Type

○ Public

○ Private
```

Choose

✅ **Public**

## Why?

Public NAT Gateway

* Uses an Elastic IP
* Can access the Internet
* Used for private subnet internet access

Private NAT Gateway is for specialized networking scenarios and **not** this lab.

---

# Step 6 – Elastic IP ⭐⭐⭐

You'll see

```text
Elastic IP Allocation ID
```

Click

```text
Allocate Elastic IP
```

AWS creates one.

### What is an Elastic IP again?

Think of it as

> NAT Gateway's permanent public phone number.

Without it,

the Internet wouldn't know where to send replies.

---

# Step 7 – Create NAT Gateway

Click

```text
Create NAT Gateway
```

---

# Step 8 – Wait

Status will be

```text
Pending
```

Do **not** continue yet.

Wait until it changes to

```text
Available
```

This may take **2–5 minutes**.

---

# While Waiting – Let's Understand What AWS Is Doing

AWS is creating:

```text
Public Subnet

↓

NAT Gateway

↓

Elastic IP
```

The NAT Gateway now knows how to:

* Receive traffic from your private subnet.
* Send it to the Internet through the Internet Gateway.
* Return the response back to the private instance.

Notice something important:

The **Private EC2 still does not have a public IP**.

The NAT Gateway is the only thing talking to the Internet.


# Wait till the status becomes "Available"

<img width="2542" height="742" alt="image" src="https://github.com/user-attachments/assets/883a7bb6-0b51-4bec-acbe-8aa84e6471f0" />


***

Now the NAT exists, **but it's not doing anything yet.**

This is one of the biggest beginner mistakes:

> **Creating a NAT Gateway does NOT automatically give the private subnet internet access.**

Why?

Because the private subnet still doesn't know **where to send internet traffic**.

Think of it like this:

You hired a delivery boy (NAT), but you forgot to tell your family **"If you need anything from outside, call this delivery boy."**

So now we have to tell the **Private Subnet**.

---

# Part 1 – Step 2: Create Private Route Table

## What is a Route Table again?

Think of it as **Google Maps**.

Whenever an EC2 wants to go somewhere, it first asks:

> "Which road should I take?"

The Route Table answers.

---

## Current Situation

Your Private-A subnet is probably using the **Main Route Table**.

Let's verify.

Go to:

**VPC → Subnets**

↓

Click

```text
cloudadhar-private-a
```

↓

Open the **Route Table** tab.



### Question:

What Route Table is associated?

It may show something like:

```text
Main Route Table
```

or another name.

This is normal.

<img width="2542" height="990" alt="image" src="https://github.com/user-attachments/assets/a44f8183-fcd9-405c-96b5-9aea6e059e10" />


---

# Step 3 – Create a New Route Table

Go to:

**VPC → Route Tables**

↓

Click

```text
Create Route Table
```

Fill in:

### Name

```text
cloudadhar-private-a-rt
```

### VPC

Choose

```text
cloudadhar-day5-vpc
```

Click

```text
Create Route Table
```

<img width="2522" height="770" alt="image" src="https://github.com/user-attachments/assets/110c6945-7a18-4ac3-87fb-9ba5e7b3ba90" />


---

# Why create a new Route Table?

Because only **Private-A** should use the NAT.

The assignment specifically says:

> **Do not add a NAT route to Private-B** in this learner lab.

So we'll make a dedicated Route Table just for **Private-A**.

---

# Step 4 – Associate it with Private-A

Open your new Route Table.

Go to:

**Subnet Associations**

↓

Click

```text
Edit subnet associations
```

Select ONLY

```text
☑ cloudadhar-private-a
```

Do **NOT** select:

```text
☐ cloudadhar-private-b
```

Save.

<img width="2537" height="675" alt="image" src="https://github.com/user-attachments/assets/2c505152-f963-49e3-8cd1-9dd9ed5e2883" />
<img width="2536" height="962" alt="image" src="https://github.com/user-attachments/assets/d7966af1-7549-42ba-9f2d-59e93244998e" />


---

# Why only Private-A?

Because today's lab is intentionally **cost-safe**.

We'll learn about NAT-B later.

For now:

```text
Private-A ✅ Internet via NAT

Private-B ❌ No Internet
```

This helps you clearly see the difference between the two subnets.

---

# Step 5 – Add the NAT Route

Now open the **Routes** tab.

You'll already see:

| Destination    | Target |
| -------------- | ------ |
| `10.10.0.0/16` | local  |

<img width="2532" height="626" alt="image" src="https://github.com/user-attachments/assets/191fbba1-3b01-4b0b-b239-bacd4db13db6" />


Do **not** remove it.

Click

```text
Edit Routes
```

↓

Add another route:

| Destination | Target                                         |
| ----------- | ---------------------------------------------- |
| `0.0.0.0/0` | **Your NAT Gateway (`cloudadhar-day6-nat-a`)** |

Save.

<img width="2527" height="531" alt="image" src="https://github.com/user-attachments/assets/b365bf42-a2d3-47bb-92f4-93a128e3294a" />
<img width="2107" height="607" alt="image" src="https://github.com/user-attachments/assets/ec42f973-0987-4f8b-acc9-0eaeb94cddd1" />


---

# Why `0.0.0.0/0`?

Remember from Day 5:

* `10.10.0.0/16` = Stay inside the VPC.
* `0.0.0.0/0` = Anywhere outside the VPC (the internet).

So now the Route Table says:

```text
If destination is inside VPC
    ↓
Use local route

Else
    ↓
Send to NAT Gateway
```

---

# Let's Check Your Understanding 🧠

Imagine your Private EC2 wants to open:

```text
https://aws.amazon.com
```

What happens?

```text
Private EC2
      │
      ▼
Private Route Table
      │
      ▼
0.0.0.0/0 matches
      │
      ▼
NAT Gateway
      │
      ▼
Public Route Table
      │
      ▼
Internet Gateway
      │
      ▼
Internet
```

Notice:

**The Route Table doesn't send traffic directly to the Internet Gateway.**

It sends it to the **NAT Gateway first**, and the NAT Gateway uses the **Public Subnet's Route Table** (which already has a route to the Internet Gateway) to reach the internet.

***

You've now completed the networking part.

Your architecture now looks like this:

```text
                    Internet
                        ▲
                        │
               Internet Gateway
                        ▲
                        │
        ┌───────────────────────────┐
        │      Public Subnet A      │
        │                           │
        │  NAT Gateway + Elastic IP │
        └───────────────────────────┘
                        ▲
                        │
     Private Route Table (0.0.0.0/0 → NAT)
                        ▲
                        │
        ┌───────────────────────────┐
        │      Private Subnet A     │
        │      (EC2 will go here)   │
        └───────────────────────────┘
```

Now we'll prove that it actually works.

---

# Part 2 – Launch a Private EC2

Let's understand the goal first.

We want an EC2 that:

✅ Has NO Public IP

✅ Cannot be accessed from the Internet

✅ Can access the Internet through NAT

This is exactly how production private servers work.

---

# Step 1 – Go to EC2

AWS Console

↓

**EC2**

↓

**Launch Instance**

---

# Step 2 – Name

Enter

```text
cloudadhar-day6-private-ec2
```

---

# Step 3 – AMI

Choose

```text
Amazon Linux 2023
```

Why?

Because the lab says so, and it's lightweight and supports Session Manager.

---

# Step 4 – Instance Type

Choose

```text
t2.micro
```

(if available under Free Tier)

or

```text
t3.micro
```

if your lab specifically uses it.

---

# Step 5 – Key Pair

### Does the lab ask us to SSH?

No.

It says:

> Connect through **Session Manager**.

So if your account allows launching without a key pair, select:

```text
Proceed without a key pair
```

If AWS requires one, use an existing key pair—you won't actually SSH into this instance for the lab.

---

# Step 6 – Network ⭐⭐⭐

Click **Edit** in the Network settings.

Fill in:

### VPC

Choose

```text
cloudadhar-day5-vpc
```

---

### Subnet

Choose

```text
cloudadhar-private-a
```

NOT Public-A.

---

### Auto-assign Public IP

This is VERY IMPORTANT.

Choose

```text
Disable
```

### Why?

Because we want to prove NAT works.

If the EC2 had a public IP, it could use the Internet directly, and we wouldn't know whether NAT was working.

---

# Step 7 – Security Group

The instructions say:

> Use a Security Group with no inbound rule and required outbound access.

Create a new Security Group.

Name:

```text
cloudadhar-day6-private-sg
```

Inbound Rules:

**None**

Leave it empty.

Outbound:

Keep the default:

```text
All traffic → 0.0.0.0/0
```

### Why no inbound?

Because we'll use **Session Manager**, not SSH.

The EC2 should not accept direct Internet connections.

---

# Step 8 – IAM Role ⭐⭐⭐

This is the most important part.

The instructions say:

> Attach a role that supports Session Manager.

Question:

### Did you already create an IAM Role for Session Manager in a previous lab?

For example, a role with:

```text
AmazonSSMManagedInstanceCore
```

attached?

Or do you **not** have one yet?

***

# Step 1 – Open IAM Roles

Go to

**AWS Console**

↓

**IAM**

↓

**Roles**

↓

Click

```text
Create role
```

---

# Step 2 – Trusted Entity

You'll see

```text
Trusted entity type
```

Choose

✅ **AWS service**

Then

```text
Use case
```

Choose

✅ **EC2**

It should look like:

```text
Trusted Entity
--------------
AWS Service

Use Case
--------
EC2
```

Click

```text
Next
```

<img width="2541" height="1144" alt="image" src="https://github.com/user-attachments/assets/5f5ba1cf-0f81-4d59-8530-6606dbe11651" />


---

# Why EC2?

Remember our story?

An IAM **Role** is like an **ID card**.

Who is going to use this ID card?

👉 The **EC2 instance**.

So we trust EC2 to assume this role.

---

# Step 3 – Add Permissions

You'll see a search box.

Search for:

```text
AmazonSSMManagedInstanceCore
```

Tick the checkbox.

✅ Select it.

Do **not** select random policies with similar names.

It should be exactly:

```text
AmazonSSMManagedInstanceCore
```

Click

```text
Next
```

<img width="2556" height="672" alt="image" src="https://github.com/user-attachments/assets/0ae8008e-9a8c-4eab-8e06-42cb12f1ec3c" />


---

# Why this policy?

It allows the EC2 instance to communicate with **AWS Systems Manager (SSM)**.

Without it:

❌ Session Manager won't work.

With it:

✅ You can open a terminal in your browser **without SSH**, **without port 22**, and **without a public IP**.

---

# Step 4 – Name the Role

Role name:

```text
cloudadhar-day6-ssm-role
```

Description (optional):

```text
Allows EC2 to connect using AWS Systems Manager
```

Click

```text
Create role
```

<img width="2555" height="1085" alt="image" src="https://github.com/user-attachments/assets/8e004df1-d11e-41c0-a02a-15f10393a68b" />
<img width="2552" height="1007" alt="image" src="https://github.com/user-attachments/assets/d57c0d0f-126a-4728-9a50-5c104b62d536" />


---

# 🎉 Done!

You now have an IAM Role.

---

## Mini Revision

What did we just create?

```
EC2
   │
   ▼
IAM Role
   │
   ▼
AmazonSSMManagedInstanceCore Policy
   │
   ▼
AWS Systems Manager
```

This means:

* No Public IP needed ✅
* No SSH needed ✅
* No Port 22 needed ✅

This is how many production AWS environments are managed.

***

Now comes the fun part—we're finally going to launch the EC2 that proves your NAT Gateway works.

We'll go **slowly**.

---

# Part 2 – Launch Private EC2

---

## Step 1 – Go to EC2

AWS Console

↓

**EC2**

↓

**Launch Instance**

---

# Step 2 – Name

Enter:

```text
cloudadhar-day6-private-ec2
```

---

# Step 3 – AMI

Choose:

```text
Amazon Linux 2023
```

---

# Step 4 – Instance Type

Choose:

```text
t2.micro
```

(or `t3.micro` if that's what your lab uses)

---

# Step 5 – Key Pair

Since we're using **Session Manager**, not SSH:

If AWS allows it, choose:

```text
Proceed without a key pair
```

If your account requires a key pair, use an existing one. We won't use SSH in this lab.

---

# Step 6 – Network Settings ⭐⭐⭐

Click **Edit**.

Now fill these carefully.

### VPC

Choose:

```text
cloudadhar-day5-vpc
```

---

### Subnet

Choose:

```text
cloudadhar-private-a
```

---

### Auto-assign Public IP

Choose:

```text
Disable
```

### Why?

This is the entire point of today's lab.

We want to prove:

```text
Private EC2
      │
      ▼
NAT Gateway
      │
      ▼
Internet
```

If the EC2 gets a Public IP, it can bypass the NAT, and the experiment is meaningless.

---

# Step 7 – Security Group ⭐⭐⭐

Choose:

**Create Security Group**

Name:

```text
cloudadhar-day6-private-sg
```

### Inbound Rules

Leave **empty**.

No SSH.

No HTTP.

Nothing.

### Outbound Rules

Leave the default:

```text
All Traffic
Destination: 0.0.0.0/0
```

---

### Why no inbound?

Because we're not allowing anyone from the internet to connect.

We'll use **AWS Systems Manager** instead.

---

# Step 8 – Advanced Details ⭐⭐⭐

Scroll all the way down.

Expand:

```text
Advanced Details
```

Find:

```text
IAM Instance Profile
```

Choose:

```text
cloudadhar-day6-ssm-role
```

(the role you created)

---

### Why?

Without this role:

❌ Session Manager cannot connect.

With it:

✅ AWS can securely open a terminal to your private EC2.

---

# Step 9 – Launch

Click:

```text
Launch Instance
```

Wait until:

```text
Running
```

---

# Step 10 – Verify the Instance

Click the instance.

Now check these things.

### Public IPv4

It should show:

```text
—
```

or

```text
None
```

There should **not** be a public IP address.

✅ Good.

---

### Private IPv4

It should show something like:

```text
10.10.11.x
```

(or whatever your Private-A subnet range is)

---

### IAM Role

On the Details tab, verify the instance profile is:

```text
cloudadhar-day6-ssm-role
```

---

# 🚦 STOP HERE

<img width="2560" height="7304" alt="image" src="https://github.com/user-attachments/assets/7a111e61-4c9a-48e6-aab2-f8509812b6b6" />

***


Now comes the moment we've been building toward:

> **Can a Private EC2 (with NO Public IP) access the internet?**

If this works, your NAT Gateway is configured correctly.

---

# Step 11 – Connect Using Session Manager

## First, let's understand what Session Manager is.

Normally people connect like this:

```text
Laptop
   │
 SSH (Port 22)
   │
EC2
```

That requires:

* Public IP ❌
* Port 22 open ❌
* Key Pair ❌

Today we're doing this:

```text
Laptop
   │
AWS Systems Manager
   │
Private EC2
```

Notice:

* No Public IP ✅
* No SSH ✅
* No Port 22 ✅

This is much more secure.

---

# Step 12 – Open Session Manager

Go to:

**EC2**

↓

Select your instance

↓

Click

```text
Connect
```

You'll see multiple tabs.

Choose:

```text
Session Manager
```

Then click:

```text
Connect
```

---

## Question:

Did it open a terminal?

You should see something like:

```bash
sh-5.2$
```

or

```bash
[ec2-user@ip-10-10-11-xx ~]$
```

---

# ❗If it DOESN'T connect

Tell me the exact error message.

Common reasons are:

* SSM Agent not ready yet (wait 2–3 minutes)
* IAM role not attached correctly
* Missing VPC endpoint/NAT connectivity
* Instance not registered with Systems Manager yet

Don't troubleshoot yet—just tell me the exact error if you get one.

---

# If the terminal opens

Run this first:

```bash
curl -I https://aws.amazon.com
```

### What should happen?

You should see something similar to:

```text
HTTP/2 200
```

or

```text
HTTP/1.1 200 OK
```

This proves:

```text
Private EC2
      │
      ▼
NAT Gateway
      │
      ▼
Internet
      │
      ▼
aws.amazon.com
```

---

## Next command

Run:

```bash
aws sts get-caller-identity
```

You should get JSON like:

```json
{
  "UserId": "...",
  "Account": "...",
  "Arn": "..."
}
```

### Why?

This proves:

* AWS CLI works
* The IAM role is attached correctly
* The instance can reach AWS APIs

---

# 🧠 What just happened?

Let's trace the first command.

You typed:

```bash
curl -I https://aws.amazon.com
```

The network path was:

```text
Private EC2
      │
      ▼
Private Route Table
      │
      ▼
0.0.0.0/0
      │
      ▼
NAT Gateway
      │
      ▼
Internet Gateway
      │
      ▼
Internet
      │
      ▼
aws.amazon.com
```

The reply came back along the same path.

Notice:

**The EC2 still does NOT have a public IP.**

The NAT Gateway is doing all the talking to the internet on its behalf.

***



Excellent! 🎉 You're doing great.

Now comes the moment we've been building toward:

> **Can a Private EC2 (with NO Public IP) access the internet?**

If this works, your NAT Gateway is configured correctly.

---

# Step 11 – Connect Using Session Manager

## First, let's understand what Session Manager is.

Normally people connect like this:

```text
Laptop
   │
 SSH (Port 22)
   │
EC2
```

That requires:

* Public IP ❌
* Port 22 open ❌
* Key Pair ❌

Today we're doing this:

```text
Laptop
   │
AWS Systems Manager
   │
Private EC2
```

Notice:

* No Public IP ✅
* No SSH ✅
* No Port 22 ✅

This is much more secure.

---

# Step 12 – Open Session Manager

Go to:

**EC2**

↓

Select your instance

↓

Click

```text
Connect
```

You'll see multiple tabs.

Choose:

```text
Session Manager
```

Then click:

```text
Connect
```

---

## Question:

Did it open a terminal?

You should see something like:

```bash
sh-5.2$
```

or

```bash
[ec2-user@ip-10-10-11-xx ~]$
```

---

# ❗If it DOESN'T connect

Tell me the exact error message.

Common reasons are:

* SSM Agent not ready yet (wait 2–3 minutes)
* IAM role not attached correctly
* Missing VPC endpoint/NAT connectivity
* Instance not registered with Systems Manager yet

Don't troubleshoot yet—just tell me the exact error if you get one.

---

# If the terminal opens

Run this first:

```bash
curl -I https://aws.amazon.com
```

### What should happen?

You should see something similar to:

```text
HTTP/2 200
```

or

```text
HTTP/1.1 200 OK
```

This proves:

```text
Private EC2
      │
      ▼
NAT Gateway
      │
      ▼
Internet
      │
      ▼
aws.amazon.com
```

---

## Next command

Run:

```bash
aws sts get-caller-identity
```

You should get JSON like:

```json
{
  "UserId": "...",
  "Account": "...",
  "Arn": "..."
}
```

### Why?

This proves:

* AWS CLI works
* The IAM role is attached correctly
* The instance can reach AWS APIs

---

# 🧠 What just happened?

Let's trace the first command.

You typed:

```bash
curl -I https://aws.amazon.com
```

The network path was:

```text
Private EC2
      │
      ▼
Private Route Table
      │
      ▼
0.0.0.0/0
      │
      ▼
NAT Gateway
      │
      ▼
Internet Gateway
      │
      ▼
Internet
      │
      ▼
aws.amazon.com
```

The reply came back along the same path.

Notice:

**The EC2 still does NOT have a public IP.**

The NAT Gateway is doing all the talking to the internet on its behalf.

***

Now comes the moment we've been building toward:

> **Can a Private EC2 (with NO Public IP) access the internet?**

If this works, your NAT Gateway is configured correctly.

---

# Step 11 – Connect Using Session Manager

## First, let's understand what Session Manager is.

Normally people connect like this:

```text
Laptop
   │
 SSH (Port 22)
   │
EC2
```

That requires:

* Public IP ❌
* Port 22 open ❌
* Key Pair ❌

Today we're doing this:

```text
Laptop
   │
AWS Systems Manager
   │
Private EC2
```

Notice:

* No Public IP ✅
* No SSH ✅
* No Port 22 ✅

This is much more secure.

---

# Step 12 – Open Session Manager

Go to:

**EC2**

↓

Select your instance

↓

Click

```text
Connect
```

You'll see multiple tabs.

Choose:

```text
Session Manager
```

Then click:

```text
Connect
```

<img width="2511" height="841" alt="image" src="https://github.com/user-attachments/assets/5f0177f4-9057-461f-9708-1834dbd6245b" />


---

## Question:

Did it open a terminal?

You should see something like:

```bash
sh-5.2$
```

or

```bash
[ec2-user@ip-10-10-11-xx ~]$
```

<img width="2557" height="167" alt="image" src="https://github.com/user-attachments/assets/2de53503-119c-40d6-92e4-5f5104b62b05" />


---

# ❗If it DOESN'T connect

Tell me the exact error message.

Common reasons are:

* SSM Agent not ready yet (wait 2–3 minutes)
* IAM role not attached correctly
* Missing VPC endpoint/NAT connectivity
* Instance not registered with Systems Manager yet

Don't troubleshoot yet—just tell me the exact error if you get one.

---

# If the terminal opens

Run this first:

```bash
curl -I https://aws.amazon.com
```

### What should happen?

You should see something similar to:

```text
HTTP/2 200
```

or

```text
HTTP/1.1 200 OK
```

This proves:

```text
Private EC2
      │
      ▼
NAT Gateway
      │
      ▼
Internet
      │
      ▼
aws.amazon.com
```

<img width="2305" height="442" alt="image" src="https://github.com/user-attachments/assets/e260e675-2bfc-49bf-8f05-9fcaa882dc97" />


---

## Next command

Run:

```bash
aws sts get-caller-identity
```

You should get JSON like:

```json
{
  "UserId": "...",
  "Account": "...",
  "Arn": "..."
}
```

<img width="1137" height="155" alt="image" src="https://github.com/user-attachments/assets/c0bba8af-8b6b-470d-bebe-927a13a90bb8" />


### Why?

This proves:

* AWS CLI works
* The IAM role is attached correctly
* The instance can reach AWS APIs

---

# 🧠 What just happened?

Let's trace the first command.

You typed:

```bash
curl -I https://aws.amazon.com
```

The network path was:

```text
Private EC2
      │
      ▼
Private Route Table
      │
      ▼
0.0.0.0/0
      │
      ▼
NAT Gateway
      │
      ▼
Internet Gateway
      │
      ▼
Internet
      │
      ▼
aws.amazon.com
```

The reply came back along the same path.

Notice:

**The EC2 still does NOT have a public IP.**

The NAT Gateway is doing all the talking to the internet on its behalf.

***


# What did we prove?

Your EC2 has:

✅ No Public IP

✅ No inbound Security Group rules

✅ Connected through Session Manager

✅ Can access the Internet

At first glance, this seems impossible.

> "How can a machine with NO Public IP reach the Internet?"

The answer is:

**NAT Gateway.**

---

# Let's trace your `curl` command

You typed:

```bash
curl -I https://aws.amazon.com
```

Here's the journey.

## Step 1

Your EC2 created an HTTPS request.

```text
Private EC2

"I want aws.amazon.com"
```

---

## Step 2

The EC2 checked its Route Table.

It asked:

> "Where should I send traffic for aws.amazon.com?"

The destination is **not inside your VPC**, so it matched:

```text
0.0.0.0/0
        ↓
NAT Gateway
```

---

## Step 3

Traffic went to the NAT Gateway.

```text
Private EC2
      │
      ▼
NAT Gateway
```

---

## Step 4

The NAT Gateway is inside the **Public Subnet**.

That subnet already has:

```text
0.0.0.0/0
      ↓
Internet Gateway
```

So the NAT Gateway sent the request to the Internet.

```text
Private EC2
      │
      ▼
NAT Gateway
      │
      ▼
Internet Gateway
      │
      ▼
aws.amazon.com
```

---

## Step 5

AWS replied.

You received:

```text
HTTP/2 200
```

What does **200** mean?

It means:

> "Success."

The website was reached successfully.

---

# What did `curl -I` do?

Notice you used:

```bash
curl -I
```

Not

```bash
curl
```

`-I` means:

> "Only give me the HTTP headers."

Instead of downloading the whole webpage, it just asked:

> "Are you there?"

AWS replied:

```text
HTTP/2 200
```

That's enough to prove connectivity.

---

# Now let's understand the second command.

You ran:

```bash
aws sts get-caller-identity
```

Output:

```json
{
    "Account": "138852020826",
    "Arn": "arn:aws:sts::138852020826:assumed-role/cloudadhar-day6-ssm-role/i-07f9714be3c1092f6"
}
```

Let's read it.

---

## `"assumed-role"`

This is VERY important.

It does **NOT** say:

```text
IAM User
```

It says:

```text
assumed-role
```

Why?

Because your EC2 isn't using an IAM User.

It's using the IAM Role you created:

```text
cloudadhar-day6-ssm-role
```

Remember creating it?

```
EC2
   │
   ▼
IAM Role
   │
   ▼
AmazonSSMManagedInstanceCore
```

Now you have proof that it's attached correctly.

---

## `"i-07f9714be3c1092f6"`

This part is your EC2 Instance ID.

AWS is saying:

> This EC2 instance assumed the role.

Exactly what we wanted.

---

# One Amazing Thing Happened (You Didn't Notice 😄)

Look carefully.

Did you ever run:

```bash
aws configure
```

inside this EC2?

No.

Did you ever enter:

* Access Key
* Secret Key

No.

So how did AWS CLI authenticate?

Because the EC2 automatically got **temporary credentials** from the IAM Role.

Remember **Day 3**?

We learned:

```
EC2
    │
Instance Profile
    │
IAM Role
    │
AWS STS
    │
Temporary Credentials
```

Today you actually **used** that concept without typing any credentials.

Everything is connected!

---

# Congratulations 🎉

You have successfully proven all of these:

✅ Private EC2

✅ No Public IP

✅ NAT Gateway works

✅ Route Table is correct

✅ Internet Gateway works

✅ Session Manager works

✅ IAM Role works

✅ STS temporary credentials work

This is exactly what the Day 6 Part 2 lab wanted.

---

# Before Part 3 (Security Group vs NACL)

Let's quickly verify your architecture.

```
Internet
    ▲
    │
Internet Gateway
    ▲
    │
Public Route Table
    ▲
    │
NAT Gateway
    ▲
    │
Private Route Table
    ▲
    │
Private EC2
```

***



### Why can't the Private EC2 send traffic directly to the Internet Gateway?

Now let's understand **why**.

---

# Imagine this

Your Private EC2 says:

> "I want to visit Google."

Can it go directly to the Internet Gateway (IGW)?

❌ **No.**

Why?

Because an **Internet Gateway only works with resources that have a public IP address**.

Your Private EC2 has:

```text
Private IP: 10.10.11.25
Public IP: None
```

The Internet doesn't know how to reach `10.10.11.25` because it's a **private IP**, and private IPs are **not routable on the public Internet**.

So if the EC2 tried this:

```text
Private EC2
      │
      ▼
Internet Gateway
      │
      ▼
Internet
```

The request would fail because the source IP is private.

---

# What does the NAT Gateway do?

The NAT Gateway says:

> "I'll send the request using **my own public IP (Elastic IP)**."

Think of it like this.

### Without NAT

```text
Private EC2

"I want Google."

IGW says:

❌ Sorry.
You don't have a public address.
```

---

### With NAT

```text
Private EC2
      │
      ▼
NAT Gateway

"I'll send it for you."

      │
      ▼
Internet Gateway
      │
      ▼
Google
```

Google replies to the NAT Gateway's **Elastic IP**, and the NAT Gateway sends the response back to the Private EC2.

---

Say this:

> **"The Private EC2 cannot use the Internet Gateway directly because it has no public IP address.
> The NAT Gateway, which has an Elastic IP in the public subnet, sends the outbound traffic to the Internet on behalf of the Private EC2
> and returns the response."**



---



Suppose I **delete the NAT Gateway**, but I **leave the Private Route Table pointing to it**.

Now you run:

```bash
curl -I https://aws.amazon.com
```

from the Private EC2.

What do you think will happen?

A. ✅ It still works.

B. ❌ It fails.

And **why?** (One sentence is enough.)

## Let's think step by step.

### Before deleting NAT

Your path was:

```text
Private EC2
      │
      ▼
Private Route Table
      │
0.0.0.0/0
      │
      ▼
NAT Gateway
      │
      ▼
Internet Gateway
      │
      ▼
Internet
```

Everything worked.

---

## Now imagine we delete the NAT Gateway.

What happens?

The Route Table still says:

```text
0.0.0.0/0
    ↓
NAT Gateway
```

But...

The NAT Gateway no longer exists.

So the EC2 says:

> "Route Table, where do I send this packet?"

The Route Table answers:

> "Send it to the NAT Gateway."

The EC2 replies:

> "But... there's no NAT Gateway!"

So the packet has **nowhere to go**.

The request fails **before it even reaches the Internet Gateway**.

---

## Why isn't the Internet Gateway used directly?

Because your Private Route Table **doesn't point to the Internet Gateway**.

It points to the NAT Gateway.

Even if you changed the route to:

```text
0.0.0.0/0 → Internet Gateway
```

it **still wouldn't work**, because:

* The EC2 has **no Public IP**.
* The Internet Gateway only provides internet access for instances with a public IPv4 (or IPv6 with the appropriate setup).

---

#  Answer



> **"What happens if the NAT Gateway is deleted?"**

A strong answer is:

> **"The Private EC2 loses outbound internet access because its route table sends internet traffic to the NAT Gateway. Once the NAT Gateway is deleted, that route has no valid target, so packets cannot leave the VPC. The instance also cannot use the Internet Gateway directly because it doesn't have a public IP address."**

---

# ⭐ Golden Rule of AWS Networking

Remember this forever:

```text
Public EC2
        │
        ▼
Internet Gateway
```

```text
Private EC2
        │
        ▼
NAT Gateway
        │
        ▼
Internet Gateway
```

A **Private EC2 never talks directly to the Internet Gateway**.

The **NAT Gateway acts as the middleman**.

***



Suppose I launch **another EC2 in Public-A** with a **Public IP**.

Question:

Can that **Public EC2** access the Internet **without using the NAT Gateway**?

👉 What do you think?

1. **Yes**
2. **No**

And tell me **why** in one sentence.

# Think about the Public EC2

Suppose we have:

```text
Public Subnet

EC2
Public IP = 54.x.x.x
Private IP = 10.10.1.25
```

This EC2 has:

* ✅ Public IP
* ✅ Public Subnet
* ✅ Route Table with `0.0.0.0/0 → Internet Gateway`

So when it wants to reach Google:

```text
Public EC2
      │
      ▼
Public Route Table
      │
0.0.0.0/0
      │
      ▼
Internet Gateway
      │
      ▼
Internet
```

It **doesn't need a NAT Gateway**.

---

# Why?

Because the EC2 already has its own **Public IP**.

It doesn't need the NAT Gateway's Elastic IP.

The Internet Gateway can directly translate traffic between the EC2's public IP and the internet.

---

# Compare Both

### Public EC2

```text
Public EC2
(Public IP)
      │
      ▼
Internet Gateway
      │
      ▼
Internet
```

No NAT needed.

---

### Private EC2

```text
Private EC2
(No Public IP)
      │
      ▼
NAT Gateway
      │
      ▼
Internet Gateway
      │
      ▼
Internet
```

NAT is required.

---

# Easy Memory Trick

Imagine two people.

### Person A (Public EC2)

Has their own phone.

📱 Calls people directly.

---

### Person B (Private EC2)

Has no phone.

📵 Must use the receptionist's phone.

The receptionist is the **NAT Gateway**.

---

# Interview Answer

If asked:

> **"Can a Public EC2 access the Internet without a NAT Gateway?"**

A good answer is:

> **"Yes. A Public EC2 has a public IP address and a route to the Internet Gateway.
> Therefore, it can communicate directly with the internet without using a NAT Gateway."**

***

# Part 3 – Security Group vs NACL Lab

## Goal

We're going to build this:

```text
                Internet
                    │
                    ▼
             Internet Gateway
                    │
                    ▼
          Public Route Table
                    │
                    ▼
             Public Subnet A
                    │
        ┌───────────────────────┐
        │     EC2 Web Server     │
        │      (Apache/nginx)    │
        └───────────────────────┘
               ▲            ▲
               │            │
      Security Group     NACL
```

Then we'll:

✅ Website works

↓

❌ NACL blocks it

↓

✅ Remove block

↓

Website works again

---

# First understand WHY

People often ask:

> "Why do we need both Security Group and NACL?"

Today you'll see.

Security Group = Bodyguard

NACL = Security gate

---

# Step 1 – Launch a Public EC2

Go to

**EC2**

↓

**Launch Instance**

---

## Name

```text
cloudadhar-day6-web-ec2
```

---

## AMI

Choose

```text
Amazon Linux 2023
```

---

## Instance Type

```text
t2.micro
```

(or `t3.micro`)

---

## Key Pair

Use

```text
Proceed without Key Pair
```

if AWS allows.

Otherwise use an existing one.

---

# Step 2 – Network Settings ⭐⭐⭐

Click **Edit**

---

### VPC

Choose

```text
cloudadhar-day5-vpc
```

---

### Subnet

Choose

```text
cloudadhar-public-a
```

Very important.

NOT Private-A.

---

### Auto Assign Public IP

Choose

```text
Enable
```

Question:

### Why?

Because we want to open the website from our browser.

Without Public IP,

browser cannot reach it.

---

# Step 3 – Security Group

Create new.

Name

```text
cloudadhar-day6-web-sg
```

---

### Inbound Rules

Add

HTTP

```text
Port

80
```

Source

```text
Anywhere
```

(We'll restrict later if needed.)

---

Leave outbound

Default

```text
All Traffic
```

---

# Step 4 – IAM Role

Attach

```text
cloudadhar-day6-ssm-role
```

Same role as before.

This lets you use Session Manager if needed.

---

# Step 5 – User Data ⭐⭐⭐

Scroll down.

Open

```text
Advanced Details
```

Find

```text
User Data
```

Paste this exactly:

```bash
#!/bin/bash
dnf update -y
dnf install -y nginx
systemctl enable nginx
systemctl start nginx
echo "<h1>CloudAdhar Day 6 NACL Demo</h1>" > /usr/share/nginx/html/index.html
```

---

# What does this script do?

Line 1

```bash
#!/bin/bash
```

Run this as a shell script.

---

```bash
dnf update -y
```

Updates packages.

---

```bash
dnf install -y nginx
```

Installs nginx.

---

```bash
systemctl enable nginx
```

Starts nginx automatically after reboot.

---

```bash
systemctl start nginx
```

Starts nginx now.

---

```bash
echo "<h1>CloudAdhar Day 6 NACL Demo</h1>"
```

Creates a simple webpage.

---

# Step 6

Click

```text
Launch Instance
```

Wait until

```text
Running
```

<img width="2560" height="7567" alt="image" src="https://github.com/user-attachments/assets/c8950696-6035-40c6-9c95-90c3c9b24a14" />
<img width="2186" height="1041" alt="image" src="https://github.com/user-attachments/assets/7a8ca642-82ef-4b65-85bf-ce2b80b721ed" />


---

# Step 7 – Test Website

Copy the

Public IPv4

Example

```text
54.xx.xx.xx
```

Open browser

Type

```text
http://PUBLIC-IP
```
```text
http://35.94.190.113/
```
NOT

```text
https://
```

because nginx is only serving HTTP.

---

## Expected

You should see

```text
CloudAdhar Day 6 NACL Demo
```

<img width="686" height="142" alt="image" src="https://github.com/user-attachments/assets/1ba1890f-869d-4186-94a6-25fcb965209d" />


---

# STOP HERE

Don't create the NACL yet.

We first need to confirm the website works.

This is important because later, when it stops working, we'll know the NACL caused it.

---

## Your task

1. Launch the Public EC2.
2. Wait until it is **Running**.
3. Open:

```text
http://Public-IP
```

***

Right now your website is working because:

```text
Your Browser
      │
      ▼
Internet
      │
      ▼
Internet Gateway
      │
      ▼
Public Subnet
      │
      ▼
NACL (Default Allow)
      │
      ▼
Security Group (Allows HTTP 80)
      │
      ▼
Nginx
```

Everything is allowing the traffic.

---

# Now we're going to BREAK it 😄

Don't worry.

We'll fix it in 2 minutes.

This is the best way to understand NACLs.

---

# Step 1 - Find Your Public IP

Open a new browser tab.

Search

```text
what is my ip
```

or go to

[https://checkip.amazonaws.com](https://checkip.amazonaws.com)

You'll get something like

```text
203.122.55.89
```

Write it down.

We need it because we're going to block **only your computer**, not everyone.

---

# Step 2 - Create Custom NACL

Go to

**VPC**

↓

**Network ACLs**

↓

Click

```text
Create Network ACL
```

Fill in

### Name

```text
cloudadhar-day6-public-a-nacl
```

### VPC

Choose

```text
cloudadhar-day5-vpc
```

Click

```text
Create
```

<img width="2526" height="762" alt="image" src="https://github.com/user-attachments/assets/67e6a8cc-3c23-479c-b3c1-882954c45257" />
<img width="2242" height="672" alt="image" src="https://github.com/user-attachments/assets/2c640e0b-e962-473c-9eeb-3a3fd5e49c6b" />


---

## What just happened?

Remember our story?

Before:

```text
Public Subnet

↓

Default NACL
```

Now we're creating our own security guard.

---

# Step 3 - Associate it

Open

```text
cloudadhar-day6-public-a-nacl
```

Go to

**Subnet Associations**

↓

**Edit subnet associations**

Tick ONLY

```text
cloudadhar-public-a
```

Save.

<img width="2200" height="747" alt="image" src="https://github.com/user-attachments/assets/67b21434-0608-4ec0-a2b5-4e9bed84565f" />


---

## What happens now?

Public-A no longer uses the default NACL.

It now uses YOUR custom NACL.

---

# Step 4 - Don't Panic!

The moment you associate it,

the website will probably stop working.

Do you know why?

Because a **new custom NACL starts with DENY ALL**.

Remember from theory?

Default NACL = Allow all.

Custom NACL = Starts empty (effectively denying all traffic until you add rules).

So don't worry if the website immediately becomes unreachable.

That's expected.

---

# Step 5 - Open Inbound Rules

Click

**Inbound Rules**

↓

**Edit**

You'll probably only see

```text
*
DENY
```

This means

Everything blocked.

---

Now add these rules.

## Rule 100

```
Rule Number : 100

Type : HTTP

Protocol : TCP

Port : 80

Source : 0.0.0.0/0

Allow
```

<img width="2527" height="437" alt="image" src="https://github.com/user-attachments/assets/08b0559c-91f1-484f-94f1-699e06afbad2" />


---

## Rule 110 ⭐

```
Rule Number : 110

Type : Custom TCP

Port Range

1024-65535

Source

0.0.0.0/0

Allow
```

<img width="2340" height="467" alt="image" src="https://github.com/user-attachments/assets/81c02faf-00a2-49a0-9641-e77fd2029612" />


---

### Why 1024-65535?

Remember yesterday?

These are **ephemeral ports**.

The response traffic uses them.

Without this rule,

the browser won't receive the response.

---

Save.

<img width="2532" height="906" alt="image" src="https://github.com/user-attachments/assets/130ce7bb-5e4c-43ab-9a02-6b94f8ef5f92" />


---

# Step 6 - Outbound Rules

Now edit

**Outbound Rules**

Add

---

## Rule 100

```
HTTP

Port 80

Destination

0.0.0.0/0

ALLOW
```

---

## Rule 110

```
HTTPS

Port 443

Destination

0.0.0.0/0

ALLOW
```

---

## Rule 120

```
Custom TCP

1024-65535

Destination

0.0.0.0/0

ALLOW
```

---

Save.

<img width="2536" height="517" alt="image" src="https://github.com/user-attachments/assets/e641416a-b5a5-4353-839a-2cedc3ba3d10" />
<img width="2537" height="962" alt="image" src="https://github.com/user-attachments/assets/fccc9d3e-960e-483f-9069-6c9be679c669" />


---

# Why these?

Imagine the EC2 wants to:

* Download updates
* Talk to package repositories
* Send responses

It needs outbound traffic.

---

# Step 7

Refresh the browser.

Question:

Does

```text
CloudAdhar Day 6 NACL Demo
```

appear again?

<img width="755" height="252" alt="image" src="https://github.com/user-attachments/assets/062eeb1b-d89f-4ee2-bf8a-7c9b1391d085" />




***

This is the **"Aha!" moment** of the lab.

Right now your NACL says:

```text
Rule 100 → Allow HTTP
Rule 110 → Allow Ephemeral Ports
```

So the website works.

Now we're going to prove **how NACL rule order works**.

---

# Step 8 – Block ONLY Yourself

Remember your public IP?

Example:

```text
49.36.120.25
```

(Your IP will be different.)

We're going to block **only that IP**.

---

## Open Inbound Rules

Go to:

**VPC → Network ACLs**

↓

Select:

```text
cloudadhar-day6-public-a-nacl
```

↓

**Inbound Rules**

↓

**Edit inbound rules**

---

## Add Rule 90 ⭐⭐⭐

Fill it like this:

| Rule # | Type | Protocol | Port | Source                | Allow/Deny |
| -----: | ---- | -------- | ---- | --------------------- | ---------- |
| **90** | HTTP | TCP      | 80   | **YOUR_PUBLIC_IP/32** | **DENY**   |

Example:

```text
Rule Number : 90

Type : HTTP

Port : 80

Source : 49.36.120.25/32

DENY
```

Click **Save**.

<img width="2536" height="536" alt="image" src="https://github.com/user-attachments/assets/a4cdaab6-072e-4ccc-ba6d-da3c01ce6c37" />
<img width="2440" height="617" alt="image" src="https://github.com/user-attachments/assets/55bda5b4-dfee-4468-9606-1fd924537fae" />


---

# Why Rule 90?

Remember from theory:

**NACL checks rules from the lowest rule number to the highest.**

So AWS checks like this:

```text
Traffic arrives

↓

Rule 90
DENY

↓

STOP
```

AWS never even looks at Rule 100.

---

# Think Like a Security Guard

Visitor arrives.

Security Guard asks:

> "Is your IP 49.36.120.25?"

You:

> "Yes."

Security Guard:

> ❌ "You are blocked."

The guard never continues checking the next rules.

---

# Test It

Go back to your browser.

Refresh:

```text
http://YOUR-PUBLIC-IP
```

### What should happen?

You should **NOT** see:

```text
CloudAdhar Day 6 NACL Demo
```

Instead, your browser may show:

* Connection timed out
* This site can't be reached
* ERR_CONNECTION_TIMED_OUT
* Another browser/network error

Any of these is acceptable.

---

# Why did it fail?

Let's trace the packet.

```text
Your Browser
      │
      ▼
Internet
      │
      ▼
Internet Gateway
      │
      ▼
NACL
      │
Rule 90
DENY
      │
      ✖
Traffic Dropped
```

Notice:

The packet **never reaches**:

* Security Group
* EC2
* Nginx

The NACL blocks it first because it protects the **subnet**.

---

# This is the BIG Difference

Imagine we **removed the Security Group's HTTP rule** instead.

Then the traffic would be:

```text
Internet
    │
    ▼
NACL
(ALLOW)
    │
    ▼
Security Group
(DENY)
    │
    ✖
EC2
```

So:

* **NACL** blocks traffic at the subnet boundary.
* **Security Group** blocks traffic at the instance.

---



You entered:

```text
35.94.190.113
```

AWS is complaining because it expects a **CIDR block**, not just an IP address.

---

# What is CIDR?

A CIDR tells AWS **how many IP addresses** are included.

Examples:

```text
35.94.190.113/32
```

means

> **Exactly one IP address** (only your computer).

Whereas:

```text
35.94.190.0/24
```

means

> 256 IP addresses (35.94.190.0 to 35.94.190.255).

We don't want to block everyone—we only want to block **your computer**.

So use:

```text
35.94.190.113/32
```

---

# Fill Rule 90 Like This

| Field       | Value                |
| ----------- | -------------------- |
| Rule Number | **90**               |
| Type        | **HTTP**             |
| Protocol    | TCP                  |
| Port        | **80**               |
| **Source**  | **35.94.190.113/32** |
| Allow/Deny  | **Deny**             |

---

## Why `/32`?

Think of it like this:

```text
/32 = One house

/24 = One street

/16 = One city
```

Today we only want to block **one house**—your browser.

<img width="2410" height="557" alt="image" src="https://github.com/user-attachments/assets/eabdc26e-dbd7-4ed7-af7b-a9183687c447" />


---

## After Saving

Refresh:

```text
http://YOUR-EC2-PUBLIC-IP
```

The page should stop loading or time out.

That proves:

* ✅ Rule **90** was checked first.
* ✅ AWS never reached Rule **100 Allow HTTP**.
* ✅ NACLs stop at the **first matching rule**.

---

### Mini Quiz 🧠

If your NACL has:

```text
Rule 90   DENY HTTP   35.94.190.113/32

Rule 100  ALLOW HTTP  0.0.0.0/0
```

and **your IP is `35.94.190.113`**, which rule will AWS apply?

A. Rule 90

B. Rule 100

(Answer before we move on.)

---

# Your Task

1. Add **Rule 90**.
2. Refresh the webpage.

Then tell me:

> **Did the website stop working?**

If yes, we'll remove Rule 90 and watch the website immediately come back. That's the final proof that **NACL rule order** matters.

No the page s still loading

***

🎉 **Excellent observation!** This is exactly how a real AWS engineer debugs.

Your answer is correct:

> ✅ **Rule 90**

But you also said:

> **"The page is still loading."**

That is actually **expected** when traffic is dropped by a NACL.

A NACL doesn't send back a message saying "Access Denied." It simply **drops the packets**. Your browser keeps waiting until it times out.

---

# First, let's verify the NACL rule.

Please check **Rule 90** carefully.

It should be:

| Field       | Value                |
| ----------- | -------------------- |
| Rule Number | **90**               |
| Type        | **HTTP**             |
| Protocol    | **TCP**              |
| Port        | **80**               |
| Source      | **35.94.190.113/32** |
| Action      | **DENY**             |

---

# Next, check the NACL association.

Go to:

**VPC → Network ACLs**

↓

Select:

```text
cloudadhar-day6-public-a-nacl
```

↓

**Subnet Associations**

Is it associated with:

✅ `cloudadhar-public-a`

or

❌ Is it still associated with the default NACL?

---

# Finally, let's verify the EC2 location.

Go to your web EC2.

Check:

**Networking** tab

↓

**Subnet**

Is it:

```text
cloudadhar-public-a
```

?

---

# Why is the browser "loading"?

When a NACL drops packets:

```text
Browser
   │
HTTP Request
   │
   ▼
NACL
   │
 DENY
   │
(drop)
```

The EC2 **never receives** the request.

Since no reply comes back, the browser usually shows:

* Loading...
* Timed out
* ERR_CONNECTION_TIMED_OUT

This is different from an application error like **403 Forbidden**, because the application never even saw the request.

---

## Please tell me these three things:

1. **Does Rule 90 show `DENY`?**
2. **Is `cloudadhar-day6-public-a-nacl` associated with `cloudadhar-public-a`?**
3. **Is your web EC2 in `cloudadhar-public-a`?**

Once we verify those, we'll know whether the NACL is working exactly as intended or if one small configuration needs adjusting.

***

Perfect! 👍 If the answer is **yes to all three**, then your configuration is **most likely correct**.

Now let's clarify one thing because the wording matters.

You said:

> **"page is still loading"**

### Do you mean:

### Option A ✅ (Expected)

The browser keeps spinning and after 30–60 seconds shows something like:

* `This site can't be reached`
* `ERR_CONNECTION_TIMED_OUT`
* `Connection timed out`

👉 **This means your NACL is working correctly.** The packet is being dropped.

---

### Option B ❌ (Unexpected)

The page eventually loads and still shows:

```text
CloudAdhar Day 6 NACL Demo
```

👉 Then something is wrong.

---

## Let's verify one more thing.

### Look at your Inbound NACL Rules.

Can you tell me **exactly** what they are?

For example:

| Rule # | Action | Type       | Source           |
| ------ | ------ | ---------- | ---------------- |
| 90     | DENY   | HTTP       | 35.94.190.113/32 |
| 100    | ALLOW  | HTTP       | 0.0.0.0/0        |
| 110    | ALLOW  | Custom TCP | 0.0.0.0/0        |
| *      | DENY   | ALL        | 0.0.0.0/0        |

A screenshot is also fine if that's easier.

---

## Also, here's a small networking tip.

Browsers often **cache** pages.

To make sure you're testing the network and not a cached page:

* Press **Ctrl + Shift + R** (hard refresh), or
* Open the URL in an **Incognito/Private** window.

If the NACL is blocking correctly, the page **will not load** after a hard refresh.

---

### Based on what you've told me so far

If:

* ✅ Rule 90 is DENY
* ✅ The custom NACL is associated with Public-A
* ✅ The EC2 is in Public-A

Then the expected result is **a timeout**, **not** an "Access Denied" page. A timeout means the NACL is silently dropping the traffic, which is exactly how NACLs behave.

<img width="1827" height="942" alt="image" src="https://github.com/user-attachments/assets/db3b8c46-0683-4d48-859e-835babc44ae0" />


***

🎉🎉 **YES!! That's exactly what we wanted!** 🎉🎉

The problem was **browser caching**, not your AWS configuration.

When you opened it in a **new browser/incognito window**, you got:

> **"This site can't be reached."**

✅ **That means Rule 90 is working perfectly.**

---

# Let's understand exactly what happened.

Before adding Rule 90:

```text
Your Browser
      │
      ▼
Internet
      │
      ▼
Internet Gateway
      │
      ▼
NACL
Rule 100 → ALLOW
      │
      ▼
Security Group
      │
      ▼
EC2
      │
      ▼
Nginx
```

Website worked.

---

After adding Rule 90:

```text
Your Browser
      │
      ▼
Internet
      │
      ▼
Internet Gateway
      │
      ▼
NACL
Rule 90 → DENY
      │
      ✖
Traffic Dropped
```

The packet never reaches:

* ❌ Security Group
* ❌ EC2
* ❌ Nginx

That's why your browser says:

> **This site can't be reached**

Exactly as expected.

---

# Why did the first browser still show the page?

Most browsers cache pages.

Think of it like this:

```text
Browser

"I already downloaded this page."

↓

"I'll show my saved copy."
```

The browser wasn't necessarily making a fresh network request every time.

A **new browser window** or **Incognito mode** forced a new request, which the NACL blocked.

---

# 🎯 This is the biggest lesson of Part 3

## Security Group vs NACL

### Security Group

```text
Internet
    │
    ▼
Security Group
    │
    ▼
EC2
```

* Attached to **EC2/ENI**
* **Stateful**
* Allow rules only

---

### NACL

```text
Internet
    │
    ▼
NACL
    │
    ▼
Subnet
    │
    ▼
EC2
```

* Attached to **Subnet**
* **Stateless**
* Can **ALLOW** and **DENY**
* Rules are processed in **ascending rule number order**
* Stops at the **first match**

---

# ⭐ Interview Questions (You've just learned these!)

### Q1. Which is evaluated first?

```text
Internet
    │
    ▼
NACL
    │
    ▼
Security Group
    │
    ▼
EC2
```

✅ **Answer:** NACL first, then Security Group.

---

### Q2. Why did Rule 90 block traffic even though Rule 100 allowed HTTP?

✅ **Answer:** NACL evaluates rules from the **lowest rule number to the highest** and stops at the **first matching rule**. Rule 90 matched your IP first, so Rule 100 was never evaluated.

---

### Q3. Why did the browser show "This site can't be reached" instead of "403 Forbidden"?

✅ **Answer:** A NACL silently drops packets. The request never reached the web server, so the browser eventually timed out instead of receiving an HTTP error.

---

# Final Step of Part 3

Now remove **Rule 90**.

After saving, refresh the page (or use a new Incognito window).

The website should immediately work again.

This proves that **removing the deny rule restores connectivity**.

<img width="2246" height="461" alt="image" src="https://github.com/user-attachments/assets/83bc1f29-322c-4add-9b93-446532d19a71" />
<img width="740" height="242" alt="image" src="https://github.com/user-attachments/assets/0ee46f1b-6baa-47ff-b014-a3f86e491051" />


***


Awesome! 🎉

This is one of the **most important AWS networking concepts** for interviews and the AWS Solutions Architect exam.

Many beginners think:

> **"My EC2 needs the internet to access S3."**

❌ That's not always true.

Today we'll prove that a **Private EC2 can access S3 without going to the internet**.

---

# Before We Start

## First, remember your current architecture.

```text
                     Internet
                         ▲
                         │
                 Internet Gateway
                         ▲
                         │
                  NAT Gateway
                         ▲
                         │
                 Private Route Table
                         ▲
                         │
                  Private EC2
```

When your EC2 runs:

```bash
aws s3 ls
```

Today, it goes like this:

```text
Private EC2
     │
     ▼
NAT Gateway
     │
     ▼
Internet
     │
     ▼
Amazon S3
```

Works...

But it's not the best design.

---

# Why is this bad?

Imagine Amazon has:

* 100 EC2s
* All downloading from S3

Every request goes:

```text
EC2
 │
 ▼
NAT Gateway
 │
 ▼
Internet
 │
 ▼
S3
```

Problems:

* 💰 NAT Gateway data processing charges
* 🚦 Extra network hop
* 📈 NAT can become a bottleneck

AWS thought:

> "Why send S3 traffic to the internet? S3 is already an AWS service!"

So they created...

# ⭐ Gateway Endpoint

---

# What is a Gateway Endpoint?

Think of it as a **private road** inside AWS.

Instead of this:

```text
Private EC2
      │
      ▼
NAT
      │
      ▼
Internet
      │
      ▼
S3
```

It becomes:

```text
Private EC2
      │
      ▼
Gateway Endpoint
      │
      ▼
S3
```

Notice:

🚫 No NAT

🚫 No Internet

Still reaches S3!

---

# Real Life Example

Imagine your house and your school are inside the same apartment complex.

Without a private road:

```text
House
 │
 ▼
Main Road
 │
 ▼
School
```

Lots of traffic.

Now the apartment builds:

```text
House
 │
 ▼
Private Walkway
 │
 ▼
School
```

Faster.

Safer.

No public road.

That's exactly what an S3 Gateway Endpoint is.

---

# What will AWS create?

Nothing inside your subnet.

Instead, AWS adds a **special route**.

Think of it like:

Before:

```text
Destination

0.0.0.0/0
        ↓
NAT Gateway
```

After:

```text
Destination

pl-63a5400a
      ↓
Gateway Endpoint
```

Don't worry about remembering the prefix list ID (`pl-...`).

Just remember:

> **AWS automatically adds an S3 route to your selected route table.**

---

# Lab Goal

We are going to:

1. Create an S3 Gateway Endpoint.
2. Attach it to your **Private-A Route Table**.
3. Verify AWS added a new route.
4. Test from the Private EC2.

---

# Step 1 – Open Endpoints

Go to

**VPC**

↓

**Endpoints**

↓

Click

```text
Create Endpoint
```

---

# Step 2 – Name

Enter

```text
cloudadhar-day6-s3-gateway-endpoint
```

---

# Step 3 – Service Category

Choose

✅ AWS Services

---

# Step 4 – Service

Search

```text
S3
```

You'll see something similar to:

```text
com.amazonaws.ap-south-1.s3
```

**Type should say:**

```text
Gateway
```

⚠️ Don't accidentally choose an **Interface Endpoint** for S3 if one appears. For this lab, the service type must be **Gateway**.

---

# Step 5 – VPC

Choose

```text
cloudadhar-day5-vpc
```

---

# Step 6 – Route Tables ⭐⭐⭐

This is the most important step.

Select **ONLY**:

```text
cloudadhar-private-a-rt
```

❌ Do **not** select the public route table.

---

## Why?

Because only the **Private EC2** needs a private path to S3.

---

# Step 7 – Policy

Choose:

```text
Full Access
```

We'll keep it simple for the connectivity test.

Later, in production, you would use a more restrictive endpoint policy.

---

# Step 8 – Create

Click:

```text
Create Endpoint
```

Wait until its status becomes:

```text
Available
```

<img width="2560" height="3727" alt="image" src="https://github.com/user-attachments/assets/1ff522dc-e4e5-4a69-9271-1128a9c8da0b" />
<img width="2551" height="985" alt="image" src="https://github.com/user-attachments/assets/f751b49e-9dc0-44ed-a2a3-a12425653dd6" />


---

> **"Why doesn't S3 traffic use the NAT Gateway anymore?"**

🎉 Great job! The **S3 Gateway Endpoint** is now available.

And I love that you tried answering the question. ❤️ That's how you learn.

Your answer was:

> **"Because we removed it."**

❌ Not quite.

Here's why.

---

# Did we remove the NAT Gateway?

No.

Your NAT Gateway is **still running**.

It still looks like this:

```text
Internet
    ▲
    │
Internet Gateway
    ▲
    │
NAT Gateway
```

In fact, if you run:

```bash
curl -I https://aws.amazon.com
```

from your Private EC2, it will **still use the NAT Gateway**.

So the NAT is definitely still there.

---

# Then why doesn't S3 use the NAT?

Let's think like the Route Table.

Suppose your EC2 wants to reach:

```text
aws.amazon.com
```

The Route Table says:

```text
Destination?

aws.amazon.com

↓

Not inside VPC

↓

0.0.0.0/0

↓

NAT Gateway
```

So it goes through the NAT.

---

Now suppose your EC2 wants:

```text
Amazon S3
```

The Route Table now says:

```text
Destination?

Amazon S3

↓

I have a special route!

↓

Gateway Endpoint
```

So it **never reaches** the NAT Gateway.

---

# Imagine a City

Before today:

```text
Your House
      │
      ▼
Main Highway
      │
      ▼
Shopping Mall (S3)
```

Today, the city built a shortcut.

```text
Your House
      │
      ▼
Private Road
      │
      ▼
Shopping Mall (S3)
```

Would you still use the highway?

No!

You'll take the shortcut.

The highway (NAT Gateway) still exists.

You simply don't need it for S3 anymore.

---

# This is exactly what AWS does.

After creating the Gateway Endpoint,

AWS automatically added a route like:

```text
Destination

pl-xxxxxxxx
        ↓
Gateway Endpoint
```

The `pl-xxxxxxxx` is an AWS-managed **prefix list** representing S3 IP ranges.

Your Route Table now says:

```text
If destination is S3

↓

Gateway Endpoint

Else

↓

0.0.0.0/0

↓

NAT Gateway
```

---

# Easy Comparison

## Going to Google

```text
Private EC2
      │
      ▼
NAT Gateway
      │
      ▼
Internet
      │
      ▼
Google
```

---

## Going to S3

```text
Private EC2
      │
      ▼
Gateway Endpoint
      │
      ▼
Amazon S3
```

Notice:

🚫 No NAT

🚫 No Internet

Still reaches S3.

---

# Interview Answer ⭐⭐⭐⭐⭐

If asked:

> **"Why doesn't S3 traffic use the NAT Gateway after creating a Gateway Endpoint?"**

A strong answer is:

> **"Because the S3 Gateway Endpoint adds a more specific route to the route table for Amazon S3. When the destination is S3, the route table sends the traffic to the Gateway Endpoint instead of the default `0.0.0.0/0` route through the NAT Gateway. The NAT Gateway is still used for other internet destinations."**

---

# Now let's verify it.

Go back to your **Private EC2** (the one connected through Session Manager).

Run:

```bash
aws s3api list-buckets
```

---

## What should happen?

You should see JSON output similar to:

```json
{
    "Buckets": [
        {
            "Name": "my-bucket",
            "CreationDate": "2026-07-20T..."
        }
    ],
    "Owner": {
        ...
    }
}
```

Or, if your account has no buckets:

```json
{
    "Buckets": []
}
```

Both are fine.

---

## 🧠 One Small Quiz

Suppose you **delete the NAT Gateway** but **keep the S3 Gateway Endpoint**.

Which of these will still work from your Private EC2?

A. `curl -I https://aws.amazon.com`

B. `aws s3api list-buckets`

C. Both

D. Neither

***

Great question! 😊

You have **2 EC2 instances**, and we need the **correct one**.

| Instance                          | Purpose                             | Use Now? |
| --------------------------------- | ----------------------------------- | -------- |
| ✅ **cloudadhar-day6-private-ec2** | Private EC2 behind the NAT Gateway  | **YES**  |
| ❌ **cloudadhar-day6-web-ec2**     | Public web server for the NACL demo | **NO**   |

---

## We need this one:

```text
cloudadhar-day6-private-ec2
```

Instance ID:

```text
i-07f9714be3c1092f6
```

Notice:

```text
Public IPv4 Address: –
```

That means it is **private**, which is exactly what we want.

---

## Don't use this one

```text
cloudadhar-day6-web-ec2
```

Because:

```text
Public IP: 35.94.190.113
```

This was only for the **NACL demonstration**.

---

# Now do this

1. Click **cloudadhar-day6-private-ec2**
2. Click **Connect**
3. Choose **Session Manager**
4. Click **Connect**

You should get a terminal like:

```bash
sh-5.2$
```

---

# Now run:

```bash
aws s3api list-buckets
```

Copy the output here.

---

# 🧠 Meanwhile, let's answer the quiz together.

> **Suppose you delete the NAT Gateway but keep the S3 Gateway Endpoint. Which command still works?**

### A

```bash
curl -I https://aws.amazon.com
```

This needs the **internet**.

Without a NAT Gateway:

❌ It fails.

---

### B

```bash
aws s3api list-buckets
```

This uses the **S3 Gateway Endpoint**.

So:

✅ It still works.

---

## ✅ Correct answer is:

**B. `aws s3api list-buckets`**

Because:

* **S3 traffic** uses the **Gateway Endpoint** (private AWS network).
* **Internet traffic** (like `curl https://aws.amazon.com`) still needs the **NAT Gateway**.

This is a very common AWS interview question, and now you know **why**, not just the answer.

Now run:

```bash
aws s3api list-buckets
```

from the **private EC2** and paste the output. We'll verify that your Gateway Endpoint is working correctly before moving to **Part 5 – Interface Endpoint**.

***

<img width="2462" height="962" alt="image" src="https://github.com/user-attachments/assets/3e721b66-b676-41d4-a8c3-91dd44ca27da" />


Excellent! 🎉 This error actually teaches us something very important.

Let's read it like detectives.

---

## The Important Part

```
SSM Agent unable to acquire credentials

Post "https://ssm.us-west-2.amazonaws.com/"

connect: connection timed out
```

This tells us:

> **The EC2 cannot reach the Systems Manager (SSM) service.**

Notice something:

This is **not an IAM permission error**.

If it were an IAM problem, you'd get **AccessDenied**.

Instead, you're getting:

```text
connection timed out
```

That means it's a **network** problem.

---

# Why did it work before?

Earlier today you successfully connected using Session Manager and ran:

```bash
curl -I https://aws.amazon.com
aws sts get-caller-identity
```

So:

* ✅ IAM role is correct.
* ✅ SSM Agent is installed.
* ✅ NAT Gateway was working.

Something changed after that.

---

# I know what changed! 😊

We modified the **NACL** on **Public-A**.

Remember:

```
Private EC2
        │
        ▼
NAT Gateway (Public-A)
```

Your **NAT Gateway lives inside Public-A**.

And earlier, we **replaced the default NACL** on **Public-A** with your custom NACL.

If that NACL doesn't allow all the traffic the NAT Gateway needs, the Private EC2 can't reach AWS services like SSM.

---

# Quick Question

Did you **remove Rule 90** after the NACL demo?

Or is Rule 90 still there?

(That alone won't cause this particular issue, but I want to know.)

---

# More importantly...

Please show me your **Subnet Associations** for:

```
cloudadhar-day6-public-a-nacl
```

I want to confirm it's only attached to:

```
cloudadhar-public-a
```

---

# I also want you to check one thing.

Go to:

**VPC → Route Tables**

Open:

```
cloudadhar-private-a-rt
```

Take a screenshot (or list the routes).

I want to verify you still have:

| Destination  | Target              |
| ------------ | ------------------- |
| 10.10.0.0/16 | local               |
| 0.0.0.0/0    | NAT Gateway         |
| pl-xxxx      | S3 Gateway Endpoint |

---

# I already suspect the cause

Your custom NACL was built specifically for a **web server**.

Its outbound rules are:

* HTTP (80)
* HTTPS (443)
* Ephemeral (1024–65535)

For a web server, that's fine.

For a **NAT Gateway**, AWS expects more permissive traffic because it forwards connections for private instances.

A common practice is to leave the **default NACL** on the public subnet or create a more permissive custom NACL for the NAT subnet.

***

Excellent! 👏 You gave exactly the information I needed.

I can now see **why Session Manager stopped working.**

## Your route table is PERFECT ✅

```text
pl-68a54001  → S3 Gateway Endpoint ✅
0.0.0.0/0    → NAT Gateway         ✅
10.10.0.0/16 → Local               ✅
```

Nothing is wrong there.

---

## The problem is your Public-A NACL.

Your inbound rules are:

```text
100  ALLOW HTTP (80)
110  ALLOW TCP 1024-65535
*    DENY ALL
```

Your outbound rules are:

```text
100  ALLOW HTTP (80)
110  ALLOW HTTPS (443)
120  ALLOW TCP 1024-65535
*    DENY ALL
```

These rules are **good for a web server demo**, but **not good for a subnet that contains a NAT Gateway**.

---

# Why?

Remember this picture:

```text
Private EC2
      │
      ▼
NAT Gateway
      │
      ▼
SSM Service (HTTPS 443)
```

The NAT Gateway has to forward **many different kinds of traffic**.

Your custom NACL is restricting the subnet too much.

For this lab, AWS expects you to demonstrate NACL behavior, but **after the demo** you should either:

* remove the restrictive custom NACL, or
* make it more permissive.

---

# The easiest fix (recommended)

Since we're finished with the NACL demo:

## Go to

**VPC → Network ACLs**

↓

Select:

```text
cloudadhar-day6-public-a-nacl
```

↓

**Subnet Associations**

↓

**Edit subnet associations**

---

### Uncheck

```text
cloudadhar-public-a
```

and associate **Public-A** back to the **default NACL** for the VPC.

The default NACL allows all inbound and outbound traffic, which is the standard choice for this learner lab.

---

# Then wait 30–60 seconds

The SSM Agent retries automatically.

Then check:

```text
EC2 → Connect → Session Manager
```

The **Ping status** should become:

```text
Online
```

---

# Why are we doing this?

The NACL exercise was to **learn** how NACLs work by intentionally breaking HTTP.

Now that you've proved:

* ✅ Rule order
* ✅ First match wins
* ✅ DENY overrides later ALLOW
* ✅ Browser timeout

there's no benefit in leaving the public subnet restricted while you continue the remaining labs.

---

## 🧠 What you learned today

This is a great interview question:

> **Why did Session Manager stop working after modifying the Public subnet NACL?**

A solid answer is:

> **"Because the NAT Gateway is deployed in the public subnet. By replacing the default NACL with a restrictive custom NACL, I unintentionally affected the network path used by the NAT Gateway. Restoring a permissive NACL on the public subnet restored connectivity to AWS services such as Systems Manager."**

***

Yes. There is another option, and it's actually a better learning experience because you understand **why** instead of just switching back to the default NACL.

---

# Option 2 – Keep the Custom NACL and Fix It

Your current NACL was designed only for the **HTTP website demo**.

The NAT Gateway is a **router**. It forwards traffic for many different connections, not just HTTP.

Instead of:

```text
Allow HTTP
Allow HTTPS
Allow Ephemeral
```

for a lab, you can make the Public subnet NACL more permissive.

---

## Step 1

Go to:

**VPC → Network ACLs**

↓

**cloudadhar-day6-public-a-nacl**

↓

**Inbound Rules**

---

## Add this rule

| Rule | Type        | Source    | Action |
| ---- | ----------- | --------- | ------ |
| 90   | All Traffic | 0.0.0.0/0 | ALLOW  |

Save.

---

## Step 2

Go to:

**Outbound Rules**

Add:

| Rule | Type        | Destination | Action |
| ---- | ----------- | ----------- | ------ |
| 90   | All Traffic | 0.0.0.0/0   | ALLOW  |

Save.

---

Now the NACL looks like:

```text
90  ALLOW ALL
100 ALLOW HTTP
110 ALLOW TCP 1024-65535
*   DENY
```

AWS checks:

```text
Rule 90

↓

ALLOW

↓

Stop
```

Everything is allowed.

---

# Why this works

Remember:

A NACL checks from the **lowest rule number**.

```text
Rule 90

↓

ALLOW ALL

↓

Done
```

The NAT Gateway can forward traffic again.

---

# Which option should you choose?

### Option 1 (Default NACL)

✅ Best practice for this learner lab after completing the NACL exercise.

---

### Option 2 (Modify the custom NACL)

✅ Good if you want to continue using your custom NACL and understand rule evaluation.

---

## One thing I want to point out

The course instructions only asked you to:

1. Create a custom NACL.
2. Add a temporary deny rule.
3. Confirm failure.
4. Remove the temporary deny rule.
5. Confirm recovery.

It **didn't** ask you to lock down the public subnet permanently.

So after proving the concept, it's completely fine to return the subnet to a permissive state for the remaining parts of the lab.

---

### I recommend **Option 2** if your goal is learning, because you'll see how changing NACL rules immediately affects connectivity without replacing the NACL.


<img width="2541" height="522" alt="image" src="https://github.com/user-attachments/assets/114b4dc2-aa9e-4522-bcdf-76515a0c26bb" />
<img width="2532" height="590" alt="image" src="https://github.com/user-attachments/assets/09823d11-f971-43b4-86f6-aa01a9cfe45b" />


<img width="2225" height="327" alt="image" src="https://github.com/user-attachments/assets/46a769e0-3ca8-427d-be88-956949dfa2bd" />

Great! Let's continue from here. 😊

## First, did you apply **Option 2**?

Did you add these two rules?

**Inbound**

* Rule **90** → **ALLOW** → **All Traffic** → `0.0.0.0/0`

**Outbound**

* Rule **90** → **ALLOW** → **All Traffic** → `0.0.0.0/0`

If **yes**, wait about **30–60 seconds**.

---

## Then check Session Manager again

Go to:

**EC2**
→ **cloudadhar-day6-private-ec2**
→ **Connect**
→ **Session Manager**

### What does it show?

Is the **Ping status** now:

* 🟢 **Online**
* 🔴 **Offline**

---



## If it is Online

Connect to the instance and run:

```bash
aws s3api list-buckets
```

Paste the output here.

***

🎉🎉 **YES!! We fixed it!** 🎉🎉

Look at the important line:

```text
Ping status
🟢 Online
```

That means:

* ✅ NAT Gateway is forwarding traffic again.
* ✅ The SSM Agent can now reach the AWS Systems Manager service.
* ✅ Your networking is healthy again.

Ignore the **Latest error messages** for now—they're just the old error that was logged earlier. The **current** status is what matters, and it says **Online**.

---

# 🎉 What did we just learn?

Let's replay the story.

## Before changing the NACL

```text
Private EC2
     │
     ▼
NAT Gateway
     │
     ▼
SSM Service
```

✅ Worked.

---

## After making the Public-A NACL restrictive

```text
Private EC2
     │
     ▼
NAT Gateway
     │
     ✖
Blocked by restrictive NACL
```

❌ Session Manager went **Offline**.

---

## After allowing the traffic again

```text
Private EC2
     │
     ▼
NAT Gateway
     │
     ▼
SSM Service
```

🟢 Session Manager became **Online** again.

---

# Why did this happen?

The **NAT Gateway is in the Public subnet**.

When you changed the **Public subnet's NACL**, you changed the network path used by the NAT Gateway.

So even though your **Private EC2** was fine, its traffic had to pass through the NAT Gateway, and the restrictive NACL interrupted that path.

This is an excellent real-world lesson: **network changes in one subnet can affect resources in another subnet if they're connected through shared infrastructure like a NAT Gateway.**

---

# Now let's finish Part 4

Click:

```text
Connect
```

to open the Session Manager terminal.

Then run:

```bash
aws s3api list-buckets
```

Paste the output here.

---

## 🧠 One more question

Without looking at your notes:

**Why can the Private EC2 access S3 even if we remove the NAT Gateway (assuming the S3 Gateway Endpoint still exists)?**

Yes. 😊

That is **normal**.

Look carefully:

```text
Ping status: Online ✅
Session Manager connection status: Not connected
```

These are **two different things**.

---

## Think of it like WhatsApp.

### Ping Status = Phone is ON 📱

AWS is asking:

> "Hello EC2, are you alive?"

EC2 replies:

> "Yes, I'm here."

So AWS shows:

```text
Ping Status: Online ✅
```

---

### Session Manager Connection Status = Are you currently on a call? 📞

Right now, you are **not connected**.

So AWS shows:

```text
Session Manager connection status:
Not connected
```

That is completely normal.

---

## Now click

```
Connect
```

AWS will start a new Session Manager session.

After a few seconds you should see something like:

```bash
sh-5.2$
```

or

```bash
[ssm-user@ip-10-10-11-10 ~]$
```

Both are fine.

---

## Then run

```bash
aws s3api list-buckets
```

and paste the output here.

---

## 🌟 Mini Lesson

Many beginners confuse these two:

| Status                                                | Meaning                                        |
| ----------------------------------------------------- | ---------------------------------------------- |
| **Ping Status = Online**                              | ✅ EC2 can communicate with AWS Systems Manager |
| **Session Manager Connection Status = Not Connected** | ✅ You haven't opened a terminal yet            |

So **"Not Connected" is expected until you click Connect.**

Go ahead and click **Connect**. You're on the last step of Part 4. 🚀

<img width="2552" height="1007" alt="image" src="https://github.com/user-attachments/assets/dfe90703-8571-45e0-93ee-15743c414921" />


🎉🎉 **YES!!** That's exactly what I expected. Great job!

The reboot restarted the **SSM Agent**, and after the network (NAT + NACL) was fixed, the agent successfully registered with Systems Manager again.

---

# Why did the reboot fix it?

Think of the SSM Agent as a person making a phone call.

### Before

```text
Private EC2
      │
      ▼
SSM Agent
      │
      ✖
NAT path broken (NACL issue)
```

The phone call failed.

---

### After fixing the NACL

The road was open again:

```text
Private EC2
      │
      ▼
NAT Gateway
      │
      ▼
SSM Service
```

But the SSM Agent was still holding onto the failed connection.

---

### After reboot

```text
EC2 starts
     │
     ▼
SSM Agent starts
     │
     ▼
Connects to Systems Manager
     │
     ▼
Online ✅
```

That's why it worked.

---

# Now continue Part 4

Open **Session Manager** and connect to:

```text
cloudadhar-day6-private-ec2
```

Run:

```bash
aws s3api list-buckets
```

Paste the output here.

<img width="2551" height="247" alt="image" src="https://github.com/user-attachments/assets/c0a1aaf5-644e-4571-ab57-184eb925b4f9" />


---

# Then answer this question

**Why does `aws s3api list-buckets` use the S3 Gateway Endpoint instead of the NAT Gateway?**

The answer should be:

> **Because the route table now has a more specific route (the S3 prefix list `pl-...`) that sends S3 traffic to the Gateway Endpoint. Only other internet traffic follows the default `0.0.0.0/0` route to the NAT Gateway.**

***



🎉 **This is actually the expected learning moment!** You didn't get a network error—you got an **IAM authorization error**.

Let's understand it step by step.

---

# What happened?

You ran:

```bash
aws s3api list-buckets
```

AWS replied:

```text
AccessDenied
```

Notice what it **didn't** say:

* ❌ Connection timed out
* ❌ Could not connect
* ❌ Network unreachable

Instead, it said:

```text
is not authorized to perform:
s3:ListAllMyBuckets
```

---

# Think of it like a building

Imagine you're going to a library.

## Step 1: Can you reach the library?

Today, **YES**.

That's your **Gateway Endpoint**.

```text
Private EC2
      │
      ▼
Gateway Endpoint
      │
      ▼
Amazon S3
```

You reached the building.

---

## Step 2: Can you enter the library?

The security guard asks:

> "Do you have permission?"

Your IAM role says:

> "No."

So the guard says:

```text
ACCESS DENIED
```

---

# This proves something very important

The request **reached S3**.

If the Gateway Endpoint wasn't working, you'd see network-related errors.

Instead, S3 itself replied:

> "I received your request, but you don't have permission."

That means:

* ✅ Network path works.
* ✅ Gateway Endpoint works.
* ❌ IAM permission is missing.

---

# Remember this sentence

> **A Gateway Endpoint provides a private network path to S3. It does not grant permission to access S3. IAM policies still control what actions are allowed.**

This is exactly what your Day 6 notes said:

> **"The endpoint supplies a private path, not permission."**

Now you've seen it in practice.

---

# How to complete the lab

Your instructions say:

> Use a role that supports Session Manager **and required read-only commands**.

Your role currently has only:

```text
AmazonSSMManagedInstanceCore
```

It does **not** have permission for:

```text
s3:ListAllMyBuckets
```

---

# Fix

Go to:

**IAM → Roles**

↓

**cloudadhar-day6-ssm-role**

↓

**Add permissions**

↓

**Attach policies**

Attach:

```text
AmazonS3ReadOnlyAccess
```

<img width="2555" height="707" alt="image" src="https://github.com/user-attachments/assets/ab874e36-325c-46ea-aada-28c7ea1c5cb3" />

Save.

Wait about **30–60 seconds** for IAM to propagate.

Then, from the same Session Manager terminal, run again:

```bash
aws s3api list-buckets
```

<img width="965" height="196" alt="image" src="https://github.com/user-attachments/assets/46c845eb-e6fe-4c54-9ecf-9b3820349dc4" />


---

# Quiz 😊

Why did you get **AccessDenied** instead of **Connection timed out**?

A. The Gateway Endpoint is broken.

B. The request reached S3, but IAM denied permission.

C. The NAT Gateway is missing.

**Answer:** **B** ✅

That's one of the most important concepts in AWS networking:

* **Networking gets you to the service.**
* **IAM decides whether you're allowed to do anything once you get there.**

***

Excellent! You're very close. 👏

After attaching **AmazonS3ReadOnlyAccess**, here's what to do.

---

# Step 1: Wait 30–60 seconds

IAM policy changes are **not always instant**.

Wait about **1 minute**.

---

# Step 2: Run the command again

In your Session Manager terminal:

```bash
aws s3api list-buckets
```

---

## You should see one of these

### Case 1: You have buckets

```json
{
    "Buckets": [
        {
            "Name": "my-bucket",
            "CreationDate": "2026-07-20T..."
        }
    ]
}
```

✅ Success.

---

### Case 2: No buckets exist

```json
{
    "Buckets": []
}
```

✅ Also success.

It means:

* Network path is working.
* Gateway Endpoint is working.
* IAM permission is working.

---

# What did we prove?

Let's think like a detective.

## Before adding the IAM policy

```text
Private EC2
      │
      ▼
Gateway Endpoint
      │
      ▼
Amazon S3
      │
      ▼
❌ AccessDenied
```

The request **reached S3**, but IAM said **No**.

---

## After adding the IAM policy

```text
Private EC2
      │
      ▼
Gateway Endpoint
      │
      ▼
Amazon S3
      │
      ▼
✅ Bucket list returned
```

Now everything works.

---

# 🎯 The biggest lesson from Part 4

There are **two separate checks** whenever you access an AWS service:

### Check 1 – Network

> **Can I reach the service?**

Handled by:

* NAT Gateway
* Gateway Endpoint
* Interface Endpoint
* Route Tables

---

### Check 2 – Permission

> **Am I allowed to use the service?**

Handled by:

* IAM Policies
* Bucket Policies
* Endpoint Policies
* SCPs
* KMS Key Policies

---

# Interview Question ⭐⭐⭐⭐⭐

**Q: Does creating an S3 Gateway Endpoint automatically allow access to S3?**

**Answer:**

> **No. The Gateway Endpoint only provides a private network path to Amazon S3. Access is still controlled by IAM policies, bucket policies, endpoint policies, and other AWS authorization mechanisms.**

***

🎉🎉 **YES!! PART 4 IS SUCCESSFULLY COMPLETED!!** 🎉🎉

Look at your final output:

```json
{
    "Buckets": [],
    "Owner": {
        "ID": "..."
    },
    "Prefix": null
}
```

That is **100% correct**.

It doesn't matter that there are no buckets.

The important thing is:

> **Amazon S3 answered your request.**

---

# Let's understand exactly what happened

## First attempt

```text
Private EC2
      │
      ▼
Gateway Endpoint
      │
      ▼
Amazon S3
      │
      ▼
❌ AccessDenied
```

Why?

Because your IAM role only had:

```text
AmazonSSMManagedInstanceCore
```

No S3 permission.

---

## After adding AmazonS3ReadOnlyAccess

```text
Private EC2
      │
      ▼
Gateway Endpoint
      │
      ▼
Amazon S3
      │
      ▼
IAM says YES
      │
      ▼
Buckets returned
```

Even though the list is empty:

```json
"Buckets": []
```

it still proves everything is working.

---

# 🧠 This is the biggest lesson of Part 4

There are **two completely separate checks**.

## Check 1 — Network

Can your EC2 reach Amazon S3?

Handled by:

* Route Table
* Gateway Endpoint
* NAT Gateway (if no endpoint)

You passed this. ✅

---

## Check 2 — Permission

Can your EC2 list buckets?

Handled by:

* IAM Policy
* Bucket Policy
* Endpoint Policy
* SCP

You passed this too after attaching `AmazonS3ReadOnlyAccess`. ✅

---

# The complete picture

```text
                     NETWORK
+--------------------------------------------+

Private EC2
      │
      ▼
Route Table
      │
      ▼
S3 Gateway Endpoint
      │
      ▼
Amazon S3

           │
           ▼

      IAM Authorization

           │
           ▼

List Buckets
```

Notice:

The **Gateway Endpoint** only provides the **road**.

IAM decides whether you're allowed to **enter the building**.

---

# ⭐⭐⭐ Interview Questions

### Q1. Why did `list-buckets` fail initially?

**Answer:**

> The request successfully reached Amazon S3 through the Gateway Endpoint, but the IAM role didn't have the `s3:ListAllMyBuckets` permission, so S3 returned `AccessDenied`.

---

### Q2. Why did it work after attaching `AmazonS3ReadOnlyAccess`?

**Answer:**

> Because the IAM role was granted permission to perform S3 read operations. The network path was already working through the Gateway Endpoint.

---

### Q3. Does a Gateway Endpoint give S3 permissions?

**Answer:**

> No. A Gateway Endpoint only provides a private network path. Access is still controlled by IAM policies, bucket policies, endpoint policies, and other authorization mechanisms.

***

Awesome! 🎉 Let's start **Part 5** slowly. Imagine you're 10 years old. 😊

---

# Part 5 – Interface Endpoint

## Goal

We already learned:

> **Gateway Endpoint = S3 and DynamoDB only**

Now we'll learn:

> **Interface Endpoint = Almost every other AWS service (EC2 API, SSM, Secrets Manager, CloudWatch, etc.)**

---

# First, remember yesterday

When your Private EC2 wanted to go to S3:

```text
Private EC2
      │
      ▼
Gateway Endpoint
      │
      ▼
Amazon S3
```

No internet.
No NAT.
Private AWS network.

---

# Today we're going to EC2 API

Suppose your Private EC2 wants to talk to the **EC2 service**.

Can it use a Gateway Endpoint?

❌ No.

Gateway Endpoints only support:

* S3
* DynamoDB

That's it.

---

# So AWS invented something new

An **Interface Endpoint**.

Think of it like AWS building a **private door** into your VPC.

Instead of going:

```text
Private EC2
      │
      ▼
NAT Gateway
      │
      ▼
Internet
      │
      ▼
EC2 API
```

it becomes:

```text
Private EC2
      │
      ▼
Interface Endpoint (ENI)
      │
      ▼
EC2 API
```

No internet.

No NAT.

Private AWS network.

---

# The biggest difference

## Gateway Endpoint

Creates:

```text
Route Table Entry
```

Example:

```text
Destination: pl-xxxxxxxx

↓

Gateway Endpoint
```

No ENI.

No Security Group.

---

## Interface Endpoint

Creates:

```text
ENI
```

An **Elastic Network Interface**.

Think of it like AWS plugging a **new network cable** into your subnet.

That's why Interface Endpoints need:

* ✅ Private IP
* ✅ Security Group

because an ENI is a network interface.

---

# Question 1 😊

Imagine your house.

Which one sounds more like an **Interface Endpoint**?

### A

A new road is added to your city.

### B

AWS installs a **new door** directly in your house.

👉 Reply with just **A** or **B**.

(We'll continue only after this. One small step at a time.)

***

🎉 **Correct!** The answer is **B**.

Why?

Because an **Interface Endpoint creates a new ENI (Elastic Network Interface)** inside your subnet.

Think of it like this:

```text
Your House (Private EC2)
        │
        ▼
🚪 New Private Door (Interface Endpoint / ENI)
        │
        ▼
AWS Service (EC2 API)
```

AWS literally creates a **network interface with a private IP address** inside your subnet.

That's why it needs a **Security Group**—because an ENI can have Security Groups attached.

---

# Compare with Gateway Endpoint

Gateway Endpoint doesn't create a door.

It simply changes the road signs (route table).

```text
Private EC2
      │
      ▼
Route Table
      │
      ▼
Gateway Endpoint
      │
      ▼
Amazon S3
```

Notice:

* No ENI ❌
* No Security Group ❌

---

# Memory Trick 🧠

### Gateway Endpoint

👉 Changes the **map** (Route Table).

### Interface Endpoint

👉 Creates a **new network card (ENI)** inside your subnet.

---

# Quiz 2 😊

Which endpoint creates an **ENI**?

**A. Gateway Endpoint**

**B. Interface Endpoint**

(Just answer **A** or **B**.)


***

🎉 **100% Correct!** ✅

**Answer: B – Interface Endpoint**

Because:

```text
Interface Endpoint
        │
        ▼
Creates an ENI
        │
        ▼
Gets a Private IP
        │
        ▼
Needs a Security Group
```

Remember this chain:

> **Interface Endpoint → ENI → Private IP → Security Group**

This is asked a lot in AWS interviews.

---

# Now let's create one.

## Step 1

Go to:

```text
VPC
   ↓
Endpoints
   ↓
Create Endpoint
```

---

## Step 2

You'll see **Endpoint type**.

Choose:

```text
AWS services
```

(Do **not** choose Resource or Marketplace.)

---

## Step 3

Now AWS asks for a **Service**.

Search for:

```text
EC2
```

You should see something like:

```text
com.amazonaws.us-west-2.ec2
```

⚠️ Since your lab is in **us-west-2**, make sure you choose the **EC2 service for us-west-2**.

---

## 🧠 Why are we choosing EC2?

Not because we're creating an EC2.

We're creating a **private connection to the EC2 API**.

Without an Interface Endpoint:

```text
Private EC2
      │
      ▼
NAT Gateway
      │
      ▼
Internet
      │
      ▼
EC2 API
```

With an Interface Endpoint:

```text
Private EC2
      │
      ▼
ENI (Interface Endpoint)
      │
      ▼
EC2 API
```

No internet is needed.

---

## Stop here.

Tell me when you've reached the **Create Endpoint** page and selected:

```text
Service = com.amazonaws.us-west-2.ec2
```

Don't click **Create** yet—we'll configure each option together so you understand what every setting does instead of just following steps.

***

Perfect! 🌟 Now we'll configure it one screen at a time.

---

# Step 4 – Name

Enter:

```text
cloudadhar-day6-ec2-endpoint
```

This is just a label to help you identify it later.

---

# Step 5 – VPC

Select:

```text
cloudadhar-day5-vpc
```

### 🤔 Why?

Because that's where your **Private EC2** lives.

Think of it like this:

```text
House (Private EC2)
        │
        ▼
Need a new private door
```

The new door (Interface Endpoint) must be built **inside the same neighborhood (VPC)**.

---

# Step 6 – Endpoint Type

It should already show:

```text
Interface
```

✅ Leave it as **Interface**.

---

# Step 7 – Subnets

This is important.

The lab says:

> **Select Private-A only for the cost-safe lab.**

So select only:

```text
cloudadhar-private-a
```

or

```text
10.10.11.0/24
```

Do **NOT** select Public-A or Private-B.

---

## 🤔 Why only Private-A?

Because AWS creates **one ENI per selected subnet**.

If you select:

```
Private-A
Private-B
```

AWS creates:

```
ENI #1 in Private-A
ENI #2 in Private-B
```

That means **two Interface Endpoints**, which costs more.

For learning, **one subnet is enough**.

---

# 🧠 Mini Quiz

Suppose you select **2 subnets**.

How many ENIs will AWS create?

A. 1

B. 2

(Answer before we continue.)

***

Good guess! 😊 But the correct answer is:

## ❌ Not A

## ✅ Correct answer: **B. 2**

Here's why.

---

Imagine your VPC has two private subnets.

```text
Private-A
Private-B
```

If you select **both**, AWS creates:

```text
Private-A
    │
    ▼
ENI #1

Private-B
    │
    ▼
ENI #2
```

**Rule to remember:**

> **1 selected subnet = 1 ENI**

So:

| Selected Subnets | ENIs Created |
| ---------------- | -----------: |
| 1                |            1 |
| 2                |            2 |
| 3                |            3 |

---

## Why does AWS do this?

Remember:

An **Interface Endpoint is an ENI**.

An ENI **lives inside a subnet**.

One ENI **cannot** be in two subnets at the same time.

So AWS creates **one ENI for each subnet you select**.

---

# 🧠 Memory Trick

```
Gateway Endpoint
        │
        ▼
Route Table

Interface Endpoint
        │
        ▼
One ENI per selected subnet
```

---

## ✅ Now continue

On the Create Endpoint page:

* **VPC:** `cloudadhar-day5-vpc` ✅
* **Subnet:** **Only** `cloudadhar-private-a` ✅

Don't click **Create** yet.

### Tell me what you see under **Security Groups**.

Is it asking you to:

* Select an existing Security Group, or
* Create a new one?

We'll explain **why** an Interface Endpoint needs a Security Group before we proceed.

<img width="2560" height="1536" alt="image" src="https://github.com/user-attachments/assets/0bf89d34-c7bb-47a9-a1b4-5156509df6c4" />
<img width="2552" height="845" alt="image" src="https://github.com/user-attachments/assets/4baec1b3-fc2a-4878-bb05-d42023cdd52f" />


***

Excellent! This is where most people just click randomly. Let's understand **why**.

---

# First, remember what an Interface Endpoint is.

Earlier, we learned:

```text
Interface Endpoint
        │
        ▼
Creates an ENI
        │
        ▼
Gets a Private IP
        │
        ▼
Needs a Security Group
```

The Security Group here is **not for your EC2 instance**.

It is for the **new ENI** that AWS is about to create.

Think of it like this:

```text
Private EC2
      │
      │ HTTPS (443)
      ▼
+---------------------------+
| Interface Endpoint (ENI)  |
| Security Group            |
+---------------------------+
      │
      ▼
EC2 API
```

The Security Group on the endpoint asks:

> "Who is allowed to talk to me?"

---

# Which Security Group should we use?

Your lab instructions say:

> Attach an endpoint Security Group allowing TCP 443 from the private instance's Security Group.

The **best practice** is to create a **new Security Group** for the endpoint.

### Why not use `cloudadhar-day6-private-sg`?

Because:

* `cloudadhar-day6-private-sg` protects your **EC2 instance**.
* The endpoint should have **its own Security Group** so you can control access independently.

In production, AWS recommends separate Security Groups.

---

# Step 8 – Create a new Security Group

Go to:

**EC2 → Security Groups → Create Security Group**

Fill in:

**Name**

```text
cloudadhar-day6-endpoint-sg
```

**Description**

```text
Allows Private EC2 to access the EC2 Interface Endpoint
```

**VPC**

```text
cloudadhar-day5-vpc
```

---

# Inbound Rules

Add **one** rule:

| Type  | Protocol | Port | Source                                                                |
| ----- | -------- | ---- | --------------------------------------------------------------------- |
| HTTPS | TCP      | 443  | **cloudadhar-day6-private-sg** (select the Security Group, not an IP) |

Notice we're choosing a **Security Group as the source**, not `0.0.0.0/0`.

That means:

> Only instances that belong to `cloudadhar-day6-private-sg` can reach this endpoint.

---

# Outbound Rules

Leave the default:

```text
All traffic
```

That's fine for this lab.

---

## Mini Quiz 😊

Why are we allowing **TCP 443**?

A. Because EC2 API uses HTTPS.

B. Because EC2 API uses SSH.

Reply with **A** or **B** before creating the Security Group.

***

🎉 Correct! **A** is the right answer.

The EC2 API communicates over **HTTPS (TCP 443)**.

Now let's fix the source selection.

---

# Don't type an IP address.

For the **Source**, we want to select a **Security Group**.

## Step 1

Click inside the **Source** box.

You should see a small drop-down.

Instead of **Custom**, change it to:

```text
Security group
```

or sometimes it appears as:

```text
Custom → Security Group
```

(depending on the AWS Console version).

---

## Step 2

After selecting **Security group**, another box should appear.

Search for:

```text
cloudadhar-day6-private-sg
```

or

```text
sg-0de7026604328cf54
```

That is the Security Group attached to your private EC2.

---

## If you still don't see it

Please tell me:

### What options do you see when you click the **Source** drop-down?

For example, do you see something like:

* Anywhere-IPv4
* Anywhere-IPv6
* My IP
* Custom
* **Security Group** ✅

or something different?

---

## Don't create the Security Group yet.

We'll get the source exactly right first.

📷 **The fastest way:** please upload a screenshot of just the **Create Security Group** page showing the **Inbound Rule** section with the **Source** dropdown open. Then I can point to exactly what to click.

***

🎉 **Perfect! That's exactly what we wanted.** ✅

You have selected:

```text
HTTPS
TCP
443

Source:
sg-0de7026604328cf54
```

That **is** your `cloudadhar-day6-private-sg`.

AWS is showing the **Security Group ID** instead of the name, and that's completely fine.

---

# What does this rule mean?

Let's say it like a story.

Your Private EC2 says:

> "Can I talk to the Interface Endpoint?"

The Interface Endpoint's Security Group checks:

```text
Are you a member of Security Group
sg-0de7026604328cf54?
```

If **YES** ✅

```text
Private EC2
      │
HTTPS (443)
      ▼
Interface Endpoint
```

If **NO** ❌

```text
Connection blocked
```

Notice we're **not** allowing:

```text
0.0.0.0/0
```

That would mean:

> "Anyone can connect."

Instead, we're saying:

> "Only my Private EC2 can connect."

That's much more secure.

---

# Step 9

Now:

1. Click **Create Security Group**.
2. Tell me when it's created.

Then we'll:

* Attach this Security Group to the Interface Endpoint.
* Enable **Private DNS**.
* Create the endpoint.
* Inspect the new ENI (this is the coolest part—you'll actually see the network interface AWS creates).


***
Excellent! 🎉 You're doing great.

Now we're going to create the **Interface Endpoint** using that new Security Group.

---

# Step 10 – Go back to the Create Endpoint page

If it's still open, great.

If not:

**VPC → Endpoints → Create Endpoint**

You should already have:

* ✅ Service: `com.amazonaws.us-west-2.ec2`
* ✅ VPC: `cloudadhar-day5-vpc`
* ✅ Subnet: `cloudadhar-private-a`

---

# Step 11 – Security Group

Under **Security Groups**:

❌ Uncheck any existing Security Groups (if selected).

✅ Select only:

```text
cloudadhar-day6-endpoint-sg
```

This is the one you just created.

---

# 🤔 Why don't we use the Private EC2 Security Group?

Remember:

Your Private EC2 has its own Security Group.

The **Interface Endpoint** is a **different network interface (ENI)**, so it has its **own Security Group**.

Think of it like two houses:

```text
House 1 (Private EC2)
    │
    │ HTTPS 443
    ▼
House 2 (Interface Endpoint ENI)
```

Each house has its own front door and its own lock.

---

# Step 12 – Private DNS

Look for:

```text
Enable DNS name
```

or

```text
Enable Private DNS
```

Make sure it is:

✅ **Checked**

---

## 🤔 Why enable Private DNS?

Without Private DNS:

When you type:

```bash
aws ec2 describe-instances
```

your EC2 tries to reach:

```text
ec2.us-west-2.amazonaws.com
```

Normally that name points to a **public IP**.

---

With **Private DNS enabled**:

AWS secretly changes the answer.

Instead of:

```text
ec2.us-west-2.amazonaws.com
      │
      ▼
Public IP
```

it becomes:

```text
ec2.us-west-2.amazonaws.com
      │
      ▼
Private IP of your Interface Endpoint ENI
```

Your application doesn't know anything changed—it still uses the same hostname.

This is one of the biggest advantages of Interface Endpoints.

---

# Step 13

Click:

```text
Create Endpoint
```

It will probably show:

```text
Pending
```

That's normal.

---

## Your turn

Tell me:

1. ✅ Is **Private DNS** enabled?
2. ✅ Did you click **Create Endpoint**?
3. What is its status now?

(Usually **Pending** for a few minutes, then **Available**.)

<img width="2560" height="4083" alt="image" src="https://github.com/user-attachments/assets/32dbb408-3783-4eb5-9ebd-e91f2c7dcabd" />

<img width="2257" height="315" alt="image" src="https://github.com/user-attachments/assets/6cd71266-8a96-4011-8a2d-11d37865973d" />

🎉🎉 **Fantastic!** You've just created your **first Interface VPC Endpoint!** This is a major AWS networking concept.

Now let's verify it properly instead of just trusting that it worked.

---

# Step 1 – Wait for the Endpoint

Go to:

```text
VPC
   ↓
Endpoints
   ↓
cloudadhar-day6-ec2-endpoint
```

Initially it may show:

```text
Pending
```

After about 1–3 minutes it should become:

```text
Available
```

⏳ Wait until it says **Available**.

---

# Step 2 – While it's becoming Available, let's understand what AWS is doing

When you clicked **Create**, AWS didn't just create a "setting."

It actually created a **new network card (ENI)** inside your subnet.

Before:

```text
Private Subnet

+-----------------------+
| Private EC2           |
| 10.10.11.10           |
+-----------------------+
```

After:

```text
Private Subnet

+-----------------------+
| Private EC2           |
| 10.10.11.10           |
+-----------------------+

+-----------------------+
| Interface Endpoint    |
| ENI                   |
| 10.10.11.xxx          |
+-----------------------+
```

Notice:

* Your EC2 still has **10.10.11.10**
* AWS created **another private IP** for the Interface Endpoint.

That's why Interface Endpoints cost more than Gateway Endpoints—they create actual ENIs.

---

# Step 3 – Verify the ENI

Once the endpoint is **Available**:

Open:

```text
VPC
   ↓
Endpoints
   ↓
cloudadhar-day6-ec2-endpoint
```

You'll see details such as:

* Network Interface ID (starts with `eni-...`)
* Private IP address
* DNS names
* Security Group (`cloudadhar-day6-endpoint-sg`)

This is the proof that AWS created the ENI.

---

# 🎓 Mini Quiz

Imagine you're explaining this to a friend.

**Question:**

Why does an **Interface Endpoint** need a Security Group, but a **Gateway Endpoint** doesn't?

Try answering in your own words.

💡 Hint:

* Gateway Endpoint = Route Table
* Interface Endpoint = ENI

---

# After the endpoint becomes **Available**

Please send me:

1. ✅ The **Status** (Available?)
2. ✅ The **Network Interface ID (eni-...)**
3. ✅ The **Private IP** of the endpoint

Then we'll do the final validation:

```bash
nslookup ec2.us-west-2.amazonaws.com
```

This is the "magic moment" where you'll actually see the EC2 service name resolve to a **private IP** instead of a public one. That's what proves Private DNS is working.

***

🎉🎉 **YES!! You successfully created an Interface Endpoint!** Excellent work.

Let's review what you have.

---

# ✅ What I see

### Status

```text
Available
```

✅ Perfect.

---

### Service

```text
com.amazonaws.us-west-2.ec2
```

✅ Correct.

---

### Endpoint Type

```text
Interface
```

✅ Correct.

---

### ENI

```text
eni-004187e9108ef0aa8
```

<img width="2222" height="1072" alt="image" src="https://github.com/user-attachments/assets/d8bfd313-949c-45ca-92eb-886283dc33c7" />


🎉 **This is the proof** that AWS created a network interface inside your subnet.

---

### Subnet

```text
subnet-082932cb27f0148df
```

✅ This is your **cloudadhar-private-a** subnet.

---

### Private DNS

```text
Private DNS names enabled
Yes
```

⭐⭐⭐⭐⭐

This is the most important part.

---

# Let's compare both endpoints

## Gateway Endpoint (S3)

```text
Private EC2
      │
      ▼
Route Table
      │
      ▼
S3 Gateway Endpoint
      │
      ▼
Amazon S3
```

AWS created:

* ✅ Route Table entry
* ❌ No ENI
* ❌ No Security Group

---

## Interface Endpoint (EC2)

```text
Private EC2
      │
 HTTPS 443
      ▼
ENI
(Interface Endpoint)
      │
      ▼
EC2 API
```

AWS created:

* ✅ ENI (`eni-004187e9108ef0aa8`)
* ✅ Private IP
* ✅ Security Group
* ✅ Private DNS

---

# 🎯 Why Private DNS is so powerful

Look carefully at what AWS created:

You have this DNS name:

```text
ec2.us-west-2.amazonaws.com
```

Normally, that hostname points to a **public** AWS endpoint.

But because you enabled **Private DNS**, inside your VPC AWS changes the answer.

Instead of:

```text
Private EC2
      │
      ▼
ec2.us-west-2.amazonaws.com
      │
      ▼
Public EC2 API
```

AWS silently changes it to:

```text
Private EC2
      │
      ▼
ec2.us-west-2.amazonaws.com
      │
      ▼
YOUR Interface Endpoint ENI
      │
      ▼
EC2 API
```

Your application doesn't have to change its code. It still calls the same hostname, but AWS routes it privately.

---

# Now let's prove it

Go back to your **Session Manager** terminal on the **private EC2** and run:

```bash
nslookup ec2.us-west-2.amazonaws.com
```

If `nslookup` isn't installed, try:

```bash
getent hosts ec2.us-west-2.amazonaws.com
```

or:

```bash
dig ec2.us-west-2.amazonaws.com
```

---

## What are we looking for?

We expect the hostname to resolve to a **private IP address** (inside your VPC) rather than a public AWS IP. That demonstrates that **Private DNS** is working and your EC2 is using the Interface Endpoint.

---

<img width="787" height="716" alt="image" src="https://github.com/user-attachments/assets/e0b3e774-1019-45ea-9992-e46f17335d71" />

Awesome! 😊 You're almost done with Part 5.

Let's validate it.

## Step 1

Connect to your **private EC2** using **Session Manager**.

Run:

```bash
nslookup ec2.us-west-2.amazonaws.com
```

---

### If you get:

```text
nslookup: command not found
```

don't worry.

Run:

```bash
getent hosts ec2.us-west-2.amazonaws.com
```

If that also doesn't work, run:

```bash
dig ec2.us-west-2.amazonaws.com
```

---

## Step 2

Paste the output here.

---

# 🎯 What are we proving?

Remember our story.

Before Interface Endpoint:

```text
Private EC2
      │
      ▼
NAT Gateway
      │
      ▼
Internet
      │
      ▼
EC2 API
```

After Interface Endpoint:

```text
Private EC2
      │
      ▼
Interface Endpoint (ENI)
      │
      ▼
EC2 API
```

The DNS lookup should show that `ec2.us-west-2.amazonaws.com` now resolves to the **private IP of your Interface Endpoint ENI**, proving that **Private DNS** is working.

---

## 🧠 One important note

Sometimes AWS may return multiple private IPs (if the service has multiple endpoint IPs for availability), and that's okay. The key thing is that they should be **private VPC addresses**, not public internet addresses.

***

# 🎉🎉 PERFECT!! YOU JUST PROVED PRIVATE DNS WORKS!! 🎉🎉

This is exactly the output we wanted.

Let's understand every line.

---

# 1. nslookup

You ran:

```bash
nslookup ec2.us-west-2.amazonaws.com
```

AWS replied:

```text
Name: ec2.us-west-2.amazonaws.com
Address: 10.10.11.155
```

### What does this mean?

Look at the IP:

```text
10.10.11.155
```

Is it:

* Public IP ❌
* Private IP ✅

Remember your VPC CIDR:

```text
10.10.0.0/16
```

Your subnet:

```text
10.10.11.0/24
```

So:

```text
10.10.11.155
```

belongs **inside your VPC**.

⭐⭐⭐⭐⭐

That proves AWS changed DNS to point to your Interface Endpoint.

---

# 2. getent

You ran:

```bash
getent hosts ec2.us-west-2.amazonaws.com
```

Output:

```text
10.10.11.155
```

Same answer.

Another confirmation.

---

# 3. dig

Again:

```text
ANSWER SECTION:

ec2.us-west-2.amazonaws.com

↓

10.10.11.155
```

Exactly what we expected.

---

# Why is this amazing?

Without an Interface Endpoint:

```text
Private EC2
      │
      ▼
ec2.us-west-2.amazonaws.com
      │
      ▼
Public AWS IP
      │
      ▼
NAT Gateway
      │
      ▼
Internet
```

---

With an Interface Endpoint:

```text
Private EC2
      │
      ▼
ec2.us-west-2.amazonaws.com
      │
      ▼
10.10.11.155
      │
      ▼
Interface Endpoint ENI
      │
      ▼
EC2 API
```

Notice:

❌ No Internet

❌ No NAT

✅ Private AWS Network

---

# This is the magic of Private DNS

Your application still uses:

```bash
aws ec2 describe-instances
```

It still contacts:

```text
ec2.us-west-2.amazonaws.com
```

But AWS secretly changes the DNS answer.

Instead of a public IP:

```text
52.x.x.x
```

it returns:

```text
10.10.11.155
```

The application doesn't know anything changed.

---

# 🧠 Interview Question

**Q: How can you verify that an Interface Endpoint with Private DNS is working?**

**Answer:**

> Run `nslookup`, `dig`, or `getent hosts` for the service hostname (for example, `ec2.us-west-2.amazonaws.com`). If it resolves to a **private IP address** inside your VPC instead of a public IP, then Private DNS is working and traffic will use the Interface Endpoint.

---

# ⭐⭐⭐ Memory Trick

## Gateway Endpoint

```text
Changes

↓

Route Table
```

---

## Interface Endpoint

```text
Creates

↓

ENI
↓

Private IP
↓

Security Group
↓

Private DNS
```

Remember this sequence:

> **Interface Endpoint → ENI → Private IP → Security Group → Private DNS**

---

# 🎉 Part 5 Complete

You have successfully completed:

* ✅ Created an Interface Endpoint
* ✅ Attached a dedicated Security Group
* ✅ Enabled Private DNS
* ✅ Verified the endpoint created an ENI
* ✅ Verified DNS resolves to a private IP (`10.10.11.155`)
* ✅ Proved traffic stays on the AWS private network

---

# ⚠️ Before Part 6

Your lab instructions say:

> **Delete the Interface Endpoint immediately after validation.**

Go to:

**VPC → Endpoints → `cloudadhar-day6-ec2-endpoint` → Delete**

Wait until it is deleted.

This avoids unnecessary hourly charges.

---

# 🧠 Before we move to Part 6, one last quiz (no memorization)

Imagine your private EC2 wants to talk to:

### 1. Amazon S3

Which endpoint should you choose?

### 2. EC2 API

Which endpoint should you choose?

### 3. Why can't a Gateway Endpoint be used for the EC2 API?

Answer these in your own words. If you can explain them, it means you truly understand the concepts rather than just following the lab. Then we'll move on to **Part 6 – VPC Flow Logs**.

***

Very close! 😊 You mixed up **private/public** with **endpoint types**.

The question is asking **which endpoint type**, not whether the connection is private or public.

Let's learn it like a kid.

---

# Imagine AWS has two special doors.

🚪 **Door 1 = Gateway Endpoint**

AWS says:

> "This door is only for **S3** and **DynamoDB**."

---

🚪 **Door 2 = Interface Endpoint**

AWS says:

> "This door is for **EC2 API**, **SSM**, **Secrets Manager**, **CloudWatch**, and many other AWS services."

---

## Question 1

### Your Private EC2 wants to talk to Amazon S3.

Which endpoint?

✅ **Gateway Endpoint**

Because AWS only supports **S3** and **DynamoDB** with Gateway Endpoints.

Diagram:

```text
Private EC2
      │
      ▼
Gateway Endpoint
      │
      ▼
Amazon S3
```

---

## Question 2

### Your Private EC2 wants to talk to the EC2 API.

Which endpoint?

✅ **Interface Endpoint**

Diagram:

```text
Private EC2
      │
      ▼
Interface Endpoint (ENI)
      │
      ▼
EC2 API
```

---

## Question 3

### Why can't a Gateway Endpoint be used for the EC2 API?

Because **AWS only supports Gateway Endpoints for two services**:

* Amazon S3
* Amazon DynamoDB

The EC2 API is **not one of them**, so you must use an **Interface Endpoint**.

---

# 🎯 Super Easy Memory Trick

```text
Gateway Endpoint
        │
        ├── S3 ✅
        └── DynamoDB ✅
```

Everything else:

```text
Interface Endpoint
        │
        ├── EC2 API ✅
        ├── SSM ✅
        ├── Secrets Manager ✅
        ├── CloudWatch ✅
        ├── KMS ✅
        └── Many more...
```

---

# ⭐ Interview Table

| Service               | Endpoint Type        |
| --------------------- | -------------------- |
| Amazon S3             | ✅ Gateway Endpoint   |
| DynamoDB              | ✅ Gateway Endpoint   |
| EC2 API               | ✅ Interface Endpoint |
| Systems Manager (SSM) | ✅ Interface Endpoint |
| Secrets Manager       | ✅ Interface Endpoint |
| CloudWatch            | ✅ Interface Endpoint |

---

# 🌟 Now let's check your understanding

Answer these:

### 1. Which endpoint **creates an ENI**?

### 2. Which endpoint **modifies the Route Table**?

### 3. Which endpoint **needs a Security Group**?

### 4. Which endpoint **supports only S3 and DynamoDB**?

Try answering in your own words. If you get these right, you've mastered the difference and we'll move on to **Part 6 – VPC Flow Logs**.

***

Excellent! 😊 I'll answer these and explain **why**, so you never have to memorize them.

---

# Imagine two delivery methods

## 🚚 Gateway Endpoint = A new road

AWS builds a **new road (route)** to S3 or DynamoDB.

It does **not** create a network card (ENI).

---

## 🏠 Interface Endpoint = A small office inside your VPC

AWS creates a **new network interface (ENI)** inside your subnet.

That ENI has:

* Private IP
* Security Group
* Private DNS

Your EC2 talks to this ENI.

---

# 1. Which endpoint creates an ENI?

✅ **Interface Endpoint**

Because AWS creates a network interface inside your subnet.

You even saw it:

```text
eni-004187e9108ef0aa8
```

That ENI **is** your Interface Endpoint.

---

# 2. Which endpoint modifies the Route Table?

✅ **Gateway Endpoint**

Remember when you created the S3 Gateway Endpoint?

AWS automatically added:

```text
pl-68a54001
      ↓
Gateway Endpoint
```

inside your **Private Route Table**.

So:

```text
Private Route Table
        │
        ▼
S3 Gateway Endpoint
```

---

# 3. Which endpoint needs a Security Group?

✅ **Interface Endpoint**

Why?

Because an Interface Endpoint is actually an **ENI**.

And ENIs can have Security Groups.

Gateway Endpoints don't have ENIs, so they don't need Security Groups.

---

# 4. Which endpoint supports only S3 and DynamoDB?

✅ **Gateway Endpoint**

Only these two services.

Nothing else.

---

# 🌟 The Complete Picture

## Gateway Endpoint

```text
Creates:
──────────────

✔ Route Table Entry

❌ No ENI

❌ No Security Group

✔ S3

✔ DynamoDB
```

---

## Interface Endpoint

```text
Creates:
──────────────

✔ ENI

✔ Private IP

✔ Security Group

✔ Private DNS

✔ EC2 API

✔ SSM

✔ CloudWatch

✔ Secrets Manager

✔ KMS

✔ Many more...
```

---

# 🎯 One Last Quiz

Fill in the blanks:

### Case 1

> My private EC2 wants to download an object from an S3 bucket without using the internet.

I should create a **________ Endpoint**.

---

### Case 2

> My private EC2 wants to call the EC2 API without using the internet.

I should create an **________ Endpoint**.

---

### Case 3

> I ran:

```bash
nslookup ec2.us-west-2.amazonaws.com
```

and got:

```text
10.10.11.155
```

What does that prove?

Answer these three in your own words. Once you get them right, we'll move on to **Part 6 – VPC Flow Logs**, the final part of Day 6.

***

🎉 **100%!** You got Cases 1 and 2 exactly right.

Let's improve Case 3 just a little.

---

# ✅ Case 1

> My private EC2 wants to download an object from an S3 bucket without using the internet.

Your answer:

> **Gateway Endpoint**

✅ Correct!

Because S3 supports **Gateway Endpoints**.

---

# ✅ Case 2

> My private EC2 wants to call the EC2 API without using the internet.

Your answer:

> **Interface Endpoint**

✅ Correct!

Because EC2 API supports **Interface Endpoints (AWS PrivateLink)**.

---

# ✅ Case 3

You answered:

> **Private endpoint**

👍 You're on the right track. Let's make it interview-ready.

When you ran:

```bash
nslookup ec2.us-west-2.amazonaws.com
```

AWS returned:

```text
10.10.11.155
```

Ask yourself:

**Is `10.10.11.155` a public IP or a private IP?**

👉 It's a **private IP** because it belongs to your VPC CIDR (`10.10.0.0/16`).

So what does that prove?

### Best answer

> **It proves that Private DNS is working. The hostname `ec2.us-west-2.amazonaws.com` resolves to the private IP address of the Interface Endpoint ENI, so traffic stays on the AWS private network instead of going through the internet or a NAT Gateway.**

---

## Think of it like this

### Without Interface Endpoint

```text
Private EC2
      │
      ▼
NAT Gateway
      │
      ▼
Internet
      │
      ▼
EC2 API
```

---

### With Interface Endpoint

```text
Private EC2
      │
      ▼
Private DNS
      │
      ▼
10.10.11.155
      │
      ▼
Interface Endpoint ENI
      │
      ▼
EC2 API
```

No internet. No NAT. Everything stays inside AWS's private network.

---

# 🎉 Congratulations!

You've completed:

* ✅ NAT Gateway
* ✅ Private EC2 with Session Manager
* ✅ Security Groups vs NACL
* ✅ S3 Gateway Endpoint
* ✅ EC2 Interface Endpoint
* ✅ Private DNS validation

The only remaining lab is **Part 6 – VPC Flow Logs**.

We'll learn:

* What VPC Flow Logs actually record.
* The difference between `ACCEPT` and `REJECT`.
* Why Flow Logs don't capture packet contents.
* How to query the logs in CloudWatch Logs Insights.

This is the final section of Day 6.

***

Awesome! 🎉 Let's finish **Day 6** together.

We'll go **slowly** like before, and I'll explain **why** at every step.

---

# Part 6 – VPC Flow Logs

## 🎯 Goal

We want to answer this question:

> **"Can AWS tell us which network traffic was allowed or blocked?"**

Answer:

✅ **Yes, using VPC Flow Logs.**

---

# Imagine a Security Guard 🧑‍✈️

Your VPC is a company building.

People (network packets) keep entering and leaving.

The security guard writes in a notebook:

```text
10.10.11.10 came in

Allowed

------------------------

35.94.190.113 tried to enter

Blocked

------------------------

10.10.11.10 talked to S3

Allowed
```

Notice something.

The guard **doesn't write what they talked about.**

He only writes:

* Who
* From where
* To where
* Allowed or Denied

That notebook is exactly what **VPC Flow Logs** are.

---

# What Flow Logs Record

They record **network metadata**, not the actual data.

For example:

```text
Source IP

Destination IP

Port

Protocol

Packets

Bytes

Time

ACCEPT or REJECT
```

They **do NOT** record:

❌ Passwords

❌ Website contents

❌ HTTP body

❌ Packet payload

---

# Think of it like a courier

Suppose Amazon delivers a package.

The delivery company records:

```text
From:
Mumbai

To:
Pune

Weight:
2 kg

Delivered:
Yes
```

But they do **NOT** open the package.

Flow Logs work the same way.

---

# Where do Flow Logs store their notebook?

Three choices:

1. CloudWatch Logs ⭐ (most common for labs)
2. Amazon S3
3. Amazon Data Firehose

For today's lab we'll use:

✅ **CloudWatch Logs**

---

# Part 6 Step 1

Go to

```
VPC Console
```

↓

```
Your VPC
```

↓

```
Flow Logs
```

↓

Click

```
Create Flow Log
```

<img width="2557" height="897" alt="image" src="https://github.com/user-attachments/assets/39097bf0-ab85-4720-97c7-769c31cb6d31" />


***

Great! 👍 Now we will create the **VPC Flow Log** step by step.

You should be on:

```text
VPC → Flow Logs → Create Flow Log
```

Let's fill it carefully.

---

# Step 1: Name

You can give:

```text
cloudadhar-day6-flow-logs
```

This is only a label to identify it.

---

# Step 2: Filter

You will see:

```
Filter
```

Options:

* Accepted
* Rejected
* All

Choose:

✅ **All**

Why?

Because we want to see both:

```text
ACCEPT ✅
```

and

```text
REJECT ❌
```

Later we will intentionally create a blocked request and verify it.

---

# Step 3: Maximum aggregation interval

You may see:

```
Maximum aggregation interval
```

Choose:

✅ **1 minute**

Why?

For a lab, we don't want to wait 10 minutes to see logs.

---

# Step 4: Destination

You will see:

```
Destination
```

Choose:

✅ **Send to CloudWatch Logs**

Why?

Because we can easily search using CloudWatch Logs Insights.

---

# Step 5: Log Group

It may ask for:

```
Destination log group
```

Create:

```text
/aws/vpc/flowlogs/cloudadhar-day6
```

or any name like:

```text
cloudadhar-day6-flowlogs
```

---

# Step 6: IAM Role

You need a role that allows VPC Flow Logs to write logs.

Click:

```
Set up permissions
```

or

```
Create IAM role
```

AWS will create something like:

```text
vpc-flow-logs-role
```

Select that role.

---

# Step 7: Create

Click:

```
Create Flow Log
```

---

After creation, wait about 1–2 minutes.

Then tell me:

✅ Flow Log status = Active?

and paste what you see.

---

Remember what we are proving:

```text
Web EC2
   |
   | HTTP request
   ↓
VPC Flow Logs
   |
   ↓
CloudWatch
```

Then we will create:

1. ✅ ACCEPT traffic
2. ❌ REJECT traffic using NACL
3. 🔍 Search logs

This is the final detective part of Day 6. 😊



<img width="2560" height="2281" alt="image" src="https://github.com/user-attachments/assets/abf00803-cb2d-473e-9490-6d88a0507709" />
<img width="2500" height="881" alt="image" src="https://github.com/user-attachments/assets/365717b2-2610-418d-963c-b08f1ae0c769" />

***

No problem 😊. You are in **CloudWatch**, but you are currently on the **Dashboard/Home page**.

The log group is under **Logs → Log groups**.

Follow me step by step.

---

## Step 1

In the left menu, find:

```
Logs
```

You already see:

```
Logs
 ├── Log Management
 ├── Log Analytics
 └── Log Anomalies
```

Click:

✅ **Log Management**

---

## Step 2

Inside Log Management, look for:

```
Log groups
```

Click:

✅ **Log groups**

---

## Step 3

You should see:

```
/aws/vpc/flowlogs/cloudadhar-day6
```

Click it.

---

## If you still don't see it

Use the top search bar in CloudWatch and search:

```
cloudadhar-day6
```

or:

```
flowlogs
```

---

## Important check

Your Flow Log creation showed:

```
Destination Name
/aws/vpc/flowlogs/cloudadhar-day6
```

and:

```
State: Active
```

So the log group should exist.

Sometimes CloudWatch takes 1–2 minutes to create the first log stream.

---

Do this:

1. Click **Log Management**
2. Click **Log groups**
3. Search `cloudadhar`

Tell me what appears. 👍


***

🎉🎉 **Excellent! Part 6 Step 1 is COMPLETE.** 🎉🎉

You successfully created VPC Flow Logs.

Let's understand what you created.

---

# ✅ Your Flow Log Configuration

## Resource monitored

```text
VPC:
cloudadhar-day5-vpc

ID:
vpc-0d6b503b8b32c7cb9
```

Meaning:

AWS will watch network traffic flowing through this VPC.

---

## Traffic captured

You selected:

```text
Traffic Type: All
```

Perfect ✅

This means AWS records:

```text
ACCEPT ✅

and

REJECT ❌
```

---

## Destination

You selected:

```text
cloud-watch-logs
```

So the records go here:

```text
/aws/vpc/flowlogs/cloudadhar-day6
```

---

## Aggregation

You selected:

```text
1 minute
```

Perfect for a lab.

It means:

> "AWS will collect packets and create flow records every minute."

---

## State

Most important:

```text
State: Active
```

🎉 This means Flow Logs are running.

---

# What happens now?

Currently AWS is just watching.

We need to create traffic.

We need two examples:

---

# Test 1: ACCEPT Traffic ✅

Your web EC2:

```text
cloudadhar-day6-web-ec2
Public IP:
35.94.190.113
```

Open browser:

```
http://35.94.190.113
```

You already know this works.

This creates:

```text
Internet Client
      |
      |
      v
Web EC2 :80

Result:
ACCEPT
```

<img width="850" height="297" alt="image" src="https://github.com/user-attachments/assets/d4eb974c-7c79-44b4-9545-a624b85b3b33" />


---

# Test 2: REJECT Traffic ❌

We will repeat your NACL trick.

Remember:

Your NACL rule:

```text
Rule 90
HTTP
35.94.190.113/32
DENY
```

blocked your own IP.

<img width="2535" height="692" alt="image" src="https://github.com/user-attachments/assets/cc7292e7-0244-4268-ae84-36f32cab6967" />


That creates:

```text
Internet Client
      |
      |
      X
NACL DENY

Result:
REJECT
```




---

# Now Step 2

Let's first create some ACCEPT traffic.

Do this:

Open a new browser tab.

Go to:

```
http://35.94.190.113
```

Wait until the page loads.

Refresh 2-3 times.

This creates flow records.

---

Wait around **2 minutes**.

Then go to:

```
CloudWatch
   ↓
Log groups
   ↓
/aws/vpc/flowlogs/cloudadhar-day6
```

Tell me when you reach the Log Group.

Don't run queries yet. We'll do it together. 😊

<img width="2546" height="1106" alt="image" src="https://github.com/user-attachments/assets/6d49a7b0-ca28-4754-87e5-9dafcd24f908" />

<img width="2560" height="1272" alt="image" src="https://github.com/user-attachments/assets/fe865b37-388e-415c-aee5-d18321e6d67c" />


***



🎉🎉 **Excellent! You have successfully captured VPC Flow Logs.** 🎉🎉

This is exactly what we wanted to see.

You have proved:

✅ Flow Logs are active
✅ CloudWatch is receiving records
✅ Network traffic is being recorded
✅ ACCEPT traffic is visible

Now let's become detectives and read one record.

---

You have this:

```text
2 138852020826 eni-0056a0228690dc480 
44.248.100.235 
10.10.11.10 
443 
44572 
6 
3 
180 
1784915449 
1784915457 
ACCEPT 
OK
```

Let's decode it.

---

# Flow Log Format

Your default format:

```text
version
account-id
interface-id
srcaddr
dstaddr
srcport
dstport
protocol
packets
bytes
start
end
action
log-status
```

---

## Your record:

### Interface

```text
eni-0056a0228690dc480
```

This is your private EC2 network interface.

Remember:

Your private EC2:

```text
cloudadhar-day6-private-ec2

IP:
10.10.11.10
```

---

### Source

```text
44.248.100.235
```

This is an AWS service endpoint/public AWS IP.

---

### Destination

```text
10.10.11.10
```

Your private EC2.

---

### Destination Port

```text
443
```

HTTPS traffic.

---

### Protocol

```text
6
```

Protocol number:

```text
6 = TCP
```

---

### Action

The most important part:

```text
ACCEPT
```

Meaning:

AWS network controls allowed this traffic.

---

# What traffic was this?

Your private EC2 was communicating over HTTPS.

The path was:

```text
Private EC2
10.10.11.10
      |
      |
      ▼
NAT Gateway / AWS Service
      |
      |
      ▼
HTTPS :443
```

And Flow Logs recorded:

```text
ACCEPT ✅
```

---

# Important Interview Point ⭐

Question:

**Does ACCEPT in Flow Logs mean the application worked?**

Answer:

❌ No.

It only means:

> Network controls allowed the connection.

It does NOT guarantee:

* Application is running
* Web server responded
* Database query succeeded

Example:

```text
Security Group ✅
NACL ✅
Route Table ✅

Flow Log:
ACCEPT

But:

Application crashed ❌
```

---

# Now let's create a REJECT example

We already know how.

Remember your NACL:

```text
Rule 90

HTTP

Your IP /32

DENY
```

<img width="2262" height="916" alt="image" src="https://github.com/user-attachments/assets/5f91aec6-a981-4356-9814-113a94e8ac73" />


We will temporarily add it again.

Then:

```text
Browser
   |
   |
   X
NACL

Flow Log:
REJECT ❌
```

---

## Do this:

Go to:

```text
VPC
 ↓
Network ACLs
 ↓
cloudadhar-day6-public-a-nacl
```

Add inbound rule:

| Rule Number | Type | Source            | Action |
| ----------- | ---- | ----------------- | ------ |
| 90          | HTTP | YOUR PUBLIC IP/32 | DENY   |

Example:

```text
35.94.190.113/32
```

(Use your current public IP if changed.)

---

Then open:

```text
http://35.94.190.113
```

It should fail.

Wait 1-2 minutes.

Then come back to CloudWatch.

We will search:

```text
REJECT
```

and see the blocked traffic.

---

<img width="2552" height="1050" alt="image" src="https://github.com/user-attachments/assets/ea152fe9-13fa-4dd5-89fb-7770a33dfe83" />
<img width="1937" height="871" alt="image" src="https://github.com/user-attachments/assets/3f926a9f-049e-42c1-80d6-589331a97fa9" />
<img width="2542" height="1102" alt="image" src="https://github.com/user-attachments/assets/97084b5c-f9b6-4f56-b011-e49547e8f7ee" />

🎉🎉 **Perfect! You have successfully completed the VPC Flow Logs ACCEPT + REJECT demo.** 🎉🎉

This is exactly the result we wanted.

You now have proof of both:

✅ Allowed traffic → `ACCEPT`
✅ Blocked traffic → `REJECT`

---

Let's decode your REJECT record.

Example:

```text
2 138852020826 eni-0ca56ded0f799d02e 
66.132.186.77 
10.10.1.190 
63698 
9142 
6 
1 
60 
1784915976 
1784915999 
REJECT 
OK
```

---

## Breaking it down

### Network Interface

```
eni-0ca56ded0f799d02e
```

This belongs to your:

```
cloudadhar-day6-web-ec2
```

with private IP:

```
10.10.1.190
```

---

### Source

```
66.132.186.77
```

External internet source trying to connect.

---

### Destination

```
10.10.1.190
```

Your web EC2.

---

### Protocol

```
6
```

Means:

```
TCP
```

---

### Action

The important part:

```
REJECT
```

Meaning:

AWS network layer blocked this traffic.

Most likely:

```
Internet
   |
   |
   v
Web EC2
10.10.1.190

NACL Rule 90
DENY

Result:
REJECT ❌
```

---

# 🎯 What you learned in Day 6

Your complete architecture now looks like:

```
                 Internet
                    |
                    |
             Public EC2
          10.10.1.190
                    |
              Security Group
                    |
              Network ACL
                    |
        ---------------------
        |                   |
     ACCEPT              REJECT
        |                   |
        v                   X

   Application works    Traffic blocked


             |
             v

        VPC Flow Logs

        CloudWatch Logs
```

---

# Very important AWS interview concepts ⭐⭐⭐

## 1. What does VPC Flow Logs capture?

Answer:

> VPC Flow Logs capture information about IP traffic going to and from network interfaces in a VPC.

---

## 2. Does Flow Log block traffic?

Answer:

> No. Flow Logs only monitor and record traffic. They do not allow or deny traffic.

Blocking is done by:

* Security Groups
* Network ACLs
* Route Tables
* Firewalls

---

## 3. What does REJECT mean?

Answer:

> REJECT means the traffic was denied by a network control such as a Network ACL or security mechanism.

---

## 4. Difference between ACCEPT and REJECT?

```
ACCEPT
------
Traffic passed network filtering.


REJECT
------
Traffic was blocked.
```

---

# Day 6 Topics Completed ✅

You covered:

✅ Private EC2 without public IP
✅ NAT Gateway internet access
✅ S3 Gateway Endpoint
✅ EC2 Interface Endpoint
✅ Private DNS resolution
✅ Security Groups
✅ Network ACL allow/deny
✅ VPC Flow Logs
✅ CloudWatch log analysis

This is a very strong AWS networking lab. 🚀

Next logical step:

**Day 6 Cleanup + Architecture Diagram + LinkedIn notes**

Before cleanup, take screenshots of:

1. VPC architecture
2. Endpoint list
3. Flow Log ACCEPT
4. Flow Log REJECT

Yes. Since you've completed **Day 6**, here's the safest cleanup order. This avoids dependency errors (for example, you can't delete a VPC while endpoints or ENIs still exist).

---

# Step 1: Terminate EC2 Instances

Go to:

**EC2 → Instances**

Terminate:

* ✅ `cloudadhar-day6-web-ec2`
* ✅ `cloudadhar-day6-private-ec2`

Wait until both show **Terminated**.

---

# Step 2: Delete VPC Endpoints

Go to:

**VPC → Endpoints**

Delete:

* ✅ `cloudadhar-day6-ec2-endpoint` (Interface)
* ✅ `cloudadhar-day6-s3-gateway-endpoint` (Gateway)

Wait until they disappear.

---

# Step 3: Delete Flow Logs

Go to:

**VPC → Your VPC → Flow logs**

Delete:

* ✅ `cloudadhar-day6-flow-logs`

---

# Step 4: Delete CloudWatch Log Group

Go to:

**CloudWatch → Logs → Log groups**

Delete:

* ✅ `/aws/vpc/flowlogs/cloudadhar-day6`

---

# Step 5: Delete NAT Gateway

Go to:

**VPC → NAT Gateways**

Delete:

* ✅ `cloudadhar-day6-nat-a`

Wait until its status becomes **Deleted** (this can take several minutes).

---

# Step 6: Release Elastic IP

Go to:

**EC2 → Elastic IPs**

Select the Elastic IP used by the NAT Gateway.

Choose:

**Actions → Release Elastic IP addresses**

Confirm.

---

# Step 7: Delete Network ACL

Go to:

**VPC → Network ACLs**

If your custom NACL is still associated with subnets:

1. Select the custom NACL.
2. Choose **Subnet associations**.
3. Replace it with the **default NACL**.
4. Save.

Then delete:

* ✅ `cloudadhar-day6-nacl`

---

# Step 8: Delete Security Groups

Go to:

**EC2 → Security Groups**

Delete (after the instances and endpoints are gone):

* ✅ `cloudadhar-day6-web-sg`
* ✅ `cloudadhar-day6-private-sg`
* ✅ `cloudadhar-day6-endpoint-sg`

Leave the **default** security group.

---

# Step 9: Delete Route Tables

Go to:

**VPC → Route Tables**

Delete custom route tables:

* ✅ `cloudadhar-public-rt`
* ✅ `cloudadhar-private-rt`

Don't delete the **main** route table yet.

---

# Step 10: Detach & Delete Internet Gateway

Go to:

**VPC → Internet Gateways**

Select:

* ✅ `cloudadhar-day5-igw`

Choose:

1. **Detach**
2. **Delete**

---

# Step 11: Delete Subnets

Go to:

**VPC → Subnets**

Delete:

* ✅ `cloudadhar-public-a`
* ✅ `cloudadhar-public-b`
* ✅ `cloudadhar-private-a`
* ✅ `cloudadhar-private-b`

---

# Step 12: Delete the VPC

Go to:

**VPC → Your VPCs**

Delete:

* ✅ `cloudadhar-day5-vpc`

---

## If the VPC won't delete

It's almost always because something is still attached. Check for:

* Interface endpoint ENIs
* NAT Gateway (still deleting)
* Elastic IP not released
* Security groups
* Route tables
* Flow logs
* Internet Gateway
* Network ACL associations


