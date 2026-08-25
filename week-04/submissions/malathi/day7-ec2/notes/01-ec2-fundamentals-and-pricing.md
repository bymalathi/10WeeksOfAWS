## What are we actually learning?

This Day 7 lab is teaching you **how to build a reusable EC2 server image**.

Instead of doing this every time:

```text
Launch EC2
   ↓
Install nginx
   ↓
Configure nginx
   ↓
Patch server
   ↓
Test server
   ↓
Repeat for another EC2
```

we want:

```text
Build one properly configured server
              ↓
          Create AMI
              ↓
     Reuse that AMI repeatedly
              ↓
       New EC2 already has nginx
```

That reusable AMI is your **Golden AMI**.

---

# PART 1 — EC2 FUNDAMENTALS

## Step 1: What is EC2?

Think of EC2 as:

> **A virtual computer rented from AWS.**

Your laptop has:

```text
CPU
RAM
Disk
Operating System
Network
```

An EC2 instance also has:

```text
vCPU
RAM
EBS storage
Operating System
Network
```

For example:

```text
EC2
 ├── 2 vCPU
 ├── 1 GB RAM
 ├── Amazon Linux
 ├── EBS disk
 └── Network connection
```

You choose the size depending on what your application needs.

---

# PART 2 — EC2 INSTANCE TYPES

This is very important for interviews.

AWS gives different **instance families**.

Think:

> "What does my application need most?"

---

## 2.1 General Purpose

Examples:

```text
T
M
```

Use when CPU and memory requirements are fairly balanced.

Example:

```text
Small web server
Application server
Development server
```

Think:

> **Normal workload → General Purpose**

---

## 2.2 Compute Optimized

Examples:

```text
C
```

Use when CPU is the main requirement.

Example:

```text
Video encoding
Batch processing
Heavy computation
```

Think:

> **CPU hungry → C**

---

## 2.3 Memory Optimized

Examples:

```text
R
X
```

Use when your application needs lots of RAM.

Example:

```text
In-memory database
Large cache
Memory-intensive application
```

Think:

> **RAM hungry → R/X**

---

## 2.4 Storage Optimized

Examples:

```text
I
D
```

Use when high local storage or high I/O is important.

Example:

```text
Search workloads
Large data processing
High I/O workloads
```

Think:

> **Storage/I/O hungry → I/D**

---

## 2.5 Accelerated Computing

Examples:

```text
P
G
Inf
Trn
```

Used for specialized workloads.

Example:

```text
Machine learning
GPU workloads
AI inference
Graphics
```

Think:

> **GPU/accelerator → Accelerated**

---

# PART 3 — T INSTANCES

This one is commonly tested.

T instances are **burstable**.

Imagine your CPU usage normally looks like:

```text
20% 20% 20% 25% 20%
```

but occasionally:

```text
20% → 90% → 95% → 20%
```

That's a good candidate for a burstable instance.

But suppose your workload continuously needs:

```text
90%
90%
95%
92%
94%
```

That's **not** what you should choose T for.

Your notes correctly say:

> Burstable T instances are for low-baseline workloads with occasional CPU bursts, not continuous heavy CPU.

### Interview question

**Q: When would you use a T instance?**

Answer:

> If the workload normally has low CPU usage but occasionally needs CPU bursts, I would consider a T-series burstable instance.

---

# PART 4 — WHAT SHOULD I CHECK BEFORE CHOOSING EC2?

Don't simply say:

> "I'll use t2.micro."

That's beginner thinking.

First ask:

```text
What workload?
       ↓
How much CPU?
       ↓
How much memory?
       ↓
What architecture?
       ↓
Network requirements?
       ↓
EBS requirements?
       ↓
Local storage?
       ↓
GPU?
       ↓
OS/software compatibility?
```

Then select the instance.

The correct thinking is:

> **Requirement → Instance family → Specific instance size**

---

# PART 5 — WHAT IS AN AMI?

Now we reach the most important part of your lab.

AMI = **Amazon Machine Image**

Think of an AMI as a **template for an EC2 machine**.

Imagine you have:

```text
EC2 Server
│
├── Amazon Linux
├── nginx
├── nginx configuration
├── application files
└── required settings
```

You are happy with this server.

You want another identical server.

Instead of installing everything again, you create:

```text
EC2 Server
     ↓
    AMI
     ↓
New EC2
```

The new EC2 starts from that image.

---

# PART 6 — GOLDEN AMI

Now what's a **Golden AMI**?

Not every AMI is automatically a Golden AMI.

A Golden AMI is an:

> **Approved, versioned, tested, patched baseline image.**

Think of a company.

They don't want every developer creating random server images.

Instead:

```text
Build
 ↓
Patch
 ↓
Configure
 ↓
Security check
 ↓
Test
 ↓
Approve
 ↓
Golden AMI
```

Then teams can launch servers from that approved image.

---

# PART 7 — WHY GOLDEN AMI?

Without Golden AMI:

```text
Server 1
Ubuntu + nginx + patch A

Server 2
Ubuntu + nginx + patch B

Server 3
Ubuntu + nginx + patch A

Server 4
Ubuntu + nginx + forgotten patch
```

Now you have **configuration drift**.

With Golden AMI:

```text
Golden AMI v1
       ↓
 ┌─────┼─────┐
 ↓     ↓     ↓
EC2   EC2   EC2
```

All start from the same approved baseline.

---

# PART 8 — AMI TYPES

Your notes give four types.

### AWS AMI

Owned/provided by AWS.

Used for:

> Supported operating-system baseline.

---

### Marketplace AMI

Provided by vendors through AWS Marketplace.

Example:

> A vendor provides a packaged security appliance.

---

### Custom AMI

You create it yourself.

Example:

```text
Amazon Linux
+
nginx
+
your configuration
=
Custom AMI
```

---

### Golden AMI

This is the important distinction.

A Golden AMI is:

```text
Approved
+
Versioned
+
Patched
+
Tested
+
Governed
```

So:

> **Golden AMI is more about the organization's approved image process than simply "an AMI I created."**

---

# PART 9 — IMMUTABLE VS MUTABLE PATCHING

This is another important DevOps concept.

## Mutable approach

You have:

```text
Running EC2
     ↓
Patch it
     ↓
Change it
     ↓
Restart it
```

The server itself changes.

Problem:

> Different servers can eventually become different.

That's configuration drift.

---

## Immutable approach

Instead:

```text
Old AMI
   ↓
Create new AMI
   ↓
Patch
   ↓
Test
   ↓
Golden AMI v2
   ↓
Launch new EC2
```

Old server isn't modified.

You replace it.

Think:

> **Don't repair the old server. Build a new known-good server.**

This is a very important DevOps idea.

---

# PART 10 — USER DATA

Now let's understand User Data.

When launching EC2, you can give it a script.

For example:

```bash
#!/bin/bash
dnf install -y nginx
systemctl enable --now nginx
```

EC2 boots.

Then User Data runs.

Conceptually:

```text
EC2 starts
   ↓
cloud-init
   ↓
User Data
   ↓
Install/configure software
```

Your lab uses:

```bash
dnf install -y nginx
systemctl enable --now nginx
```

So nginx gets installed automatically.

---

# PART 11 — WHY USER DATA IS NOT THE GOLDEN AMI

This is VERY important.

Suppose:

```text
AMI
 +
User Data
 =
EC2
```

User Data is useful for **first-boot setup**.

But your Golden AMI should already contain the important baseline.

Your lab eventually proves this.

It launches:

```text
Test EC2
   ↓
Golden AMI v2
   ↓
NO USER DATA
```

Then:

```bash
sudo systemctl is-enabled nginx
sudo systemctl is-active nginx
curl -I http://localhost
```

If nginx works:

> nginx came from the AMI.

That's the whole point of the exercise.

---

# PART 12 — LAUNCH TEMPLATE

A Launch Template is different from an AMI.

Don't confuse them.

### AMI

Answers:

> **What is inside my machine?**

For example:

```text
Amazon Linux
nginx
configuration
```

### Launch Template

Answers:

> **How should I launch the machine?**

It can contain:

```text
AMI
Instance type
IAM role
Security groups
Storage
Metadata settings
Tags
User Data
```

So remember:

```text
AMI
=
Machine image/template

Launch Template
=
Launch instructions
```

---

# PART 13 — IMDSv2

Now let's understand the scary-looking metadata commands.

EC2 has something called:

**Instance Metadata Service**

It is available from inside the EC2 instance at:

```text
169.254.169.254
```

It can provide information about the instance.

But there's a security concern with the older metadata access method.

So AWS supports:

> **IMDSv2**

IMDSv2 requires a token.

Think:

```text
Old way:

EC2 → metadata
```

versus:

```text
IMDSv2:

EC2
 ↓
Request token
 ↓
Receive token
 ↓
Present token
 ↓
Metadata
```

Your lab requires:

> **V2 only (token required)**

---

# PART 14 — YOUR FIRST IMDS TEST

Your lab performs:

```bash
curl -sS -o /dev/null \
  -w 'IMDSv1 HTTP status: %{http_code}\n' \
  --max-time 3 \
  http://169.254.169.254/latest/meta-data/instance-id
```

Because IMDSv2 is required, the old tokenless request should fail.

Expected:

```text
IMDSv1 HTTP status: 401
```

This is **good**.

It means:

```text
Tokenless request
      ↓
     401
      ↓
Denied
```

Don't think:

> "401 means my EC2 is broken."

Here it is evidence that tokenless metadata access is denied.

---

# PART 15 — TOKEN-BASED REQUEST

Then the lab does:

```bash
TOKEN=$(curl -sS -X PUT \
  -H 'X-aws-ec2-metadata-token-ttl-seconds: 21600' \
  http://169.254.169.254/latest/api/token)
```

This asks:

> "Give me an IMDSv2 token."

Then:

```bash
curl -sS -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/instance-id
```

Now the request includes the token.

So:

```text
Without token
     ↓
401

With token
     ↓
Metadata works
```

That's exactly what you're proving.

---

# PART 16 — IAM ROLE

Your lab creates:

```text
cloudadhar-role-ec2-ssm
```

with:

```text
AmazonSSMManagedInstanceCore
```

Why?

Because you're going to connect to EC2 using:

> **AWS Systems Manager Session Manager**

instead of SSH.

Think:

```text
Your computer
      ↓
AWS Systems Manager
      ↓
EC2
```

No public SSH is needed.

That's why your security group doesn't need:

```text
Port 22 from 0.0.0.0/0
```

In fact, your lab specifically says:

> **Do not add public SSH.**

Good security practice.

---

# PART 17 — SECURITY GROUP

Your security group:

```text
cloudadhar-sg-nginx-public
```

is for the nginx server.

The browser needs to reach nginx:

```text
Browser
   ↓
HTTP :80
   ↓
EC2
   ↓
nginx
```

Your lab says preferably allow HTTP from your public `/32`.

That means:

```text
YOUR_PUBLIC_IP/32
```

instead of:

```text
0.0.0.0/0
```

Why?

Because `/32` means **one IP address**.

---

# PART 18 — NOW YOUR MANUAL GOLDEN AMI LAB

Now we can finally understand the actual exercise.

The flow is:

```text
IAM Role
   ↓
Security Group
   ↓
Builder EC2
   ↓
User Data installs nginx
   ↓
Validate nginx
   ↓
Validate IMDSv2
   ↓
Patch server
   ↓
Create AMI
   ↓
Golden AMI v2
   ↓
Launch test EC2
   ↓
NO USER DATA
   ↓
nginx works
```

That's the entire lab.

---

# PART 19 — STEP 1: CREATE IAM ROLE

Create:

```text
cloudadhar-role-ec2-ssm
```

Attach:

```text
AmazonSSMManagedInstanceCore
```

Purpose:

```text
EC2
 ↓
Systems Manager
 ↓
Session Manager
```

Don't attach AdministratorAccess.

---

# PART 20 — STEP 2: CREATE SECURITY GROUP

Create:

```text
cloudadhar-sg-nginx-public
```

Need:

```text
HTTP :80
```

Prefer:

```text
YOUR PUBLIC IP /32
```

Don't create public SSH.

---

# PART 21 — STEP 3: LAUNCH BUILDER EC2

Name:

```text
cloudadhar-ec2-ami-builder-01
```

Use:

```text
Amazon Linux 2023
```

Attach:

```text
IAM role
cloudadhar-role-ec2-ssm
```

and:

```text
Security group
cloudadhar-sg-nginx-public
```

Metadata:

```text
IMDSv2 required
```

---

# PART 22 — STEP 4: USER DATA

Paste the exact User Data from your lab:

```bash
#!/bin/bash
set -euxo pipefail
dnf install -y nginx
systemctl enable --now nginx
cat > /usr/share/nginx/html/index.html <<'HTML'
<h1>CloudAdhar Week 4 Golden AMI</h1>
<p>nginx was installed by EC2 User Data.</p>
HTML
```

What happens?

```text
EC2 boots
   ↓
cloud-init
   ↓
User Data
   ↓
dnf installs nginx
   ↓
nginx starts
   ↓
index.html created
```

---

# PART 23 — STEP 5: CONNECT USING SESSION MANAGER

After the EC2 becomes ready:

Go to:

```text
EC2
 ↓
Instances
 ↓
Your instance
 ↓
Connect
 ↓
Session Manager
 ↓
Connect
```

You should get a terminal.

Now you're inside your EC2.

---

# PART 24 — STEP 6: VALIDATE BOOTSTRAP

Run:

```bash
sudo cloud-init status --wait
```

This waits for cloud-init to finish.

Then:

```bash
sudo systemctl status nginx --no-pager
```

You want nginx to be active.

Then:

```bash
curl -I http://localhost
```

You want an HTTP response.

Then:

```bash
sudo tail -n 40 /var/log/cloud-init-output.log
```

This lets you see User Data output.

---

# PART 25 — STEP 7: VALIDATE IMDSv2

First run the tokenless request.

Expected:

```text
401
```

Then obtain token.

Then make the token-authenticated requests.

You should see things such as:

```text
instance-id
availability zone
```

The important lesson:

```text
Tokenless → 401
Token → works
```

Do **not** query role credentials.

---

# PART 26 — STEP 8: PATCH THE SERVER

Now:

```bash
cat /etc/os-release
```

This tells you what OS you're running.

Then:

```bash
sudo dnf check-update || test $? -eq 100
```

The `|| test $? -eq 100` part is important because `dnf check-update` can return exit code 100 when updates are available.

Then:

```bash
sudo dnf upgrade -y
```

Apply updates.

Then:

```bash
sudo systemctl restart nginx
```

Make sure nginx still works:

```bash
curl -I http://localhost
```

---

# PART 27 — STEP 9: CREATE GOLDEN AMI

Now your builder EC2 contains:

```text
Amazon Linux 2023
+
Updates
+
nginx
+
nginx configuration
```

You create:

```text
cloudadhar-ami-nginx-golden-v2-20260725
```

This becomes your reusable image.

Wait until:

```text
Available
```

---

# PART 28 — STEP 10: THE MOST IMPORTANT TEST

Now launch:

```text
cloudadhar-ec2-ami-test-v2-01
```

from your Golden AMI.

And:

> **NO USER DATA**

This is deliberate.

Why?

Because we want to answer:

> "Does nginx already exist inside my AMI?"

Run:

```bash
sudo systemctl is-enabled nginx
```

Expected:

```text
enabled
```

Then:

```bash
sudo systemctl is-active nginx
```

Expected:

```text
active
```

Then:

```bash
curl -I http://localhost
```

Expected:

```text
HTTP response
```

Therefore:

```text
Golden AMI
    ↓
New EC2
    ↓
nginx already exists
    ↓
No User Data required
```

🎯 **This is the key proof of your Golden AMI.**

---

# PART 29 — NOW THE AUTOMATION PART

Everything above was:

> **Manual Golden AMI creation**

AWS gives you a service to automate this.

That service is:

## EC2 Image Builder

Think:

```text
Manual process:

Launch EC2
 ↓
Install software
 ↓
Patch
 ↓
Test
 ↓
Create AMI
```

Image Builder automates this:

```text
Recipe
  ↓
Temporary build EC2
  ↓
Build components
  ↓
Patch
  ↓
Create AMI
  ↓
Test component
  ↓
Golden AMI
```

---

# PART 30 — IMAGE BUILDER COMPONENTS

You have two components.

### Build component

```text
cloudadhar-component-nginx-build
```

Its job:

```text
Install nginx
Configure nginx
Validate nginx
```

### Test component

```text
cloudadhar-component-nginx-test
```

Its job:

```text
Take resulting AMI
       ↓
Launch test instance
       ↓
Check nginx
       ↓
Pass/fail
```

Very important:

> **Build component builds the image. Test component tests the image.**

---

# PART 31 — IMAGE RECIPE

Your recipe:

```text
cloudadhar-recipe-nginx-golden
```

Think of the recipe as:

> **The instructions describing how the image should be built.**

It specifies things like:

```text
Base OS
+
Build components
+
Test components
+
Storage
```

Your recipe uses:

```text
Amazon Linux 2023
       ↓
update-linux
       ↓
nginx build component
       ↓
AMI
       ↓
nginx test component
```

---

# PART 32 — INFRASTRUCTURE CONFIGURATION

This tells Image Builder:

> "Where and how should you build this image?"

It contains things like:

```text
VPC
Subnet
Security Group
Instance profile
Instance type
IMDSv2 requirement
```

Image Builder then creates **temporary EC2 instances**.

You don't manually maintain those build instances.

---

# PART 33 — DISTRIBUTION CONFIGURATION

This answers:

> "Where should the finished AMI go, and who can use it?"

Your lab says:

```text
Region:
ap-south-1
```

and:

```text
Private
```

So the resulting AMI isn't being made publicly launchable.

---

# PART 34 — PIPELINE

Finally:

```text
cloudadhar-pipeline-nginx-golden
```

connects everything:

```text
Recipe
  +
Infrastructure configuration
  +
Distribution configuration
        ↓
     Pipeline
        ↓
     Build AMI
        ↓
     Test AMI
        ↓
   Output Golden AMI
```

---

# PART 35 — THE ENTIRE THING IN ONE PICTURE

Memorize this:

```text
                    EC2 GOLDEN AMI

                    Amazon Linux
                         │
                         ▼
                  Builder EC2
                         │
                    User Data
                         │
                         ▼
                    Install nginx
                         │
                         ▼
                    Patch / Test
                         │
                         ▼
                      AMI v2
                         │
                         ▼
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
        New EC2 #1             New EC2 #2
              │                     │
              └──────────┬──────────┘
                         │
                         ▼
                  Same baseline
```

Then automation:

```text
             EC2 IMAGE BUILDER

              Image Recipe
                   │
                   ▼
          Infrastructure Config
                   │
                   ▼
             Build Component
                   │
                   ▼
              Build EC2
                   │
                   ▼
                AMI
                   │
                   ▼
              Test Component
                   │
                   ▼
             Tested AMI
                   │
                   ▼
            Golden AMI
```

---

# PART 36 — PRICING: DON'T MEMORIZE RANDOMLY

Think about **how predictable your workload is**.

### Unknown / short-term

```text
On-Demand
```

Think:

> "I don't know how long I'll need this."

---

### Steady compute usage

```text
Savings Plans
```

Think:

> "I consistently spend money on compute."

Savings Plans are **billing discounts**, not EC2 servers.

---

### Steady matching EC2 usage

```text
Reserved Instances
```

Think:

> "I have predictable EC2 usage."

Again:

> It's a pricing commitment/discount, not a server.

---

### Interruptible workload

```text
Spot
```

Think:

> "My workload can tolerate interruption."

Examples:

```text
Batch processing
Flexible jobs
Fault-tolerant workloads
```

Spot can be interrupted.

Therefore your application needs:

```text
Checkpointing
Retries
Graceful termination
```

---

### Server-bound licensing

```text
Dedicated Host
```

Think:

> "I need the actual physical host visibility because of licensing or host-level requirements."

---

### Single-tenant instance requirement

```text
Dedicated Instance
```

Think:

> "I need dedicated hardware tenancy, but I don't necessarily need host-level visibility/control."

---

# PART 37 — EXAM QUESTIONS

Let's make sure you understand before we move to the actual AWS Console.

### Question 1

Your company wants an approved, patched, tested server baseline that can be reused.

What do you choose?

**Answer: Golden AMI**

Reason:

```text
Approved + versioned + tested baseline
→ Golden AMI
```

---

### Question 2

Your company wants to automatically build and test AMIs.

Answer:

**EC2 Image Builder**

---

### Question 3

You need to run a small script when EC2 starts for the first time.

Answer:

**User Data**

---

### Question 4

You want versioned EC2 launch configuration.

Answer:

**Launch Template**

---

### Question 5

You want token-required EC2 metadata.

Answer:

**IMDSv2**

---

### Question 6

Demand is unknown and you don't want a commitment.

Answer:

**On-Demand**

---

### Question 7

Workload is interruptible and can retry.

Answer:

**Spot**

---

### Question 8

You have predictable compute spending and want flexibility across compute usage.

Answer:

**Savings Plans**

---

### Question 9

Your workload needs continuous heavy CPU.

Would you choose T?

**No.**

Think:

```text
Occasional CPU burst → T
Continuous CPU → Compute Optimized C
```

---

# PART 38 — THE MOST IMPORTANT INTERVIEW PATTERN

Whenever you get an AWS scenario question, don't immediately name a service.

Use:

```text
Requirement
     ↓
Choice
     ↓
Reason
```

Example:

> **Requirement:** The workload has low baseline CPU usage with occasional spikes.
> **Choice:** T-series burstable instance.
> **Reason:** T instances are designed for workloads that need occasional CPU bursts rather than sustained high CPU.

That's exactly the thinking AWS exam questions want.

---

## 🧠 Your Day 7 mental map

If you remember only this, remember:

```text
EC2
│
├── Instance Type
│      └── What resources does workload need?
│
├── AMI
│      └── What should the machine contain?
│
├── Golden AMI
│      └── Approved reusable baseline
│
├── User Data
│      └── First-boot setup
│
├── Launch Template
│      └── How to launch EC2
│
├── IMDSv2
│      └── Secure metadata access using token
│
├── Pricing
│      ├── On-Demand
│      ├── Reserved Instances
│      ├── Savings Plans
│      ├── Spot
│      ├── Dedicated Instance
│      └── Dedicated Host
│
└── EC2 Image Builder
       └── Automate Golden AMI creation
```