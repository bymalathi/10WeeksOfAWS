The lab is really teaching  **one simple story**:

> **Build one properly configured EC2 → install nginx → secure it → turn it into an AMI → launch another EC2 from that AMI → prove nginx is already there. → Then automate the same process using EC2 Image Builder.**

---

# 🧒 First: Understand the big picture

Imagine you are making a **ready-made computer template**.

### Step 1 — Build a computer

```text
Amazon Linux 2023
       ↓
Builder EC2
       ↓
Install nginx
       ↓
Configure nginx
       ↓
Secure EC2 with IMDSv2
```

Your builder is:

```text
cloudadhar-ec2-ami-builder-01
```

---

### Step 2 — Take a picture of that computer

That picture is called an:

```text
AMI
```

Think:

> AMI = photograph/template of an EC2 machine.

So:

```text
Builder EC2
     ↓
Create AMI
     ↓
cloudadhar-ami-nginx-golden-v2-20260725
```

---

### Step 3 — Use the picture to create another computer

```text
Golden AMI
     ↓
New EC2
     ↓
cloudadhar-ec2-ami-test-v2-01
```

And the important test is:

> **We do NOT provide User Data to the new EC2.**

Yet nginx should already work.

That proves nginx came from the AMI.

---

# 🧠 Before touching AWS, understand the 6 important things

## 1. EC2

EC2 is simply:

> **A virtual computer in AWS.**

Your computer:

```text
Laptop
```

AWS computer:

```text
EC2
```

---

## 2. Security Group

Security Group is like the **security guard at the door**.

For this lab:

```text
Internet
   |
   | HTTP : 80
   ↓
Security Group
   |
   ↓
EC2
```

We allow:

```text
HTTP → your public IP /32
```

We **do NOT allow public SSH**.

Why?

Because we're going to use:

> **AWS Systems Manager Session Manager**

instead of SSH.

---

# 3. IAM Role

IAM Role answers:

> "What is this EC2 allowed to do?"

You create:

```text
cloudadhar-role-ec2-ssm
```

and attach:

```text
AmazonSSMManagedInstanceCore
```

This lets Systems Manager communicate with the EC2.

Think:

```text
EC2
 |
 | "AWS, please let me use Session Manager"
 ↓
IAM Role
 |
 ↓
AmazonSSMManagedInstanceCore
```

---

# 4. User Data

User Data is a script that EC2 runs during its initial startup.

Your script says:

```bash
dnf install -y nginx
```

Meaning:

> Install nginx.

Then:

```bash
systemctl enable --now nginx
```

Meaning:

> Start nginx now and make sure it starts automatically after reboot.

Then you're creating your webpage.

So:

```text
EC2 starts
   ↓
User Data runs
   ↓
Install nginx
   ↓
Start nginx
   ↓
Create webpage
```

---

# 5. IMDSv2

This one sounds scary but is actually simple.

EC2 has something called:

> **Instance Metadata Service**

at:

```text
169.254.169.254
```

It contains information about the EC2.

IMDSv2 requires a **token** before metadata can be accessed.

Think:

```text
IMDSv1

"Give me metadata."

EC2 → "Okay"
```

Not as secure.

IMDSv2:

```text
EC2
 ↓
"Give me a token"
 ↓
AWS gives token
 ↓
"Now give me metadata + token"
 ↓
AWS gives metadata
```

Your lab requires:

```text
IMDSv2 = Required
```

---

# 6. AMI

AMI = **Amazon Machine Image**

Think of it as:

> A frozen template of an EC2.

For example:

```text
EC2
 ├── Amazon Linux
 ├── nginx installed
 ├── nginx configured
 ├── webpage
 └── other configuration
        ↓
      AMI
```

Then:

```text
AMI
 ↓
New EC2
```

The new EC2 gets what was inside the image.

---

# 🟢 NOW LET'S ACTUALLY DO THE LAB

We'll do this **one tiny step at a time**.

Don't jump ahead.

---

# PART 1 — Create the IAM Role

Go to:

**AWS Console → IAM → Roles**

Click:

**Create role**

---

## Step 1

For trusted entity:

```text
AWS service
```

Then:

```text
Use case → EC2
```

Click:

**Next**

---

## Step 2 — Permissions

Search:

```text
AmazonSSMManagedInstanceCore
```

Select it.

This is important.

Your role should have:

```text
cloudadhar-role-ec2-ssm
        |
        └── AmazonSSMManagedInstanceCore
```

Don't add AdministratorAccess.

Click:

**Next**

---

# Step 3 — Name the role

Role name:

```text
cloudadhar-role-ec2-ssm
```

Add these tags:

```text
Project = AWS-Zero-to-Hero
Module = EC2 Fundamentals
Environment = Training
Owner = CloudAdhar
ManagedBy = Manual
CleanupAfter = 25 July 2026
DataClassification = Training-Only
```

Then:

**Create role**

---

# 🟢 STOP HERE

At this point, you should have:

```text
IAM
 |
 └── Role
      |
      └── cloudadhar-role-ec2-ssm
             |
             └── AmazonSSMManagedInstanceCore
```

That's it.

---

# PART 2 — Create Security Group

Now go:

**EC2 → Security Groups**

Click:

**Create security group**

Use:

```text
Security group name:
cloudadhar-sg-nginx-public
```

Description:

```text
Public HTTP access for nginx training instance
```

Select the VPC you're using for the lab.

---

# Inbound rules

Add:

```text
Type: HTTP
Port: 80
Source: My IP
```

AWS will convert your IP into something like:

```text
203.xxx.xxx.xxx/32
```

The `/32` means:

> Only this one IP address.

---

## 🚨 VERY IMPORTANT

Do NOT create:

```text
SSH
0.0.0.0/0
```

We don't need SSH.

We're going to use:

```text
Session Manager
```

---

# Outbound

Leave the default outbound rule unless your instructor specifically says otherwise.

Usually:

```text
All traffic
0.0.0.0/0
```

This allows the EC2 to reach things such as package repositories.

---

# Tags

Again:

```text
Project = AWS-Zero-to-Hero
Module = EC2 Fundamentals
Environment = Training
Owner = CloudAdhar
ManagedBy = Manual
CleanupAfter = 25 July 2026
DataClassification = Training-Only
```

Create the Security Group.

---

# 🧠 What have we created?

We now have:

```text
                 AWS
                  |
        ┌─────────┴─────────┐
        ↓                   ↓
 IAM Role              Security Group
        |                   |
 cloudadhar-             HTTP : 80
 role-ec2-ssm            from My IP
        |
 AmazonSSMManaged
 InstanceCore
```

We haven't created the EC2 yet.

---

# PART 3 — Launch the Builder EC2

Go to:

**EC2 → Instances → Launch instances**

---

## Name

Use EXACTLY:

```text
cloudadhar-ec2-ami-builder-01
```

---

# Application and OS Image

Choose:

```text
Amazon Linux 2023
```

Don't choose Ubuntu.

Don't choose Windows.

We specifically want:

```text
Amazon Linux 2023
```

---

# Instance type

Use the small instructor-approved instance type from your lab.

For example, if your class permits it:

```text
t3.micro
```

But **follow your instructor's approved type if different**.

---

# Key pair

You don't need SSH for this lab.

So:

```text
Key pair → Proceed without a key pair
```

The important thing is that we use Session Manager.

---

# Network settings

Choose the VPC/subnet appropriate for your training environment.

Security Group:

```text
cloudadhar-sg-nginx-public
```

Public IPv4:

You need internet access for:

```text
dnf install nginx
```

and you'll eventually access nginx through HTTP.

So use a public subnet/public IPv4 setup if that's how your lab environment is configured.

---

# IAM role

Under advanced/details, find:

```text
IAM instance profile
```

Choose:

```text
cloudadhar-role-ec2-ssm
```

---

# Metadata options

This is VERY important.

Find:

```text
Metadata version
```

Set:

```text
V2 only
```

or equivalent wording such as:

```text
IMDSv2
Required
```

The final configuration should be:

```text
IMDSv2 = Required
```

---

# User Data

Scroll down to:

**Advanced details → User data**

Paste exactly:

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

---

# 🧠 What will happen?

When EC2 starts:

```text
EC2 boots
   ↓
cloud-init starts
   ↓
User Data executes
   ↓
dnf install nginx
   ↓
nginx starts
   ↓
HTML page created
```

That's your **bootstrap**.

---

# Launch it

Click:

**Launch instance**

You should now see:

```text
cloudadhar-ec2-ami-builder-01
```

Wait until:

```text
Instance state = Running
```

and:

```text
Status checks = 2/2
```

---

# 🟢 PART 4 — Connect WITHOUT SSH

This is an important learning moment.

Select:

```text
cloudadhar-ec2-ami-builder-01
```

Click:

**Connect**

You should see options such as:

```text
EC2 Instance Connect
Session Manager
SSH client
```

Choose:

**Session Manager**

Then:

**Connect**

If everything is configured correctly, AWS opens a terminal in your browser.

You are now inside your EC2.

Something like:

```text
[ssm-user@ip-10-xxx-xxx-xxx ~]$
```

Don't worry about the exact prompt.

---

# 🧪 PART 5 — Check User Data

Now run:

```bash
sudo cloud-init status --wait
```

This basically asks:

> "Has the startup script finished?"

You want something like:

```text
status: done
```

---

# Check nginx

Run:

```bash
sudo systemctl status nginx --no-pager
```

You want:

```text
Active: active (running)
```

---

# Check HTTP locally

Run:

```bash
curl -I http://localhost
```

You should see something like:

```text
HTTP/1.1 200 OK
```

The important thing is:

```text
200 OK
```

---

# Check User Data logs

Run:

```bash
sudo tail -n 40 /var/log/cloud-init-output.log
```

This lets you see what User Data did.

You should see evidence that nginx installation succeeded.

---

# 🧠 Understand what just happened

You started with:

```text
Amazon Linux 2023
```

Then User Data did:

```text
Install nginx
      ↓
Start nginx
      ↓
Create webpage
```

So now:

```text
Builder EC2
   |
   └── nginx
         |
         └── CloudAdhar webpage
```

---

# 🧪 PART 6 — Test IMDSv2

This is another important part.

We're going to prove:

> **IMDSv1 doesn't work.**

Run:

```bash
curl -sS -o /dev/null \
  -w 'IMDSv1 HTTP status: %{http_code}\n' \
  --max-time 3 \
  http://169.254.169.254/latest/meta-data/instance-id
```

Expected:

```text
IMDSv1 HTTP status: 401
```

### What does 401 mean?

Basically:

> "Nope. You didn't provide the required token."

That's exactly what we want.

---

# 🟢 Now test IMDSv2 correctly

First request a token:

```bash
TOKEN=$(curl -sS -X PUT \
  -H 'X-aws-ec2-metadata-token-ttl-seconds: 21600' \
  http://169.254.169.254/latest/api/token)
```

Now use that token:

```bash
curl -sS -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/instance-id
```

You should get an instance ID such as:

```text
i-0123456789abcdef
```

Then:

```bash
curl -sS -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/placement/availability-zone
```

You should get something like:

```text
ap-south-1a
```

Then clean up the token:

```bash
unset TOKEN
```

---

# 🧠 Your IMDS proof

You have now demonstrated:

```text
Tokenless request
       ↓
      401
       ↓
IMDSv1 blocked ✅


Token request
       ↓
Receive token
       ↓
Use token
       ↓
Metadata returned ✅
```

That's exactly what your instructor wants to see.

---

# PART 7 — Patch the Builder

Now we're going to update the OS.

First:

```bash
cat /etc/os-release
```

This tells you which Linux version you're using.

Then:

```bash
sudo dnf check-update || test $? -eq 100
```

The weird-looking part:

```text
|| test $? -eq 100
```

is intentional.

`dnf check-update` can return exit code `100` when updates are available. That isn't necessarily a failure.

Then:

```bash
sudo dnf upgrade -y
```

This applies available updates.

Restart nginx:

```bash
sudo systemctl restart nginx
```

Check:

```bash
curl -I http://localhost
```

You still want:

```text
200 OK
```

Then:

```bash
sudo dnf clean all
```

This cleans package-manager cache.

---

# 🧠 Now we reach the important part

Your EC2 is now something like:

```text
┌───────────────────────────────────┐
│ Builder EC2                       │
│                                   │
│ Amazon Linux 2023                 │
│ Updated                           │
│ nginx installed                   │
│ nginx enabled                     │
│ nginx running                     │
│ webpage configured                │
│ IMDSv2 required                   │
└───────────────────────────────────┘
                 |
                 | CREATE IMAGE
                 ↓
        ┌───────────────────┐
        │ Golden AMI v2     │
        └───────────────────┘
```

---

# PART 8 — Create the Golden AMI

Before creating it:

Make sure you don't have:

* passwords
* secret keys
* temporary files
* host-specific information

Then go to:

**EC2 → Instances**

Select:

```text
cloudadhar-ec2-ami-builder-01
```

Choose:

**Actions → Image and templates → Create image**

---

# Image name

Use:

```text
cloudadhar-ami-nginx-golden-v2-20260725
```

Description can explain that it contains:

```text
Amazon Linux 2023 with patched nginx for Week 4 Golden AMI lab
```

---

# Reboot

Your lab says:

> reboot enabled

So keep:

```text
No reboot = unchecked
```

In other words:

```text
Reboot instance = YES
```

Why?

AWS can reboot the instance to create a more consistent image.

---

# Create image

Click:

**Create image**

Now AWS starts creating the AMI.

Go to:

**EC2 → AMIs**

Look for:

```text
cloudadhar-ami-nginx-golden-v2-20260725
```

Initially it may say:

```text
Pending
```

Wait.

Eventually:

```text
Available
```

---

# 🧠 What did we just accomplish?

This:

```text
Builder EC2
   |
   | Amazon Linux
   | nginx
   | webpage
   | updates
   | configuration
   ↓
Golden AMI v2
```

The AMI is now your **golden template**.

---

# PART 9 — Launch Test EC2

Now we test whether our AMI actually works.

Go:

**EC2 → AMIs → Owned by me**

Select:

```text
cloudadhar-ami-nginx-golden-v2-20260725
```

Click:

**Launch instance from AMI**

---

# Name

Use:

```text
cloudadhar-ec2-ami-test-v2-01
```

---

# VERY IMPORTANT

This EC2 should use:

```text
Golden AMI v2
```

And:

```text
User Data = EMPTY
```

This is the most important test.

---

# Why no User Data?

Because we're trying to prove:

```text
AMI contains nginx
```

If you put:

```bash
dnf install nginx
```

in User Data again, you wouldn't know whether nginx came from:

```text
AMI
```

or:

```text
User Data
```

So:

```text
User Data = NOTHING
```

---

# IAM Role

Use:

```text
cloudadhar-role-ec2-ssm
```

---

# IMDS

Again:

```text
IMDSv2 = Required
```

---

# Security Group

Use:

```text
cloudadhar-sg-nginx-public
```

or the instructor-approved equivalent for the test instance.

HTTP should be allowed from:

```text
Your IP
```

---

# No key pair

Again:

```text
No key pair
```

because:

```text
Session Manager
```

---

# Launch

Now launch it.

Wait for:

```text
Running
```

and:

```text
2/2 status checks
```

---

# 🧪 PART 10 — Connect using Session Manager

Select:

```text
cloudadhar-ec2-ami-test-v2-01
```

→ **Connect**

→ **Session Manager**

→ **Connect**

Now you're inside the NEW EC2.

---

# Test 1 — Is nginx enabled?

Run:

```bash
sudo systemctl is-enabled nginx
```

Expected:

```text
enabled
```

---

# Test 2 — Is nginx running?

```bash
sudo systemctl is-active nginx
```

Expected:

```text
active
```

---

# Test 3 — Does nginx respond?

```bash
curl -I http://localhost
```

Expected:

```text
HTTP/1.1 200 OK
```

---

# Test 4 — Check OS

```bash
cat /etc/os-release
```

You should see Amazon Linux information.

---

# 🎉 THIS IS THE BIG PROOF

You created:

```text
Builder
   |
   | User Data installed nginx
   ↓
Golden AMI
   |
   | launched WITHOUT User Data
   ↓
Test EC2
   |
   ↓
nginx works
```

Therefore:

> **nginx came from the AMI.**

That's the heart of this lab.

---

# 🧠 Your entire manual lab in one picture

```text
                 AWS
                  |
          ┌───────┴────────┐
          |                |
       IAM Role        Security Group
          |                |
   SSMManagedCore       HTTP : 80
          |                |
          └───────┬────────┘
                  ↓
       cloudadhar-ec2-ami-builder-01
                  |
          IMDSv2 Required
                  |
             User Data
                  |
        ┌─────────┴─────────┐
        ↓                   ↓
   Install nginx       Create webpage
        |                   |
        └─────────┬─────────┘
                  ↓
            Patch / Upgrade
                  |
                  ↓
        Create Golden AMI v2
                  |
                  ↓
cloudadhar-ami-nginx-golden-v2-20260725
                  |
                  ↓
       Test EC2 — NO User Data
                  |
                  ↓
           nginx already works
                  |
                  ↓
                SUCCESS
```

---

# 🟣 NOW — THE AUTOMATION PART

Everything above was:

> **Manual Golden AMI creation.**

Now AWS gives us a service called:

> **EC2 Image Builder**

Its job is basically:

> "AWS, please automatically build my Golden AMI for me."

Instead of manually doing:

```text
Launch EC2
 ↓
Install nginx
 ↓
Patch
 ↓
Create AMI
 ↓
Launch test EC2
 ↓
Test nginx
```

Image Builder automates it.

---

# 🧠 Manual vs Image Builder

### Manual

```text
YOU
 |
 ↓
EC2
 |
 ↓
Install nginx
 |
 ↓
Patch
 |
 ↓
Create AMI
 |
 ↓
Test
```

### Image Builder

```text
             Image Builder
                  |
          ┌───────┴────────┐
          ↓                ↓
       Build             Test
          |                |
          ↓                ↓
      nginx AMI       nginx validation
          |
          ↓
      Golden AMI
```

---

# PART 11 — Image Builder Role

Go:

**IAM → Roles → Create role**

Choose:

```text
AWS service
```

→

```text
EC2
```

Attach:

```text
EC2InstanceProfileForImageBuilder
```

and:

```text
AmazonSSMManagedInstanceCore
```

Role name:

```text
cloudadhar-role-image-builder
```

No:

```text
AdministratorAccess
```

---

# PART 12 — Image Builder Security Group

Create Security Group:

```text
cloudadhar-sg-image-builder
```

Description:

```text
No-inbound Security Group for Image Builder
```

Inbound:

```text
NONE
```

That's intentional.

Image Builder's temporary instances don't need public inbound SSH/HTTP for this build.

Outbound access must allow the instances to reach what they need, such as:

```text
Systems Manager
Amazon Linux repositories
AWS services
```

---

# PART 13 — Build Component

This is where you tell Image Builder:

> "When you build my AMI, install nginx."

Create:

```text
cloudadhar-component-nginx-build
```

Version:

```text
1.0.0
```

Category:

```text
Build
```

The YAML you pasted is basically saying:

```text
BUILD
 |
 ├── install nginx
 ├── enable nginx
 ├── start nginx
 └── create webpage
```

Then validation says:

```text
Is nginx enabled?
       ↓
Is nginx active?
       ↓
Does webpage exist?
       ↓
Does webpage contain expected text?
```

If yes:

```text
BUILD SUCCESS
```

---

# PART 14 — Test Component

Now create:

```text
cloudadhar-component-nginx-test
```

Version:

```text
1.0.0
```

Category:

```text
Test
```

Its job is NOT to install nginx.

This is extremely important.

The build component:

```text
INSTALL
```

The test component:

```text
VERIFY
```

The test does:

```text
Is nginx enabled?
       ↓
Start nginx
       ↓
Is nginx active?
       ↓
curl localhost
       ↓
Expected webpage?
```

---

# 🧠 Remember this

```text
BUILD component
      ↓
"Make it"

TEST component
      ↓
"Check it"
```

---

# PART 15 — Image Recipe

Now we tell Image Builder:

> "What exactly should my AMI contain?"

Create:

```text
cloudadhar-recipe-nginx-golden
```

Version:

```text
1.0.0
```

Base image:

```text
Amazon Linux 2023
```

Then build components in this order:

```text
1. update-linux
2. cloudadhar-component-nginx-build/1.0.0
```

Test component:

```text
cloudadhar-component-nginx-test/1.0.0
```

---

# Why this order?

Think:

```text
Amazon Linux
      ↓
Update Linux
      ↓
Install nginx
      ↓
Create AMI
      ↓
Launch test instance
      ↓
Test nginx
```

Perfect.

---

# VERY IMPORTANT — User Data

For the recipe:

```text
User Data = BLANK
```

Why?

Because the component is responsible for installing nginx.

---

# PART 16 — Infrastructure Configuration

This tells Image Builder:

> "Where should you temporarily build this image?"

Create:

```text
cloudadhar-infra-nginx-image-builder
```

It needs:

```text
Instance profile
    ↓
cloudadhar-role-image-builder
```

and:

```text
Security Group
    ↓
cloudadhar-sg-image-builder
```

Use an instructor-approved small instance.

Choose:

```text
VPC
Subnet
```

with outbound connectivity.

---

# IMDSv2

Set:

```text
IMDSv2 required
```

Again.

We're keeping our temporary build/test EC2 instances secure too.

---

# Key pair

Use:

```text
None
```

We don't need SSH.

---

# PART 17 — Distribution Configuration

This answers:

> "Where should Image Builder publish my finished AMI?"

Create:

```text
cloudadhar-distribution-nginx-golden
```

Region:

```text
ap-south-1
```

Output AMI name:

```text
cloudadhar-ami-nginx-golden-{{imagebuilder:buildDate}}
```

Launch permission:

```text
Private
```

No sharing with other AWS accounts.

No other Region for this training run.

---

# PART 18 — Pipeline

Now we bring everything together.

Create:

```text
cloudadhar-pipeline-nginx-golden
```

Schedule:

```text
Manual
```

Image tests:

```text
Enabled
```

And connect:

```text
Recipe
   ↓
Infrastructure Configuration
   ↓
Distribution Configuration
```

So the pipeline becomes:

```text
Recipe
  |
  ├── Amazon Linux
  ├── update-linux
  ├── nginx build component
  └── nginx test component
        |
        ↓
Infrastructure Configuration
        |
        ↓
Temporary Build EC2
        |
        ↓
Build AMI
        |
        ↓
Temporary Test EC2
        |
        ↓
Run nginx test
        |
        ↓
Private Golden AMI
```

---

# 🚀 PART 19 — Run Pipeline

Before running:

Check:

```text
Pipeline
   ↓
Image recipe
   ↓
Correct recipe version
```

Then:

**Actions → Run pipeline**

And now:

> **WAIT.**

Don't start another execution while this one is running.

---

# 🧠 What Image Builder is doing behind the scenes

You may see stages like:

```text
LaunchBuildInstance
        ↓
ApplyBuildComponents
        ↓
InventoryCollection
        ↓
RunSanitizeScript
        ↓
RunSysPrepScript
        ↓
CreateOutputAMI
        ↓
TerminateBuildInstance
```

Then the test workflow happens.

Think:

```text
BUILD
 ↓
CLEAN
 ↓
CREATE AMI
 ↓
TEST AMI
 ↓
SUCCESS
```

---

# 🎯 The most important mental model

Don't memorize 20 AWS screens.

Remember these **three layers**:

## Layer 1 — Manual learning

```text
EC2
 ↓
User Data
 ↓
nginx
 ↓
AMI
 ↓
Test EC2
```

You learn **what a Golden AMI is**.

---

## Layer 2 — Security

```text
IAM Role
Security Group
Session Manager
IMDSv2
No public SSH
```

You learn:

> **How to build it securely.**

---

## Layer 3 — Automation

```text
Image Builder
     ↓
Recipe
     ↓
Build Component
     ↓
Test Component
     ↓
Infrastructure Config
     ↓
Distribution Config
     ↓
Pipeline
     ↓
Golden AMI
```

You learn:

> **How to automate Golden AMI creation.**

---

# ⭐ If your instructor asks "Explain this lab"

You can think of your answer like this:

> "First I launched an Amazon Linux 2023 builder EC2 with an SSM IAM role and IMDSv2 required. I used User Data to install and configure nginx. I validated the bootstrap process and verified that tokenless metadata access returned 401 while token-based IMDSv2 access worked. I then patched the instance and created a Golden AMI. I launched a second EC2 from that AMI without User Data and verified that nginx was already enabled and running. This proved that the nginx configuration was baked into the AMI. Finally, I automated the same lifecycle using EC2 Image Builder with separate build and test components, an image recipe, infrastructure configuration, distribution configuration, and a manual pipeline."

That's the **whole Day 7 story**.

---

## 🔑 10 things I want you to remember

```text
1. EC2 = virtual computer

2. IAM Role = what EC2 is allowed to do

3. Security Group = network traffic gate

4. User Data = startup script

5. nginx = web server

6. IMDSv2 = secure way to access EC2 metadata

7. AMI = reusable EC2 template

8. Golden AMI = tested, trusted baseline image

9. Image Builder = automates Golden AMI creation

10. Build component = install/configure
    Test component = verify
```

### And the single most important proof:

```text
Builder EC2
   |
   | User Data installs nginx
   ↓
Golden AMI
   |
   | NO User Data
   ↓
Test EC2
   |
   ↓
nginx works
```

**That is why you can confidently say: "nginx came from the Golden AMI."**
