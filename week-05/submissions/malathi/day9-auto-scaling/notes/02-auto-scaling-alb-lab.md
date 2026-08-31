# Day 9 — What are we building?

Imagine we own a website.

At first, only **one worker** is needed:

```text
             👨 User
                |
                v
          🚦 Load Balancer
                |
                v
             💻 EC2-1
```

Suddenly lots of people visit:

```text
       👨 👩 👨 👩 👨 👩
               |
               v
        🚦 Load Balancer
          /           \
         v             v
      💻 EC2-1      💻 EC2-2
```

When people leave:

```text
        🚦 Load Balancer
               |
               v
            💻 EC2-1
```

AWS does this automatically using:

```text
Launch Template
       ↓
Auto Scaling Group
       ↓
Target Group
       ↓
Application Load Balancer
       ↓
Users
```

---

# 🏗️ Our Day 9 Resources

We will create these **in this order**:

```text
1. Security Groups
       ↓
2. Launch Template
       ↓
3. Target Group
       ↓
4. Application Load Balancer
       ↓
5. Auto Scaling Group
       ↓
6. Target Tracking Policy
       ↓
7. Test Scale OUT
       ↓
8. Test Scale IN
       ↓
9. Test Self-Healing
```

Don't create everything together.

**We will do one step → check it → screenshot → move on.**

---

# STEP 0 — Check Region first 🌍

Sir says:

```text
Region = ap-south-1
```

That means:

> AWS Mumbai Region.

At the top-right of AWS Console, make sure you are in:

```text
Asia Pacific (Mumbai)
ap-south-1
```

### ⚠️ Important

Do **not** start creating resources until the Region is correct.

Your previous labs had work in another Region, so this is especially important.

---

# STEP 1 — Security Groups 🔐

We need **two Security Groups**.

Think of Security Groups as **guards**.

We have:

```text
Internet
   |
   v
🚦 ALB
   |
   v
💻 EC2
```

There should be **two guards**.

---

## 🛡️ Guard #1 — ALB Security Group

Name:

```text
cloudadhar-day9-alb-sg
```

This guard protects the ALB.

We want:

```text
Internet
   |
   | HTTP :80
   v
ALB
```

Therefore:

### Inbound

```text
Type:       HTTP
Port:       80
Source:     0.0.0.0/0
```

Meaning:

> Anyone on the internet can reach the Load Balancer on HTTP port 80.

That's okay because the **ALB is public**.

---

# 🛡️ Guard #2 — Web Security Group

Name:

```text
cloudadhar-day9-web-sg
```

This protects our EC2 instances.

But here's the important part.

❌ Don't do:

```text
Internet
   |
   | HTTP 80
   v
EC2
```

Instead:

```text
Internet
   |
   v
ALB
   |
   | HTTP 80
   v
EC2
```

Therefore EC2 should allow:

```text
HTTP
Port: 80
Source: cloudadhar-day9-alb-sg
```

### 🧠 Kid memory

```text
Internet → ALB ✅
ALB → EC2 ✅
Internet → EC2 ❌
```

That's a very important security design.

---

# STEP 2 — Launch Template 📋

Now we make the **EC2 recipe**.

Name:

```text
cloudadhar-day9-lt
```

Version name:

```text
v1-nginx-imdsv2
```

Think:

> "AWS, whenever you create an EC2 for me, use this recipe."

---

## 🍰 Launch Template recipe

Sir wants:

```text
AMI
Amazon Linux 2023 x86_64

Instance type
t3.micro

Security Group
cloudadhar-day9-web-sg

IAM
SSM-capable instance profile

Storage
8 GiB gp3
Encrypted

Monitoring
Detailed monitoring

Metadata
IMDSv2 required
Hop limit = 1
```

Let's understand each one.

---

### 💿 AMI

AMI is basically the **starting image** for EC2.

Like:

```text
🏠 Empty house blueprint
```

We use:

```text
Amazon Linux 2023
x86_64
```

---

### 💻 t3.micro

This is the EC2 size.

For our classroom lab:

```text
t3.micro
```

Small and cheap.

---

### 🔐 IAM Role

The EC2 needs permission to communicate with AWS services.

We're using an **SSM-capable instance profile** so we can preferably manage it using Session Manager.

Remember:

> IAM Role = what the EC2 is allowed to do.

---

### 💾 8 GiB gp3

Our root disk:

```text
8 GiB
gp3
Encrypted
```

Think:

```text
EC2
 |
 └── 💾 8 GiB disk
```

---

### 📊 Detailed Monitoring

Normal monitoring gives less frequent metric information.

Detailed monitoring gives **1-minute CPU data**, which helps our scaling evidence.

We need this because later we are going to say:

> "CPU became high → ASG should create another EC2."

---

# 🔐 IMDSv2

This is important from your previous Week 4 work too.

Sir says:

```text
Metadata tokens: Required
Hop limit: 1
```

So:

```text
IMDSv2 = Required
```

Why?

Because EC2 instance metadata should be accessed securely using a token.

Our User Data will do:

```text
Request token
     ↓
Get instance metadata
     ↓
Instance ID
Instance Type
AZ
Private IP
```

---

# STEP 3 — User Data 👶

This is one of the coolest parts.

When EC2 starts for the first time:

```text
EC2 starts
   ↓
User Data runs
   ↓
Install nginx
   ↓
Start nginx
   ↓
Get EC2 information
   ↓
Create web page
   ↓
Create health.html
```

The page will show things like:

```text
CloudAdhar Auto Scaling Lab

Instance ID: i-xxxxxxxx
Instance Type: t3.micro
Availability Zone: ap-south-1a
Private IP: 10.x.x.x
Hostname: ...
```

Why show the Instance ID?

Because later we want to prove:

```text
Request 1 → EC2-A
Request 2 → EC2-B
```

So the webpage tells us **which EC2 answered**.

---

# ❤️ health.html

We also create:

```text
/health.html
```

with:

```text
healthy
```

The Load Balancer asks:

```text
"Are you healthy?"
        |
        v
http://EC2/health.html
        |
        v
200 OK
```

Then ALB says:

```text
✅ Healthy
```

---

# STEP 4 — Target Group 🎯

Name:

```text
cloudadhar-day9-tg
```

Think of Target Group as a **list of EC2 workers**.

```text
Target Group
    |
    ├── 💻 EC2-1
    └── 💻 EC2-2
```

But initially we'll have only one.

---

## Health check

Sir wants:

```text
Protocol: HTTP
Port: 80

Path:
/health.html

Success:
200

Interval:
15 seconds

Healthy threshold:
2

Unhealthy threshold:
2
```

### What does this mean?

ALB repeatedly asks:

```text
Are you healthy?
Are you healthy?
```

If it gets enough successful answers:

```text
EC2 → Healthy ✅
```

If it repeatedly fails:

```text
EC2 → Unhealthy ❌
```

---

# STEP 5 — Application Load Balancer 🚦

Name:

```text
cloudadhar-day9-alb
```

It must be:

```text
Internet-facing
IPv4
```

And it uses **two AZs**.

Example:

```text
             ALB
          /       \
         /         \
     AZ-1a         AZ-1c
       |              |
    Subnet          Subnet
```

Why two?

Because we don't want our Load Balancer depending on only one AZ.

---

# STEP 6 — Auto Scaling Group 👨‍💼

Name:

```text
cloudadhar-day9-asg
```

ASG uses our:

```text
cloudadhar-day9-lt
```

And the same two subnets/AZs.

Our capacity:

```text
Minimum = 1
Desired = 1
Maximum = 2
```

Initially:

```text
ASG
 |
 └── 💻 EC2-1
```

---

# 🩺 Enable BOTH health checks

Sir specifically wants:

```text
EC2 health check ✅
ELB health check ✅
```

This is important.

Think:

```text
EC2 health
    ↓
"Is the machine okay?"

ELB health
    ↓
"Is the application okay?"
```

---

# ⏰ Grace Period

Set:

```text
300 seconds
```

This gives the new EC2 time to:

```text
Boot
 ↓
Run User Data
 ↓
Start nginx
 ↓
Become healthy
```

---

# 🔥 Default Warmup

Set:

```text
120 seconds
```

This helps AWS avoid making immediate scaling decisions based on a brand-new instance that hasn't stabilized yet.

---

# 🏷️ Tags

Every resource should have:

```text
Project = AWS-Zero-To-Hero
Day = 09
Environment = Training
Owner = CloudAdhar
DataClassification = Training-Only
```

And for EC2 Name:

```text
cloudadhar-day9-web-instance
```

### Very important

For ASG tags:

> Enable **propagate to instances**.

That means new EC2s created by the ASG get the tags too.

---

# STEP 7 — Target Tracking 🎯

Name:

```text
cloudadhar-day9-cpu50-policy
```

Metric:

```text
Average CPU utilization
```

Target:

```text
50%
```

Meaning:

> "AWS, try to keep the average CPU around 50%."

If CPU becomes very high:

```text
CPU 🔥
 |
 v
Scaling Policy
 |
 v
ASG
 |
 v
Create EC2
```

---

# STEP 8 — Our first test: Scale OUT 📈

Initially:

```text
ASG
 |
 └── EC2-1
```

We'll connect to EC2 using Session Manager.

Then install:

```bash
sudo dnf install -y stress-ng
```

And run:

```bash
nohup stress-ng --cpu 2 --cpu-load 95 --timeout 10m \
  > /tmp/stress-ng.log 2>&1 &
```

This basically tells the CPU:

> "Work very hard for a while!" 😄

CPU goes high:

```text
CPU
100% |       █████████
     |
 50% |────── target
     |
  0% |
```

Then AWS should eventually decide:

```text
"CPU is too high."
       ↓
Create another EC2
```

Result:

```text
1 → 2
```

---

# 📸 Your friend's screenshots make sense now

We can use his sequence as our evidence checklist:

```text
01 → Launch Template
02 → Target Group
03 → ALB
04 → ASG
05 → Healthy target
06 → ALB working
07 → Scaling policy
08 → High CPU alarm
09 → Scale-out activity
10 → Two healthy EC2s
11 → ALB serving multiple instances
12 → Low CPU
13 → Unhealthy target
14 → Replacement
15 → Replacement healthy
```

So we're **not copying his configuration blindly**.

We're saying:

> "Sir requires these outcomes. My friend's screenshots show one way to prove those outcomes."

---

# 📈 STEP 9 — Scale OUT proof

We need to capture:

### 1. High CPU

```text
EC2
 ↓
CPU high
```

### 2. CloudWatch alarm

```text
High CPU alarm
     ↓
   ALARM 🔴
```

### 3. ASG Activity

```text
Desired capacity:
1 → 2
```

### 4. Two EC2 instances

```text
ASG
 |
 ├── EC2-A ✅
 └── EC2-B ✅
```

### 5. Two healthy targets

```text
Target Group

EC2-A → Healthy ✅
EC2-B → Healthy ✅
```

---

# 🚦 STEP 10 — Prove ALB is actually balancing

Now we refresh the ALB URL several times.

Maybe:

```text
Refresh 1
Instance ID: i-AAA

Refresh 2
Instance ID: i-BBB

Refresh 3
Instance ID: i-AAA

Refresh 4
Instance ID: i-BBB
```

That proves:

> The ALB is sending traffic to multiple healthy EC2 instances.

This is much better evidence than simply saying "ALB exists."

---

# 📉 STEP 11 — Scale IN

Now we stop the CPU stress.

On every instance:

```bash
sudo pkill stress-ng || true
pgrep -af stress-ng
```

CPU comes down:

```text
🔥 95%
   ↓
🙂 20%
```

Eventually AWS decides:

> "We don't need two instances anymore."

Then:

```text
2 → 1
```

The removed target may show:

```text
Draining
```

### 🧒 What is Draining?

Imagine a bus is leaving.

You don't throw people out immediately.

You let current passengers finish.

Similarly, ALB gives existing connections time to finish before completely removing the instance.

That's **connection draining / deregistration delay**.

---

# ❤️ STEP 12 — Self-Healing

This is another VERY important test.

We can stop nginx on one EC2:

```bash
sudo systemctl stop nginx
```

The EC2 itself is still:

```text
RUNNING ✅
```

But the application is:

```text
nginx ❌
```

Then:

```text
ALB health check
       ↓
/health.html
       ↓
Failure ❌
       ↓
Target unhealthy
```

Because ELB health checks are enabled for the ASG, Auto Scaling can replace the unhealthy instance.

Eventually:

```text
Old EC2 ❌
    ↓
ASG replaces it
    ↓
New EC2 ✅
    ↓
User Data runs
    ↓
nginx starts
    ↓
/health.html → 200
    ↓
Healthy ✅
```

That's **self-healing**.

---

# 🧠 One very important thing

There are actually **two different situations**:

### Situation A — EC2 itself dies

```text
EC2 ❌
```

ASG can replace it.

### Situation B — EC2 is alive but nginx dies

```text
EC2 ✅
nginx ❌
```

ELB health check detects the application failure, and with ELB health checks enabled for the ASG, the instance can be replaced.

That's why sir specifically asks us to enable:

```text
EC2 health checks
+
ELB health checks
```

---

# 🎯 FINAL DAY 9 MAP

Keep this picture in your notes:

```text
                         👥 USERS
                            |
                            v
                    🌐 INTERNET
                            |
                            v
                  ┌─────────────────┐
                  │       ALB       │
                  │ cloudadhar-day9 │
                  └────────┬────────┘
                           |
                           v
                  ┌─────────────────┐
                  │  TARGET GROUP   │
                  │ cloudadhar-day9 │
                  └────────┬────────┘
                           |
                           v
                  ┌─────────────────┐
                  │       ASG       │
                  │ min 1           │
                  │ desired 1       │
                  │ max 2           │
                  └───────┬─────────┘
                          |
                 ┌────────┴────────┐
                 ↓                 ↓
              💻 EC2-1          💻 EC2-2
              AZ-1a              AZ-1c
```

And:

```text
Launch Template
       |
       | EC2 recipe
       v
      ASG
       |
       | creates/removes EC2
       v
 EC2 instances
```

And scaling:

```text
              CPU
               |
               v
       Target Tracking
          target 50%
               |
        ┌──────┴──────┐
        ↓             ↓
    CPU HIGH       CPU LOW
        ↓             ↓
   Scale OUT       Scale IN
        ↓             ↓
      1 → 2         2 → 1
```

And self-healing:

```text
EC2 running
    |
    v
nginx stops ❌
    |
    v
ALB health check fails
    |
    v
Target unhealthy
    |
    v
ASG replaces instance
    |
    v
New EC2
    |
    v
nginx starts
    |
    v
Healthy ✅
```

## 🚦 Where we start now

**Do NOT create the Launch Template yet.**

We'll start with **STEP 0 → Region + VPC + two subnets + Security Groups**.

### First action

Go to AWS Console → make sure the Region is:

**`ap-south-1 (Mumbai)`**

***


#  Now  current situation


> "nothing in VPC security subnet"

That's actually okay.

It means we need to build the **network foundation first**.

Think of AWS like building a house:

```text
🏠 Our AWS Application

First:
🏞️ Land = VPC

Then:
🛣️ Roads = Subnets

Then:
🚪 Gates/guards = Security Groups

Then:
💻 House = EC2

Then:
🚦 Traffic police = ALB
```

So we **should NOT create the Launch Template yet**.

---

# STEP 1 — Create the VPC

We'll create a small VPC for Week 5.

Go to:

**AWS Console → VPC → Your VPCs**

Make sure the top-right says:

```text
Oregon
us-west-2
```

Then click:

**Create VPC**

### Choose:

```text
Resources to create:
VPC only
```

### Name

Use:

```text
cloudadhar-day9-vpc
```

### IPv4 CIDR

Use:

```text
10.50.0.0/16
```

### IPv6

Don't add one.

### Tenancy

Keep:

```text
Default
```

So it should look approximately like:

```text
Name:
cloudadhar-day9-vpc

IPv4 CIDR:
10.50.0.0/16

IPv6:
No IPv6 CIDR block

Tenancy:
Default
```

Then:

**Create VPC**

---

## 🛑 STOP HERE

Don't create subnets yet.

After you create the VPC, send me the screenshot showing:

```text
cloudadhar-day9-vpc
10.50.0.0/16
Available
us-west-2
```

Then I'll take you through **STEP 2 — Internet Gateway + two subnets**, one click at a time.

And don't worry about the whole Day 9 yet. 😊

We're going to build it like Lego:

```text
🧱 VPC
  ↓
🧱 Internet Gateway
  ↓
🧱 Subnet 1
  ↓
🧱 Subnet 2
  ↓
🧱 Security Groups
  ↓
🧱 Launch Template
  ↓
🧱 Target Group
  ↓
🧱 ALB
  ↓
🧱 ASG
  ↓
🎯 Scaling test
```

**For now: only create `cloudadhar-day9-vpc`.**

[1]: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones-setup.html"Select a Region for your Amazon EC2 resources - Amazon Elastic Compute Cloud"
[2]: https://docs.aws.amazon.com/global-infrastructure/latest/regions/aws-availability-zones.html"AWS Availability Zones - AWS Regions and Availability Zones"

***


Doing the lab in **Oregon (`us-west-2`)**, keep that Region selected at the top.

## Fill this page like this

### 1. Resources to create

Select:

**✅ VPC only**

Do **not** select "VPC and more."

Why?

Because we'll create the networking pieces ourselves so you understand what each one does.

---

### 2. Name tag

Enter:

```text
cloudadhar-day9-vpc
```

---

### 3. IPv4 CIDR

Select:

**✅ IPv4 CIDR manual input**

Enter:

```text
10.50.0.0/16
```

Think of this as our **big neighborhood**:

```text
VPC
10.50.0.0/16
     |
     +--- Subnet 1
     |
     +--- Subnet 2
```

---

### 4. IPv6 CIDR block

Select:

**✅ No IPv6 CIDR block**

We don't need IPv6 for this classroom lab.

---

### 5. Tenancy

Keep:

**Default**

Don't change it.

---

### 6. VPC encryption control

Keep:

**None**

⚠️ Don't select Monitor or Enforce.

Those can introduce additional charges, and we don't need them for this lab.

---

### 7. Tags

Add the required lab tags.

Click **Add tag** and enter:

| Key                  | Value              |
| -------------------- | ------------------ |
| `Project`            | `AWS-Zero-To-Hero` |
| `Day`                | `09`               |
| `Environment`        | `Training`         |
| `Owner`              | `CloudAdhar`       |
| `DataClassification` | `Training-Only`    |

So you'll have:

```text
Name              = cloudadhar-day9-vpc
Project           = AWS-Zero-To-Hero
Day               = 09
Environment       = Training
Owner             = CloudAdhar
DataClassification= Training-Only
```

### Before clicking Create VPC, check:

```text
Region:          us-west-2
Resources:       VPC only
Name:            cloudadhar-day9-vpc
IPv4:            10.50.0.0/16
IPv6:            None
Tenancy:         Default
Encryption:      None
```

Then click:

**🟢 Create VPC**

***

**VPC is created correctly.**

Let's check it against our Day 9 requirements:

| Setting     | Your result             | ✅                          |
| ----------- | ----------------------- | -------------------------- |
| Region      | `us-west-2` Oregon      | ✅                          |
| VPC name    | `cloudadhar-day9-vpc`   | ✅                          |
| VPC ID      | `vpc-07e5b8224d971ebb1` | ✅                          |
| IPv4 CIDR   | `10.50.0.0/16`          | ✅                          |
| State       | Available               | ✅                          |
| Tenancy     | Default                 | ✅                          |
| IPv6        | None                    | ✅                          |
| Default VPC | No                      | ✅                          |
| Subnets     | 0                       | ✅ — we'll create them next |

One thing we need to fix **before launching EC2**:

> **DNS hostnames = Disabled**

For our ALB/EC2 setup, I want DNS hostnames enabled. AWS uses DNS names heavily for load balancers and related resources.

---

# 🧒 STEP 2 — Enable DNS Hostnames

You are currently on:

```text
cloudadhar-day9-vpc
```

You can see:

```text
DNS resolution     Enabled
DNS hostnames      Disabled
```

We want:

```text
DNS resolution     Enabled ✅
DNS hostnames      Enabled ✅
```

### Do this:

On the VPC details page:

**Actions → Edit VPC settings**

Find:

### DNS hostnames

Turn it **ON / Enable**.

Leave:

### DNS resolution

**Enabled**.

Then click:

**Save changes**

---

### 🧠 Why do we need this?

Think of DNS like AWS's **phone book** 📖.

Instead of remembering an IP address like:

```text
10.50.x.x
```

AWS can give resources DNS names such as:

```text
something.elb.amazonaws.com
```

Our ALB will have a DNS name that we use to open our website.

So:

```text
👤 Browser
   |
   | "Where is my website?"
   v
DNS
   |
   v
🚦 ALB
   |
   v
💻 EC2
```

---

## 🛑 Do only this now

Enable:

```text
DNS hostnames = Enabled
```

Keep:

```text
DNS resolution = Enabled
```

Then send me the updated VPC details.

After that we'll create:

# STEP 3 — Internet Gateway 🌐

We'll build:

```text
Internet
    |
    v
🌐 Internet Gateway
    |
    v
VPC
10.50.0.0/16
```

Then we'll create our **two subnets in two AZs**.

***

Perfect! ✅ **Step 2 is complete.**

Your VPC now has:

```text
cloudadhar-day9-vpc
        |
        ├── IPv4: 10.50.0.0/16 ✅
        ├── DNS resolution: Enabled ✅
        ├── DNS hostnames: Enabled ✅
        ├── IPv6: None ✅
        └── State: Available ✅
```

Also:

```text
Subnets: 0
```

That's correct because we haven't created them yet.

---

# 🧒 STEP 3 — Create Internet Gateway 🌐

Think of your VPC as a **house** 🏠.

Right now:

```text
        🏠 VPC
   10.50.0.0/16

   🚫 No internet door
```

An **Internet Gateway (IGW)** is the door that connects the VPC to the Internet.

We'll eventually have:

```text
                 🌍 Internet
                      |
                      |
               🌐 Internet Gateway
                      |
                      |
            🏠 cloudadhar-day9-vpc
```

### Important

Creating an Internet Gateway **does not automatically make everything public**.

We still need:

* a public subnet
* a route table
* a route to the Internet Gateway
* appropriate security groups

We'll do those separately.

---

# Create the Internet Gateway

Go to:

**AWS Console → VPC → Internet gateways**

Click:

**Create internet gateway**

### Name

Enter:

```text
cloudadhar-day9-igw
```

Then add these tags:

| Key                  | Value              |
| -------------------- | ------------------ |
| `Project`            | `AWS-Zero-To-Hero` |
| `Day`                | `09`               |
| `Environment`        | `Training`         |
| `Owner`              | `CloudAdhar`       |
| `DataClassification` | `Training-Only`    |

Then click:

**Create internet gateway**

---

# 🛑 Don't attach it yet?

Actually, after creation we **do need to attach it to our VPC**, but let's do it immediately after you show me the creation result.

You should see something similar to:

```text
Internet gateway
cloudadhar-day9-igw
State: Detached
```

That's okay initially.

### Send me the result after creating it.



**STEP 4 — Attach Internet Gateway to `cloudadhar-day9-vpc`**

***

Perfect! ✅ **Step 3 is complete.**

Your Internet Gateway is correctly attached:

```text
🌍 Internet
     |
     v
🌐 cloudadhar-day9-igw
     |
     v
🏠 cloudadhar-day9-vpc
10.50.0.0/16
```

Your settings look correct:

* IGW: `cloudadhar-day9-igw` ✅
* IGW ID: `igw-0632c7e008097fa59` ✅
* State: **Attached** ✅
* VPC: `cloudadhar-day9-vpc` ✅
* Required tags: ✅

---

# 🧒 STEP 4 — Create our first subnet

Now our VPC is like a big neighborhood:

```text
🏠 VPC
10.50.0.0/16
```

We need to divide that neighborhood into smaller areas called **subnets**.

For our ALB, we need **two subnets in two different Availability Zones**.

We'll make:

```text
VPC
10.50.0.0/16
   |
   ├── Subnet 1
   |
   └── Subnet 2
```

Let's create the first one.

---

## Go to

**VPC Console → Subnets**

Click:

**Create subnet**

---

## 🟢 Subnet 1

### VPC

Select:

```text
cloudadhar-day9-vpc
```

It should show:

```text
VPC ID:
vpc-07e5b8224d971ebb1
```

---

### Subnet name

Enter:

```text
cloudadhar-day9-public-1
```

---

### Availability Zone

Choose:

```text
us-west-2a
```

⚠️ If `us-west-2a` is not available in your dropdown, **don't randomly choose one yet**. Show me the AZ options.

---

### IPv4 subnet CIDR block

Enter:

```text
10.50.1.0/24
```

Think of this as:

```text
VPC
10.50.0.0/16
       |
       +--- 10.50.1.0/24
```

---

### Tags

Add:

| Key                  | Value              |
| -------------------- | ------------------ |
| `Project`            | `AWS-Zero-To-Hero` |
| `Day`                | `09`               |
| `Environment`        | `Training`         |
| `Owner`              | `CloudAdhar`       |
| `DataClassification` | `Training-Only`    |

The Name tag will be:

```text
cloudadhar-day9-public-1
```

---

# ⚠️ One important setting

You may see:

**Auto-assign public IPv4 address**

For the **ALB public subnets**, we want public addressing available.

If the Create Subnet page doesn't offer that setting, that's okay—we'll configure the subnet after creation.

---

# 🛑 STOP BEFORE CREATING

Go to **Create subnet** and select:

```text
VPC:
cloudadhar-day9-vpc

Name:
cloudadhar-day9-public-1

AZ:
us-west-2a

CIDR:
10.50.1.0/24
```

***

Perfect 👍 You are on the correct **Create subnet** page, and AWS has already selected the correct VPC and AZ for us.

We'll fill this one carefully.

# 🧒 Subnet 1

### 1. VPC

Already correct:

```text
cloudadhar-day9-vpc
vpc-07e5b8224d971ebb1
```

✅ Don't change it.

---

### 2. Subnet name

Enter:

```text
cloudadhar-day9-public-1
```

---

### 3. Availability Zone

You currently have:

```text
us-west-2a
```

Perfect. ✅

Keep it.

---

### 4. IPv4 VPC CIDR block

Already selected:

```text
10.50.0.0/16
```

✅ Keep it.

---

### 5. IPv4 subnet CIDR block

This is the important one.

Enter:

```text
10.50.1.0/24
```

You should then see approximately:

```text
256 IPs
```

✅ That's correct.

---

# 🏷️ Tags

You have several empty tag rows.

We need these **5 tags**:

| Key                  | Value              |
| -------------------- | ------------------ |
| `Project`            | `AWS-Zero-To-Hero` |
| `Day`                | `09`               |
| `Environment`        | `Training`         |
| `Owner`              | `CloudAdhar`       |
| `DataClassification` | `Training-Only`    |

The Name tag is already handled by:

```text
Subnet name:
cloudadhar-day9-public-1
```

So don't create another `Name` tag manually.

---

# 🔍 Before you click Create subnet

Your screen should effectively say:

```text
VPC
cloudadhar-day9-vpc

Subnet name
cloudadhar-day9-public-1

Availability Zone
us-west-2a

VPC CIDR
10.50.0.0/16

Subnet CIDR
10.50.1.0/24
```

Tags:

```text
Project              AWS-Zero-To-Hero
Day                  09
Environment          Training
Owner                CloudAdhar
DataClassification   Training-Only
```

### Then:

🟢 **Click "Create subnet"**

---

## After creation 🛑

Don't create the second subnet yet.

Send me the **creation success screen**, especially the:

```text
Subnet ID
Subnet name
Availability Zone
IPv4 CIDR
State
```

Then we'll create **Subnet 2 in a different AZ**.

Our final layout will be:

```text
                 cloudadhar-day9-vpc
                    10.50.0.0/16
                          |
             ┌────────────┴────────────┐
             |                         |
             v                         v
        us-west-2a                us-west-2b
             |                         |
        10.50.1.0/24               10.50.2.0/24
             |                         |
     public-subnet-1             public-subnet-2
```

This **two-AZ setup** is important because our ALB needs subnets in different Availability Zones.

***

Excellent! 🎉 **Subnet 1 is correct.**

You have:

```text
cloudadhar-day9-public-1
        |
        ├── AZ: us-west-2a ✅
        ├── CIDR: 10.50.1.0/24 ✅
        ├── State: Available ✅
        └── VPC: cloudadhar-day9-vpc ✅
```

And AWS shows **251 available IPv4 addresses**. That's normal because AWS reserves 5 IP addresses in every subnet.

---

# 🧒 STEP 5 — Create Subnet 2

Now we need a **second subnet in a different Availability Zone**.

Why?

Imagine our application has two houses:

```text
🏠 House 1              🏠 House 2
AZ us-west-2a           AZ us-west-2b
     |                       |
     └───────── ALB ─────────┘
```

If one Availability Zone has a problem, the other can still work.

Our second subnet will be:

```text
Name:
cloudadhar-day9-public-2

AZ:
us-west-2b

CIDR:
10.50.2.0/24
```

---

## Go to

**VPC → Subnets → Create subnet**

### VPC

Select:

```text
cloudadhar-day9-vpc
```

### Subnet name

```text
cloudadhar-day9-public-2
```

### Availability Zone

Select:

```text
us-west-2b
```

⚠️ **Important:** Your first subnet is in `us-west-2a`, so the second one **must not** be `us-west-2a`.

Choose:

```text
us-west-2b
```

### VPC CIDR

Keep:

```text
10.50.0.0/16
```

### Subnet CIDR

Enter:

```text
10.50.2.0/24
```

Notice:

```text
Subnet 1 → 10.50.1.0/24
Subnet 2 → 10.50.2.0/24
```

No overlap. ✅

---

## 🏷️ Add the same 5 tags

| Key                  | Value              |
| -------------------- | ------------------ |
| `Project`            | `AWS-Zero-To-Hero` |
| `Day`                | `09`               |
| `Environment`        | `Training`         |
| `Owner`              | `CloudAdhar`       |
| `DataClassification` | `Training-Only`    |

---

### Before creating, check:

```text
VPC
cloudadhar-day9-vpc

Subnet name
cloudadhar-day9-public-2

AZ
us-west-2b

CIDR
10.50.2.0/24
```

Then click **Create subnet**.

🛑 **Stop after creation and send me the result.**

Then we'll do the next important piece:

**STEP 6 — Create the route table and make both subnets actually public.** 🌐

***

Perfect! 🎉 **Both subnets are correct.**

You now have the basic two-AZ network:

```text
                 🌐 Internet
                     |
                     |
              Internet Gateway
                     |
                     v
        🏠 cloudadhar-day9-vpc
             10.50.0.0/16
                /       \
               /         \
              v           v
        us-west-2a     us-west-2b
             |              |
     public-1          public-2
   10.50.1.0/24      10.50.2.0/24
```

### ✅ Your subnet check

| Subnet                     | AZ           | CIDR           | Status      |
| -------------------------- | ------------ | -------------- | ----------- |
| `cloudadhar-day9-public-1` | `us-west-2a` | `10.50.1.0/24` | ✅ Available |
| `cloudadhar-day9-public-2` | `us-west-2b` | `10.50.2.0/24` | ✅ Available |

And importantly:

```text
Different AZs       ✅
No CIDR overlap     ✅
Same VPC             ✅
251 available IPs   ✅
```

---

# 🧒 STEP 6 — Make the subnets PUBLIC

Right now, **don't be fooled by their names**:

```text
cloudadhar-day9-public-1
cloudadhar-day9-public-2
```

They are **not actually public yet**.

Why?

Look at your screenshot:

```text
Route table:
rtb-0333eb8265523e997
```

That route table currently has only:

```text
10.50.0.0/16 → local
```

There is **no Internet Gateway route** yet.

Think:

```text
Subnet 🏠
   |
   | "I want to go to Internet"
   v
Route Table 🛣️
   |
   | ????
   v
Internet Gateway 🌐
```

We need to tell the route table:

```text
0.0.0.0/0  →  cloudadhar-day9-igw
```

That means:

> "For any IPv4 destination that isn't inside my VPC, send the traffic to the Internet Gateway."

---

# STEP 6A — Create a dedicated route table

I recommend **not modifying the current main route table**.

We'll create a separate route table specifically for Day 9 public subnets.

Go to:

**VPC → Route tables**

Click:

**Create route table**

### Name

```text
cloudadhar-day9-public-rt
```

### VPC

Select:

```text
cloudadhar-day9-vpc
```

Add the same tags:

| Key                  | Value              |
| -------------------- | ------------------ |
| `Project`            | `AWS-Zero-To-Hero` |
| `Day`                | `09`               |
| `Environment`        | `Training`         |
| `Owner`              | `CloudAdhar`       |
| `DataClassification` | `Training-Only`    |

Then:

**Create route table**

---

## 🛑 Stop there

Don't add routes or associations yet.

Send me the result showing:

```text
cloudadhar-day9-public-rt
```

Then we'll do the next tiny step:

**STEP 6B — Add `0.0.0.0/0 → cloudadhar-day9-igw`**

Then we'll associate **both subnets** with this route table.

After that, your network will truly be:

```text
🌍 Internet
     |
     v
🌐 IGW
     |
     v
🛣️ Public Route Table
   /           \
  v             v
Subnet 1      Subnet 2
AZ-a          AZ-b
```

You're doing this exactly the right way—**one small piece at a time.**


No 👍 **don't edit this route table.**

The one you are seeing:

```text
rtb-0333eb8265523e997
```

is the **main route table** that AWS automatically created with your VPC.

We'll leave it alone. This is safer and cleaner for your lab.

### 🧒 Think of it like this

AWS already gave your VPC a basic road:

```text
🏠 VPC
   |
   └── 🛣️ Main route table
          |
          └── 10.50.0.0/16 → local
```

We're going to build **our own road** for the Day 9 public subnets:

```text
🏠 VPC
   |
   ├── 🛣️ Main route table      ← DON'T TOUCH
   |
   └── 🛣️ cloudadhar-day9-public-rt  ← CREATE THIS
```

## What to do now

On the **Route tables** page, click:

**🟢 Create route table**

Fill:

**Name:**

```text
cloudadhar-day9-public-rt
```

**VPC:**

```text
cloudadhar-day9-vpc
```

Add these tags:

```text
Project = AWS-Zero-To-Hero
Day = 09
Environment = Training
Owner = CloudAdhar
DataClassification = Training-Only
```

Then click **Create route table**.

🛑 **Don't edit `rtb-0333eb8265523e997`.**

After you create the new one, send me the screen. Then I'll show you exactly where to add:

```text
0.0.0.0/0 → cloudadhar-day9-igw
```

That's our next step.


***

Excellent! 🎉 **The dedicated public route table is created correctly.**

You now have:

```text
🛣️ cloudadhar-day9-public-rt
ID: rtb-09a517d6cf851dd80
VPC: cloudadhar-day9-vpc
Main: No ✅
```

It currently has only:

```text
10.50.0.0/16 → local
```

That's normal.

# 🧒 STEP 6B — Add the Internet route

Now we're going to add the **Internet door** to this route table.

We want:

```text
0.0.0.0/0  →  cloudadhar-day9-igw
```

### What does `0.0.0.0/0` mean?

It means:

> **"Any IPv4 address outside my VPC."**

So:

```text
💻 EC2
   |
   v
🛣️ Route table
   |
   | 0.0.0.0/0
   v
🌐 Internet Gateway
   |
   v
🌍 Internet
```

---

## Do this now

You are already on:

**`cloudadhar-day9-public-rt`**

Under **Routes**, click:

### **Edit routes**

Then click:

### **Add route**

Enter:

**Destination:**

```text
0.0.0.0/0
```

For **Target**, choose:

**Internet Gateway**

Then select:

```text
cloudadhar-day9-igw
igw-0632c7e008097fa59
```

It should look like:

| Destination    | Target                |
| -------------- | --------------------- |
| `10.50.0.0/16` | `local`               |
| `0.0.0.0/0`    | `cloudadhar-day9-igw` |

Then click:

**Save changes**

---

### 🛑 Don't associate the subnets yet.

After saving, send me the **Routes** section.

I'll check that the route is:

```text
0.0.0.0/0 → igw-0632c7e008097fa59 → Active
```

Then we'll do **STEP 6C — associate both public subnets with this route table.**

***

Perfect! ✅ **The Internet route is correct.**

You now have:

```text
🛣️ cloudadhar-day9-public-rt
        |
        ├── 10.50.0.0/16 → local       ✅
        |
        └── 0.0.0.0/0 → Internet Gateway ✅
```

And the route status is **Active**. 🎉

# 🧒 STEP 6C — Connect both subnets to this route table

Right now, your route table says:

> "I know how to reach the Internet."

But our two subnets aren't using this route table yet.

We need to connect them:

```text
cloudadhar-day9-public-rt
          |
          ├── cloudadhar-day9-public-1
          |
          └── cloudadhar-day9-public-2
```

## Do this

You are already on the route table page.

Click:

### **Subnet associations**

Then click:

### **Edit subnet associations**

You should see your two subnets.

Select **both**:

☑ `cloudadhar-day9-public-1`
☑ `cloudadhar-day9-public-2`

Then click:

### **Save associations**

---

## After saving, we want to see

```text
Explicit subnet associations: 2
```

And:

```text
cloudadhar-day9-public-1
cloudadhar-day9-public-2
```

associated with:

```text
cloudadhar-day9-public-rt
```

### 🧠 Our network will then be:

```text
                     🌍 Internet
                          |
                          v
                  🌐 Internet Gateway
                          |
                          v
               🛣️ Public Route Table
                0.0.0.0/0 → IGW
                    /          \
                   /            \
                  v              v
             Public-1        Public-2
             us-west-2a      us-west-2b
             10.50.1.0/24    10.50.2.0/24
```

🛑 **Do only the subnet associations now.**

Send me the result after saving, and I'll verify both subnets are attached correctly.

***


