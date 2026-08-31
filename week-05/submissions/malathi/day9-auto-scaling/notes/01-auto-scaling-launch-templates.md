# 📘 Week 5 — Day 9

# Auto Scaling & Launch Templates

## 🧠 First: What problem are we solving?

Imagine you have a shop.

During normal time:

```text
👤 Customers
     |
     v
🏪 Shop
     |
     v
💻 1 EC2
```

But suddenly many customers come:

```text
👤👤👤👤👤👤👤
        |
        v
      🏪 Shop
        |
        v
      💻 EC2
```

One EC2 may become too busy.

AWS can automatically create another EC2:

```text
👤👤👤👤👤👤👤
        |
        v
      🏪
     /  \
    v    v
  💻 EC2 💻 EC2
```

When customers go away, AWS can remove the extra EC2.

That is **Auto Scaling**.

---

# 1️⃣ Launch Template

### 🧒 Think of it like a recipe

Suppose Mom has a recipe:

```text
🍕 Pizza Recipe

Flour
Cheese
Tomato
Oven = 200°C
```

Every time she wants pizza, she follows the same recipe.

A **Launch Template** is the recipe for an EC2 instance.

It tells AWS:

```text
What AMI?
What instance type?
Which Security Group?
Which IAM role?
What User Data?
How much storage?
Is IMDSv2 required?
```

So:

```text
Launch Template
       |
       | "Build EC2 like this"
       v
     EC2
```

### ⭐ Remember

> **Launch Template = EC2 recipe**

---

# 2️⃣ Why Launch Template?

Older AWS had:

**Launch Configuration**

But it is now **legacy**.

For new designs:

> ✅ Use **Launch Templates**

Launch Templates have an important feature:

### Versions

Think of a notebook:

```text
Launch Template
      |
      ├── Version 1
      ├── Version 2
      └── Version 3
```

Maybe:

```text
Version 1 → nginx old version
Version 2 → nginx updated version
Version 3 → security update
```

If Version 3 has a problem:

```text
Version 3 ❌
     ↓
Rollback
     ↓
Version 2 ✅
```

### 🧠 Exam memory

> **Launch Template = recipe + versions**

---

# 3️⃣ What goes inside Launch Template?

Think:

```text
             📋 Launch Template
                    |
       ┌────────────┼────────────┐
       ↓            ↓            ↓
      AMI      Instance Type   Security Group
       ↓            ↓            ↓
    💿 OS          💻 Size       🔐 Firewall

       ┌────────────┼────────────┐
       ↓            ↓            ↓
    IAM Role     User Data      Storage
       ↓            ↓            ↓
   Permissions   Installation     gp3

                    +
                 IMDSv2
```

So remember:

### **A I S U S I**

You don't need to memorize the letters. Just remember:

**"How should my EC2 be born?"**

The Launch Template answers that question.

---

# 4️⃣ Auto Scaling Group

Now we have the EC2 recipe.

But who decides **how many EC2s we need?**

👉 **Auto Scaling Group (ASG)**

Think of ASG as the **manager**.

```text
Launch Template
      |
      | recipe
      v
     ASG
      |
      | "I need 2 EC2s"
      v
   EC2 + EC2
```

### Launch Template says:

> "HOW should EC2 be created?"

### ASG says:

> "HOW MANY EC2s should exist?"

⭐ Very important:

> **Launch Template = HOW**
> **ASG = HOW MANY + WHERE**

---

# 5️⃣ Minimum, Desired, Maximum

This is VERY important for the exam.

Our classroom values are:

```text
Minimum = 1
Desired = 1
Maximum = 2
```

Let's understand like a kid.

---

## 🟢 Minimum = 1

ASG says:

> "I should normally never have fewer than 1 EC2."

```text
ASG
 |
 └── 💻
```

---

## 🟡 Desired = 1

ASG says:

> "Right now, I want 1 EC2."

```text
Desired = 1

ASG
 |
 └── 💻
```

---

## 🔴 Maximum = 2

ASG says:

> "I won't normally go above 2 EC2s."

```text
Maximum = 2

ASG
 |
 ├── 💻
 └── 💻
```

---

### 🧠 Easy memory

```text
MIN     DESIRED     MAX
 ↓         ↓         ↓
Lowest    NOW       Highest

 1         1          2
```

Think:

> **Minimum = floor**
> **Desired = what I want now**
> **Maximum = ceiling**

---

# 6️⃣ Why two Availability Zones?

Suppose our EC2 is only here:

```text
ap-south-1a

      💻
```

What if that AZ has a problem?

😱 EC2 may become unavailable.

Instead:

```text
AWS Region
ap-south-1
│
├── AZ 1a
│     └── 💻 EC2
│
└── AZ 1c
      └── 💻 EC2
```

Now our application has better availability.

### 🧠 Remember

> **Don't put everything in one AZ.**

For this classroom lab:

```text
AZ 1 → ap-south-1a
AZ 2 → ap-south-1c
```

---

# 7️⃣ What happens during scale-out?

Suppose:

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

CPU becomes very high.

AWS says:

> "EC2 is getting too busy. Let's create another one."

```text
ASG
 |
 ├── 💻 EC2-1
 └── 💻 EC2-2
```

So:

```text
1 → 2
```

This is called:

# 📈 Scale OUT

---

# 8️⃣ What happens during scale-in?

Now customers leave.

CPU becomes low.

AWS says:

> "We don't need two EC2s anymore."

So:

```text
ASG
 |
 └── 💻 EC2-1
```

Therefore:

```text
2 → 1
```

This is:

# 📉 Scale IN

### 🧠 Memory trick

```text
OUT = Add EC2 ➕
IN  = Remove EC2 ➖
```

---

# 9️⃣ Health Checks

Now imagine EC2 is running:

```text
💻 EC2
Status: RUNNING ✅
```

But nginx has crashed:

```text
💻 EC2
Status: RUNNING ✅

nginx
Status: DEAD ❌
```

Is the application healthy?

❌ No.

This is why we have different health checks.

---

# 🔟 EC2 Health Check

EC2 health check asks:

> "Is the EC2 machine/system okay?"

For example:

```text
💻 EC2
     |
     v
System okay?
```

It checks infrastructure-level problems.

---

# 1️⃣1️⃣ ELB Health Check

The Load Balancer asks:

> "Is the APPLICATION working?"

For our lab:

```text
/health.html
```

For example:

```text
ALB
 |
 | "Are you healthy?"
 v
EC2
 |
 v
/health.html
 |
 v
200 OK ✅
```

If nginx is broken:

```text
ALB
 |
 v
EC2
 |
 v
/health.html
 |
 v
❌ Failure
```

The ALB can stop sending traffic to that unhealthy target.

---

# ⭐ Very important difference

| Health check | Question                     |
| ------------ | ---------------------------- |
| EC2 health   | Is the **machine** okay?     |
| ELB health   | Is the **application** okay? |

### 🧠 Easy example

Your child is sitting in class.

```text
👦 Child is sitting
```

But teacher asks:

> "Can he answer the question?"

Being physically present doesn't mean he's working properly.

Same with EC2:

```text
EC2 RUNNING ≠ Application Healthy
```

---

# 1️⃣2️⃣ Health Check Grace Period

When AWS creates a new EC2:

```text
EC2 starts
   ↓
Linux boots
   ↓
User Data runs
   ↓
nginx starts
   ↓
health check
```

This takes some time.

If AWS checks immediately:

```text
EC2 just started
       ↓
Health check
       ↓
❌ Not ready yet
```

AWS might think something is wrong.

So we give it a:

# ⏳ Health Check Grace Period

It means:

> "Give the new EC2 some time to start before deciding it's unhealthy."

---

# 1️⃣3️⃣ Instance Warmup

After scaling out:

```text
New EC2
   ↓
Starting
   ↓
Getting ready
   ↓
Stable
```

**Instance warmup** gives the new instance time to stabilize before its metrics are fully used for scaling decisions.

### Don't confuse:

**Grace period**

→ Gives the new instance time to pass health checks.

**Warmup**

→ Gives the new instance time to stabilize before scaling decisions rely heavily on its metrics.

---

# 1️⃣4️⃣ Security Group

This is VERY important.

We don't want:

```text
Internet
   |
   | HTTP
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
    | HTTP
    v
   EC2
```

The EC2 Security Group should allow HTTP **from the ALB Security Group**.

So:

```text
ALB SG
  |
  | HTTP :80
  v
EC2 SG
```

Not:

```text
Internet
   |
   | HTTP :80
   v
EC2 ❌
```

### 🧠 Remember

> **Internet talks to ALB.**
> **ALB talks to EC2.**

---

# 1️⃣5️⃣ Scaling Policies

Now who tells ASG:

> "Create another EC2!"

That's the job of a **Scaling Policy**.

There are different types.

---

## 🎯 Target Tracking

Imagine your teacher says:

> "Keep the classroom temperature around 24°C."

AWS says:

> "Keep average CPU around 50%."

If CPU becomes too high:

```text
CPU ↑
 ↓
ASG adds EC2
 ↓
CPU average ↓
```

This is:

# Target Tracking

### Best for:

> "Keep this metric around my target."

Example:

```text
Target CPU = 50%
```

---

# 1️⃣6️⃣ Step Scaling

Imagine:

```text
CPU 55% → Add 1 EC2
CPU 80% → Add 2 EC2
CPU 95% → Add 3 EC2
```

The bigger the problem, the bigger the action.

That's:

# Step Scaling

### Memory

> **Small problem → small step**
> **Big problem → big step**

---

# 1️⃣7️⃣ Scheduled Scaling

Suppose every day your shop becomes busy at 7 PM.

You already know this.

So tell AWS:

```text
6:30 PM
   ↓
Increase capacity
```

This is:

# Scheduled Scaling

Perfect when you **know the busy time in advance**.

Example:

```text
Monday-Friday
9 AM → increase
6 PM → decrease
```

---

# 1️⃣8️⃣ Predictive Scaling

Suppose AWS looks at your previous traffic:

```text
Monday   → busy
Tuesday  → busy
Wednesday → busy
Thursday → busy
Friday   → very busy
```

It can use historical patterns to **forecast future demand**.

That's:

# Predictive Scaling

Usually used with dynamic scaling to handle unexpected changes too.

### 🧠 Memory

```text
Target Tracking → Keep target
Step Scaling    → Bigger problem = bigger step
Scheduled       → I know the time
Predictive      → AWS forecasts the pattern
```

---

# 1️⃣9️⃣ Lifecycle Hooks

Sometimes you don't want an EC2 to immediately start receiving traffic.

You want to do something first.

For example:

```text
EC2 created
   ↓
⏸️ WAIT
   ↓
Install software
   ↓
Send logs
   ↓
Validate
   ↓
Continue
```

That's a:

# Lifecycle Hook

There are two important places.

### Launch

```text
Pending:Wait
```

Instance is being prepared.

### Termination

```text
Terminating:Wait
```

Instance is being shut down.

You might use this time for:

* draining
* log shipping
* cleanup
* initialization

---

# 2️⃣0️⃣ Warm Pool

Imagine you need EC2 very quickly.

Normally:

```text
Need EC2
  ↓
Launch
  ↓
Boot
  ↓
Install
  ↓
Ready
```

That takes time.

A **Warm Pool** keeps already-initialized instances ready/stopped/hibernated depending on configuration.

So:

```text
Warm Pool
 ├── 💻
 └── 💻
      ↓
Need capacity
      ↓
Move into ASG
```

### 🧠 Remember

> **Warm Pool = EC2s kept ready for faster startup**

But don't use one just because it sounds cool.

It adds:

* cost
* complexity

Use it when startup speed really matters.

---

# 2️⃣1️⃣ Termination Policy

Suppose ASG has:

```text
💻 EC2-A
💻 EC2-B
💻 EC2-C
```

And it needs to remove one.

Which one?

The **termination policy** helps decide.

But first AWS considers things like **Availability Zone balance**.

### Simple idea:

> **Termination policy = helps ASG decide which eligible instance to remove during scale-in.**

---

# 2️⃣2️⃣ Scale-in Protection

Imagine:

```text
💻 EC2-A
```

is doing something very important.

You don't want normal scale-in to remove it.

You can enable:

# Scale-in Protection

Meaning:

> "Please don't terminate this instance during normal ASG scale-in."

---

# 2️⃣3️⃣ Instance Refresh

Suppose you have:

```text
Old AMI
   ↓
10 EC2 instances
```

You create a new Launch Template version:

```text
New AMI
```

You don't want to manually replace all 10 EC2s.

Instance Refresh helps gradually replace old instances with new ones.

```text
OLD OLD OLD OLD
 ↓
NEW OLD OLD OLD
 ↓
NEW NEW OLD OLD
 ↓
NEW NEW NEW OLD
 ↓
NEW NEW NEW NEW
```

### 🧠 Remember

> **Instance Refresh = gradually update the fleet**

Very useful for:

* new AMI
* security patches
* application updates

---

# 2️⃣4️⃣ Mixed Instances

Normally ASG might use:

```text
t3.small
t3.small
t3.small
```

Mixed Instances lets you use compatible different instance types:

```text
t3.small
t3a.small
another compatible type
```

It can also combine:

```text
On-Demand
+
Spot
```

Example:

```text
ASG
 |
 ├── On-Demand 💻
 ├── On-Demand 💻
 ├── Spot 💻
 └── Spot 💻
```

Spot is cheaper but can be interrupted.

So:

> Use Spot when your application can tolerate interruption.

---

# 🧠 SUPER IMPORTANT DAY 9 CHEAT SHEET

Write this in your notebook:

```text
Launch Template
= EC2 RECIPE

ASG
= HOW MANY EC2 + WHERE

Minimum
= LOWEST

Desired
= WHAT WE WANT NOW

Maximum
= HIGHEST

Scale OUT
= ADD EC2

Scale IN
= REMOVE EC2

EC2 Health Check
= Is the MACHINE okay?

ELB Health Check
= Is the APPLICATION okay?

Target Tracking
= Keep metric around TARGET

Step Scaling
= Bigger problem → bigger action

Scheduled Scaling
= Known TIME

Predictive Scaling
= Forecast PATTERN

Lifecycle Hook
= PAUSE before launch/termination continues

Warm Pool
= READY EC2s for faster startup

Termination Policy
= Helps choose instance to remove

Scale-in Protection
= Don't remove this instance normally

Instance Refresh
= Gradually replace old instances

Mixed Instances
= Different instance types + On-Demand/Spot
```

## ⭐ The entire Day 9 in one picture

```text
                    👥 USERS
                       |
                       v
                      ALB
                       |
                       v
                  TARGET GROUP
                       |
                       v
                     ASG
                       |
             ┌─────────┴─────────┐
             |                   |
          EC2 AZ-1a           EC2 AZ-1c
             |                   |
             └─────────┬─────────┘
                       |
                Launch Template
                       |
        "How should EC2 be created?"
```

And the ASG watches capacity and scaling:

```text
             📊 CloudWatch Metric
                     |
                     v
              Scaling Policy
                     |
                     v
                    ASG
                  /     \
             Scale OUT  Scale IN
                |          |
                v          v
             1 → 2       2 → 1
```

### 🎯 SAA-C03 exam shortcut

If the question says:

**"Create repeatable/versioned EC2 launch settings"**
→ **Launch Template**

**"Maintain average CPU around a target"**
→ **Target Tracking**

**"Known peak at a particular time"**
→ **Scheduled Scaling**

**"EC2 is running but application is broken"**
→ **ELB health check**

**"Gradually replace old instances with new AMI"**
→ **Instance Refresh**

**"Need cheaper interruptible capacity"**
→ **Mixed Instances + Spot**

**"Application must survive an AZ failure"**
→ **Use multiple AZs**

