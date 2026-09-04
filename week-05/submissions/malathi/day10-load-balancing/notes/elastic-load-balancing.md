Let’s forget the complicated AWS words for a minute and imagine **a big school with three different types of gates**.

# 🏫 AWS Load Balancers 

Imagine you have **100 students** trying to enter your school.

If everyone uses **one door**, there will be a huge queue.

So you build a **Load Balancer**.

Its job is:

> **“Don’t send everyone to the same server. I’ll distribute the visitors among the available servers.”**

Think:

```text
                 👨‍👩‍👧‍👦 Users
                    |
                    v
             🚦 Load Balancer
              /      |      \
             v       v       v
          🖥️ Server 🖥️ Server 🖥️ Server
```

AWS gives us three important types:

```text
ALB 🧑‍💼     NLB 🚦     GWLB 🛡️
Web          Network    Security
Layer 7      Layer 4    Security appliances
```

The easiest way to remember them:

> **ALB = Web receptionist**
> **NLB = Traffic junction**
> **GWLB = Security checkpoint**

---

# 1️⃣ ALB — Application Load Balancer 🧑‍💼

Imagine a receptionist at a hotel.

A visitor says:

> “I want the **billing department**.”

The receptionist understands what the visitor is asking and sends them to the correct room.

That's ALB.

## 🧑‍💼 ALB understands HTTP

For example:

```text
User
 |
 | https://cloudadhar.com/api/users
 v
🧑‍💼 ALB
 |
 | "I see /api/users"
 v
🖥️ API Server
```

ALB can look at things like:

### 🌐 Host

```text
api.cloudadhar.local
```

ALB says:

> "Oh! This is for the API."

Send to:

```text
API servers
```

---

### 📁 Path

Suppose someone requests:

```text
/app1/login
```

ALB can say:

> "This starts with `/app1`."

Send to App 1.

```text
                ALB
                 |
        ┌────────┴────────┐
        |                 |
    /app1/*            /app2/*
        |                 |
        v                 v
    🖥️ App 1           🖥️ App 2
```

That's called **path-based routing**.

---

# 2️⃣ ALB Can Look at Headers

Imagine a customer has a special badge:

```text
Version: beta
```

ALB can read that HTTP header.

Then:

```text
Normal users → 🖥️ Production
Beta users   → 🧪 Beta
```

So ALB is basically saying:

> "Let me read the request and decide where it should go."

---

# 3️⃣ ALB Can Redirect

Suppose someone visits:

```text
http://cloudadhar.com
```

But you want HTTPS:

```text
https://cloudadhar.com
```

ALB can say:

> "Please use the secure door."

```text
HTTP
 |
 v
🧑‍💼 ALB
 |
 | Redirect
 v
HTTPS 🔒
```

---

# 4️⃣ ALB Can Give a Fixed Response

Imagine someone asks:

> "Is the website under maintenance?"

ALB doesn't necessarily need to ask a backend server.

It can directly respond:

```text
🔧 Website under maintenance.
Please come back later.
```

---

# 5️⃣ ALB Health Checks ❤️‍🩹

Now imagine you have three servers:

```text
🖥️ Server A ❤️
🖥️ Server B ❤️
🖥️ Server C 💀
```

ALB regularly asks:

> "Hey Server A, are you okay?"

> "Hey Server B, are you okay?"

> "Hey Server C, are you okay?"

Server C doesn't answer correctly.

ALB says:

> "Okay, I'm not sending new customers to Server C."

That's a **health check**.

```text
             ALB
          /   |   \
         ❤️  ❤️   💀
        App1 App2 App3

       App3 gets no
       new traffic
```

---

# 6️⃣ What is Draining? 🚪

This one is important.

Imagine Server A needs maintenance.

There are already customers inside.

You don't want to suddenly throw them out! 😄

So ALB says:

> "No new customers, please. Let the existing customers finish."

```text
New users
   ❌
   |
   v
🖥️ Server A
   ↑
Existing users
   ✅
```

This is called:

# **Deregistration Delay / Draining**

Think:

> **Draining = “Finish your current work, then go home.”**

---

# 7️⃣ ALB Blue-Green Deployment 🔵🟢

Imagine you have:

🔵 **Blue = old application**

🟢 **Green = new application**

You don't want to immediately send everyone to Green.

You can tell ALB:

```text
Blue  → 90%
Green → 10%
```

So:

```text
              ALB
               |
        ┌──────┴──────┐
        ↓             ↓
     🔵 Blue        🟢 Green
       90%            10%
```

If Green works well:

```text
Blue   → 50%
Green  → 50%
```

Then:

```text
Blue   → 10%
Green  → 90%
```

Finally:

```text
Blue   → 0%
Green → 100%
```

This is called **weighted target groups**.

Very useful for **Blue/Green deployments**.

---

# 8️⃣ Stickiness 🍪

Imagine you go to a restaurant.

The waiter gives you table #5.

Every time you come back, the restaurant tries to give you the same table.

That's roughly what **stickiness** means.

```text
You
 |
 v
ALB
 |
 v
🖥️ Server A

Next request
 |
 v
ALB
 |
 v
🖥️ Server A
```

The customer keeps going to the same place.

But in modern applications, it's often better to make applications **stateless** and store sessions somewhere shared.

---

# 🚦 Now Meet NLB

# 9️⃣ NLB — Network Load Balancer

NLB is different.

Remember the hotel receptionist?

ALB is like:

> "Tell me what you're asking for and I'll understand it."

NLB is more like a **traffic police officer**.

It doesn't care about the actual web page.

It mainly cares about:

```text
Where is the traffic coming from?
Where should the traffic go?
```

NLB works at:

# **Layer 4**

That means things like:

```text
TCP
UDP
TLS
```

---

# 🔟 ALB vs NLB — Easy Example

Suppose a request says:

```text
GET /payments
Host: api.cloudadhar.com
```

ALB can understand:

> "Ah! `/payments`."

NLB says:

> "I don't care about `/payments`."

NLB mainly sees the network connection.

Think:

```text
ALB 🧑‍💼
"I understand your web request."

NLB 🚦
"I understand your network traffic."
```

---

# 1️⃣1️⃣ Why Would We Use NLB?

Imagine you have a game server using **UDP**.

```text
🎮 Game Client
       |
       | UDP
       v
      NLB
    /     \
   v       v
🖥️ Game1 🖥️ Game2
```

ALB isn't the right choice for this kind of UDP traffic.

NLB is designed for Layer 4 traffic.

---

# 1️⃣2️⃣ Static IP — Important NLB Feature 📌

Imagine your company tells you:

> "Our firewall only allows traffic from this IP."

You need an IP that doesn't keep changing.

NLB can provide **static IPs per enabled Availability Zone**.

An internet-facing NLB can also use an **Elastic IP per AZ** during creation.

So you can think:

```text
Internet
   |
   v
NLB
 / \
IP1 IP2
```

This is one reason NLB is useful when **fixed public IP addresses** matter.

---

# 1️⃣3️⃣ TLS Pass-Through 🔒

This sounds scary but it's simple.

Suppose:

```text
User 🔒
   |
   | encrypted traffic
   v
NLB
   |
   | still encrypted
   v
🖥️ Server
```

NLB doesn't necessarily open the HTTPS conversation.

With a **TCP 443 listener**, it can pass the encrypted traffic to the backend.

The backend can decrypt it.

That's called:

> **TLS pass-through**

---

# 🛡️ Now Meet GWLB

# 1️⃣4️⃣ GWLB — Gateway Load Balancer

Imagine your school has a **security checkpoint**.

Before students enter:

```text
Student
   |
   v
🛡️ Security Check
   |
   v
🏫 School
```

The security system checks traffic before allowing it through.

GWLB is designed for things like:

```text
🔥 Firewall
🔍 IDS
🚨 IPS
🛡️ Security appliances
```

---

# 1️⃣5️⃣ GWLB Is NOT a Normal Web Load Balancer

This is very important.

Don't think:

```text
GWLB → nginx → website
```

That's not what GWLB is designed for.

Instead:

```text
Traffic
   |
   v
GWLB
   |
   v
🛡️ Firewall appliance
   |
   v
Destination
```

GWLB helps distribute traffic across **security appliances**.

---

# 1️⃣6️⃣ What is GENEVE 6081? 🧐

AWS uses a special encapsulation protocol with GWLB called:

# **GENEVE**

It uses:

```text
UDP 6081
```

You don't need to panic about this for now.

For the exam, remember:

> **GWLB → GENEVE → UDP 6081**

That's enough initially.

---

# 1️⃣7️⃣ The BIG Picture

Now put the three together.

```text
                 AWS LOAD BALANCERS
                        |
        ┌───────────────┼───────────────┐
        |               |               |
        v               v               v
     🧑‍💼 ALB          🚦 NLB          🛡️ GWLB
     Layer 7          Layer 4         Security
        |               |               |
     HTTP/HTTPS      TCP/UDP/TLS    Firewalls
        |               |               |
     Web routing     Network        Security
                    traffic         appliances
```

---

# 🧠 The Easiest Memory Trick

Think about **what the load balancer needs to understand**.

### 🧑‍💼 ALB

Needs to understand the **web request**.

```text
Host?
Path?
Header?
Query?
HTTP?
HTTPS?
```

Therefore:

> **ALB = Layer 7**

---

### 🚦 NLB

Doesn't need to understand the web page.

It cares about network traffic.

```text
TCP?
UDP?
TLS?
Static IP?
```

Therefore:

> **NLB = Layer 4**

---

### 🛡️ GWLB

Needs to send traffic through security appliances.

```text
Firewall?
IDS?
IPS?
Deep inspection?
```

Therefore:

> **GWLB = Security appliance load balancing**

---

# 🎯 Exam Questions Become Easy

### Question 1

> "I need `/api/*` to go to the API servers."

Answer:

**ALB**

Because that's HTTP path-based routing.

---

### Question 2

> "I need UDP traffic."

Answer:

**NLB**

---

### Question 3

> "I need a static public IP."

Answer:

**NLB**

---

### Question 4

> "I need AWS WAF for my web application."

Answer:

**ALB** (or CloudFront with WAF, depending on the architecture).

---

### Question 5

> "I need to send traffic through a third-party firewall."

Answer:

**GWLB**

---

### Question 6

> "I want Blue/Green HTTP traffic like 90% Blue and 10% Green."

Answer:

**ALB weighted target groups**

---

### Question 7

> "I want to remove a server without suddenly killing existing requests."

Answer:

**Deregistration delay / draining**

---

# 🏆 One-Line Cheat Sheet

| If the question says... | Think         |
| ----------------------- | ------------- |
| `/api/*`                | 🧑‍💼 **ALB** |
| Host header             | 🧑‍💼 **ALB** |
| HTTP/HTTPS routing      | 🧑‍💼 **ALB** |
| WAF                     | 🧑‍💼 **ALB** |
| Blue/Green percentage   | 🧑‍💼 **ALB** |
| TCP                     | 🚦 **NLB**    |
| UDP                     | 🚦 **NLB**    |
| Static IP / EIP         | 🚦 **NLB**    |
| TLS pass-through        | 🚦 **NLB**    |
| Firewall                | 🛡️ **GWLB**  |
| IDS / IPS               | 🛡️ **GWLB**  |
| Security appliance      | 🛡️ **GWLB**  |
| GENEVE UDP 6081         | 🛡️ **GWLB**  |

## ⭐ The one sentence I want you to remember

> **ALB understands the web request, NLB understands the network connection, and GWLB sends traffic through security appliances.**

If you remember **that one sentence**, most ALB vs NLB vs GWLB questions become much easier.


***




Don't try to memorize the AWS console first. First understand **what we are building and WHY**. Then every console step will make sense.

# 🏫 Day 10 — The CloudAdhar School Story

Imagine you have a school called:

> 🏫 **CloudAdhar School**

There are two classrooms:

```text
🔵 BLUE classroom
🟢 GREEN classroom
```

Each classroom has one computer/server running nginx.

```text
🔵 Blue EC2          🟢 Green EC2
     🖥️                   🖥️
   nginx                 nginx
```

Now lots of students want to visit the school website.

Instead of students directly going to the computers, we put a **receptionist** in front.

```text
                 👨‍👩‍👧‍👦 Users
                     |
                     v
              🧑‍💼 ALB
             /       \
            v         v
        🔵 Blue     🟢 Green
          🖥️          🖥️
```

Later, we'll put another type of receptionist called **NLB** in front.

---

# 🧩 First Understand the Whole Lab

Your Day 10 lab has **two major parts**:

### Part 1 — ALB

We will teach ALB:

> "Look at what the user requested and decide where to send them."

We'll test:

* Default routing
* Host routing
* Path routing
* Weighted Blue/Green
* Stickiness
* Health checks
* Draining

### Part 2 — NLB

We'll then say:

> "Now let's put these same servers behind an NLB and see how Layer 4 behaves."

---

# 🏗️ Our Final Architecture

By the end, think of it like this:

```text
                         👩‍💻 USER
                            |
                            v
                    🧑‍💼 ALB
                   /    |    \
                  /     |     \
                 v      v      v
             🔵 Blue  🟢 Green
                🖥️      🖥️


Later:

                         👩‍💻 USER
                            |
                            v
                       🚦 NLB
                            |
                     ┌──────┴──────┐
                     v             v
                  🔵 Blue       🟢 Green
                    🖥️             🖥️
```

---

# STEP 1️⃣ — Create Security Groups

Before building anything, AWS asks:

> "Who is allowed to talk to whom?"

Think of Security Groups as **school security guards**.

---

## 🧑‍💼 ALB Security Group

Name:

```text
cloudadhar-day10-alb-sg
```

We allow:

```text
Internet
   |
   | HTTP 80
   v
🧑‍💼 ALB
```

For this classroom lab:

```text
HTTP 80 from 0.0.0.0/0
```

That means:

> Anyone on the internet can reach the ALB on port 80.

⚠️ In production, you'd normally use HTTPS 443 and redirect HTTP → HTTPS.

---

# 🚦 NLB Security Group

Name:

```text
cloudadhar-day10-nlb-sg
```

Allow:

```text
TCP 80
```

from the clients you intend to test.

---

# 🖥️ Web Security Group

Name:

```text
cloudadhar-day10-web-sg
```

This is VERY important.

We don't want random people on the internet directly talking to our servers.

Instead:

```text
Internet
   |
   v
🧑‍💼 ALB
   |
   v
🖥️ EC2
```

So the EC2 security group should allow:

```text
HTTP 80
Source = ALB Security Group
```

And because we're also going to test NLB:

```text
HTTP 80
Source = NLB Security Group
```

So:

```text
               Internet
                  |
                  v
               🧑‍💼 ALB
                  |
                  | 80
                  v
               🖥️ EC2
                  ^
                  | 80
                  |
               🚦 NLB
```

### 🧠 Remember

Don't think:

> "Allow HTTP from everyone."

Think:

> **"Allow HTTP from my load balancers."**

That's safer.

---

# STEP 2️⃣ — Create Blue and Green EC2

Now create two EC2 instances.

```text
🔵 cloudadhar-day10-blue-ec2

🟢 cloudadhar-day10-green-ec2
```

Put them in **different Availability Zones**.

For example:

```text
Region: ap-south-1

AZ-A                 AZ-B
 |                    |
 v                    v
🔵 Blue              🟢 Green
 EC2                  EC2
```

Why?

Because if one AZ has a problem, the other AZ can still work.

That's the whole idea behind **high availability**.

---

# 🖥️ What Do These EC2 Machines Do?

Very simple.

Both run:

> **nginx**

But they show different pages.

Blue says:

```text
🔵 BLUE VERSION
CloudAdhar Day 10
Instance ID: ...
Availability Zone: ...
```

Green says:

```text
🟢 GREEN VERSION
CloudAdhar Day 10
Instance ID: ...
Availability Zone: ...
```

This is clever.

Why?

Because when you see:

```text
BLUE VERSION
```

you know:

> "My request reached Blue."

And when you see:

```text
GREEN VERSION
```

you know:

> "My request reached Green."

---

# 🔐 Why Does the Script Use IMDSv2?

Your User Data script asks AWS:

> "Hey EC2, what's your instance ID?"

and:

> "Which Availability Zone are you in?"

It gets that information from:

**Instance Metadata Service.**

But your lab requires:

> **IMDSv2**

So the script first gets a token.

Don't worry about the long command.

Conceptually:

```text
EC2
 |
 | "Give me a metadata token"
 v
IMDSv2
 |
 v
Token
 |
 v
Instance ID + AZ
```

So your webpage can display:

```text
Instance ID: i-xxxxxxxx
Availability Zone: ap-south-1a
```

---

# ❤️ STEP 3 — Create `/health.html`

Your nginx server has:

```text
/health.html
```

which simply says:

```text
healthy
```

Why?

Because ALB needs to regularly ask:

> "Are you alive?"

It calls:

```text
http://server/health.html
```

If it gets:

```text
HTTP 200
```

ALB says:

> ❤️ "Healthy!"

If it fails:

> 💀 "Unhealthy!"

---

# 🧪 STEP 4 — Test Both EC2s BEFORE ALB

This is important.

Don't immediately create the ALB.

First prove:

```text
🔵 Blue works
🟢 Green works
```

Check:

```text
nginx running?
```

Then:

```text
curl http://localhost/
```

Then:

```text
curl http://localhost/health.html
```

You want:

```text
healthy
```

on both.

### Why?

Because if ALB doesn't work later, you'll know:

> "The EC2 was already working. The problem must be somewhere in the load balancer configuration."

That's troubleshooting.

---

# STEP 5️⃣ — Create Target Groups

Now we need to tell ALB:

> "Here are the servers you are allowed to send traffic to."

A **Target Group** is basically a **list of servers**.

Create:

```text
🔵 cloudadhar-day10-blue-tg
```

Contains:

```text
🔵 Blue EC2
```

And:

```text
🟢 cloudadhar-day10-green-tg
```

Contains:

```text
🟢 Green EC2
```

Like this:

```text
Blue Target Group
       |
       v
   🔵 Blue EC2


Green Target Group
       |
       v
   🟢 Green EC2
```

---

# ❤️ Target Group Health Check

Tell the target group:

```text
Protocol: HTTP
Port: 80
Health path: /health.html
Success code: 200
```

So AWS repeatedly checks:

```text
ALB
 |
 | "Are you healthy?"
 v
Blue
 |
 | HTTP 200
 v
❤️ Healthy
```

Same for Green.

Wait until:

```text
🔵 Blue     Healthy
🟢 Green    Healthy
```

---

# STEP 6️⃣ — Create the ALB

Now we create:

```text
cloudadhar-day10-alb
```

Choose:

```text
Internet-facing
IPv4
```

Put it in two AZs.

```text
             Internet
                 |
                 v
          🧑‍💼 ALB
          /       \
       AZ-A       AZ-B
        |           |
        v           v
     🔵 Blue     🟢 Green
```

Attach:

```text
cloudadhar-day10-alb-sg
```

---

# STEP 7️⃣ — ALB Listener

A listener is basically:

> **"What door should the ALB listen on?"**

We say:

```text
HTTP
Port 80
```

Then initially:

```text
HTTP :80
   |
   v
Blue Target Group
```

So when someone visits:

```text
http://ALB-DNS-NAME/
```

they should see:

```text
🔵 BLUE VERSION
```

---

# 🎯 STEP 8 — Now We Teach ALB Rules

This is where the fun begins.

We tell ALB:

> "If the request looks like THIS, send it THERE."

Your rules are:

```text
Priority 5
Host = api.cloudadhar.local
        ↓
      GREEN


Priority 10
Path = /app1/*
        ↓
       BLUE


Priority 20
Path = /app2/*
        ↓
      GREEN


Priority 30
Path = /release/*
        ↓
Blue 80%
Green 20%


Default
        ↓
      BLUE
```

---

# 🚦 Very Important: Priority

ALB checks rules from the **smallest priority number first**.

```text
5
↓
10
↓
20
↓
30
↓
Default
```

And:

> **First matching rule wins.**

Imagine a teacher checking students:

```text
Student comes in
      |
      v
Check Rule 5
      |
   Match?
   /   \
 Yes    No
 |       |
Send     Check 10
```

Once it matches:

> **STOP!**

It doesn't continue checking the remaining rules.

---

# 🌐 STEP 9 — Host-Based Routing

Suppose you send:

```text
curl -H "Host: api.cloudadhar.local" http://ALB-DNS-NAME/
```

The ALB looks at:

```text
Host = api.cloudadhar.local
```

It says:

> "Ah! I know this visitor."

Rule 5:

```text
api.cloudadhar.local
        ↓
      GREEN
```

So:

```text
User
 |
 v
ALB
 |
 | Host = api.cloudadhar.local
 v
🟢 Green
```

You should see:

```text
GREEN VERSION
```

---

# 📁 STEP 10 — Path-Based Routing

Now:

```text
http://ALB-DNS-NAME/app1/
```

ALB looks at:

```text
/app1/
```

Matches:

```text
/app1/*
```

So:

```text
/app1/*
    |
    v
🔵 Blue
```

You see:

```text
BLUE VERSION
```

---

Now:

```text
http://ALB-DNS-NAME/app2/
```

Matches:

```text
/app2/*
```

So:

```text
/app2/*
    |
    v
🟢 Green
```

You see:

```text
GREEN VERSION
```

---

# 🧠 ALB Is Like a Smart Receptionist

This is the key idea.

```text
User says:

"I want /app1/"
        |
        v
🧑‍💼 ALB
        |
        v
"Oh, /app1 goes to Blue."
        |
        v
🔵 Blue
```

ALB can understand **HTTP information**.

That's why we call it:

> **Layer 7 Load Balancer**

---

# 🎨 STEP 11 — Blue/Green Weighted Release

Now imagine Green is a **new version**.

You don't want to send everyone there immediately.

You say:

> "Let's test Green with only 20% of users."

So:

```text
/release/*

🔵 Blue  = 80%
🟢 Green = 20%
```

Like a teacher choosing students:

```text
100 visitors

80 → 🔵 Blue
20 → 🟢 Green
```

But here's something important:

### It won't necessarily be exactly 80 and 20.

If you test only 50 requests, you might get:

```text
Blue  = 41
Green = 9
```

or:

```text
Blue  = 37
Green = 13
```

That's okay.

It's a **distribution**, not a promise that every 5 requests will be exactly 4 Blue + 1 Green.

---

# 🧪 Why Run 50 Requests?

Because one request tells you almost nothing.

You run:

```text
50 requests
```

Then count:

```text
BLUE VERSION
GREEN VERSION
```

You should see something roughly around:

```text
Blue  ≈ 80%
Green ≈ 20%
```

Not necessarily exactly.

---

# 🍪 STEP 12 — Stickiness

Now we add cookies.

Imagine you walk into the school.

The receptionist gives you a little sticker:

```text
🍪 Cookie
```

It basically helps the ALB remember your selection.

You get:

```text
Request 1 → Green
Request 2 → Green
Request 3 → Green
Request 4 → Green
```

Instead of being randomly redistributed each time.

Your curl command stores the cookie:

```text
cloudadhar-cookies.txt
```

So:

```text
Request 1
   ↓
ALB
   ↓
🟢 Green
   ↓
🍪 Cookie
```

Next request:

```text
🍪 Cookie
   ↓
ALB
   ↓
🟢 Green
```

That's **stickiness**.

---

# ⚠️ Important Difference

There are two concepts.

### Target-group stickiness

```text
User
 ↓
ALB
 ↓
Blue Target Group
```

The user stays with that target group.

### Target stickiness

Inside a target group, the user may stay with the same specific server.

For this lab, you're demonstrating **target-group stickiness** on the weighted action.

---

# STEP 13️⃣ — Health Check Experiment

Now we're going to break Green deliberately.

😈

Stop nginx on Green.

```text
🟢 Green EC2
     |
     X
   nginx stopped
```

ALB checks:

```text
/health.html
```

Green doesn't respond correctly.

ALB eventually says:

```text
🟢 Green → Unhealthy
```

---

# What Happens to `/app2/`?

Remember:

```text
/app2/*
   ↓
Green
```

But Green is unhealthy.

So:

```text
User
 |
 v
ALB
 |
 | /app2/
 v
Green Target Group
 |
 X
No healthy target
```

The request cannot successfully reach a healthy backend.

This demonstrates why **health checks matter**.

---

# 🔄 Restart Green

Start nginx again.

ALB checks:

```text
/health.html
```

Eventually:

```text
Initial
   ↓
Healthy
```

So Green is back.

🎉

---

# 🚪 STEP 14 — Connection Draining

Now let's pretend Blue needs maintenance.

We don't want:

```text
User downloading file
          |
          v
       🔵 Blue
          |
          X
      SERVER GONE
```

That would be rude. 😄

Instead we tell ALB:

> "Remove Blue, but let current connections finish."

Set:

```text
Deregistration delay = 30 seconds
```

---

# 🐢 Start Slow Download

Your file is:

```text
20 MB
```

And you limit download speed:

```text
200 KB/s
```

So it takes long enough to observe what happens.

While download is happening:

```text
User
 |
 v
ALB
 |
 v
🔵 Blue
 |
 | large file
 v
🐢 slowly downloading
```

Now deregister Blue.

ALB says:

> "No new customers go to Blue."

But the existing download gets time to finish.

---

# 🔄 Blue Target State

You'll observe something like:

```text
Healthy
   ↓
Draining
   ↓
Unused
```

### Healthy

> "I can receive new requests."

### Draining

> "Don't send new requests, but existing connections can finish."

### Unused

> "I'm no longer being used by this target group."

That's connection draining.

---

# 🚦 STEP 15 — Now Build NLB

Now we say:

> "Okay ALB, you've shown us your smart HTTP skills."

Now let's create:

```text
🚦 NLB
```

Name:

```text
cloudadhar-day10-nlb
```

---

# 🧠 Remember the Difference

ALB:

```text
🧑‍💼
"I understand your web request."
```

NLB:

```text
🚦
"I mainly care about the network connection."
```

---

# STEP 16️⃣ — NLB Target Group

Create:

```text
cloudadhar-day10-nlb-tg
```

Targets:

```text
🔵 Blue
🟢 Green
```

Protocol:

```text
TCP
```

Port:

```text
80
```

Notice something interesting:

### Traffic protocol

```text
TCP
```

### Health check

```text
HTTP /health.html
```

That's okay.

The NLB forwards TCP traffic, while the health check can use HTTP.

---

# STEP 17️⃣ — Create NLB

Create:

```text
cloudadhar-day10-nlb
```

Internet-facing.

IPv4.

Two AZs.

```text
             Internet
                 |
                 v
              🚦 NLB
             /     \
            v       v
        🔵 Blue   🟢 Green
          EC2       EC2
```

Attach:

```text
cloudadhar-day10-nlb-sg
```

Listener:

```text
TCP :80
```

Forward to:

```text
cloudadhar-day10-nlb-tg
```

---

# 🧪 STEP 18 — Test NLB

Find the NLB DNS name.

Then:

```text
curl http://NLB-DNS-NAME/
```

You might get:

```text
BLUE VERSION
```

Then another connection might get:

```text
GREEN VERSION
```

But don't expect:

```text
Blue
Green
Blue
Green
Blue
Green
```

❌ Not guaranteed.

---

# 🤔 Why Doesn't NLB Alternate Perfectly?

Because NLB works using **flow hashing**.

Think of a traffic police officer.

They don't say:

> "Car 1 → Blue, Car 2 → Green, Car 3 → Blue..."

Instead, traffic flows are distributed based on connection information.

Also, if you keep reusing the same connection, it can continue going to the same target.

So:

```text
Connection A
      ↓
   🔵 Blue

Connection B
      ↓
   🟢 Green
```

Your repeated curl commands don't necessarily represent completely independent flows in the way you might imagine.

---

# 📍 NLB Static IPs

Another important NLB feature:

Each enabled AZ can have a stable IP.

Think:

```text
AZ-A             AZ-B
 |                 |
IP-A              IP-B
 |                 |
 └────── NLB ──────┘
```

An internet-facing NLB can also use an **Elastic IP per AZ** when created.

This is useful when someone says:

> "Our firewall allowlist needs fixed IP addresses."

Think:

# 🚦 NLB = Static IP

---

# 🧠 Now the BIG Comparison

Imagine three workers.

## 🧑‍💼 ALB

Smart receptionist:

> "What website are you asking for?"

Can understand:

```text
Host
Path
HTTP headers
Query
HTTP/HTTPS
```

Therefore:

**Layer 7**

---

## 🚦 NLB

Traffic officer:

> "Where should this network connection go?"

Works with:

```text
TCP
UDP
TLS
```

Therefore:

**Layer 4**

And remember:

**Static IP**

---

## 🛡️ GWLB

Security checkpoint:

> "Send this traffic through my firewall/security appliance."

Used for:

```text
Firewall
IDS
IPS
Deep inspection
```

Uses:

```text
GENEVE
UDP 6081
```

---

# 🎯 Your Day 10 Exam Cheat Sheet

When you see:

```text
HTTP path routing
```

👉 **ALB**

```text
Host header routing
```

👉 **ALB**

```text
Blue/Green 80/20 HTTP
```

👉 **ALB**

```text
Cookie stickiness
```

👉 **ALB**

```text
Graceful removal
```

👉 **Deregistration delay**

```text
TCP
```

👉 **NLB**

```text
UDP
```

👉 **NLB**

```text
Static public IP
```

👉 **NLB**

```text
TLS pass-through
```

👉 **NLB TCP 443**

```text
Firewall / IDS / IPS
```

👉 **GWLB**

```text
GENEVE UDP 6081
```

👉 **GWLB**

---

# 🗺️ Your Day 10 Lab Journey

This is the sequence I want you to follow:

```text
1️⃣ Create Security Groups
        ↓
2️⃣ Create Blue EC2
        ↓
3️⃣ Create Green EC2
        ↓
4️⃣ Verify nginx on both
        ↓
5️⃣ Verify /health.html
        ↓
6️⃣ Create Blue Target Group
        ↓
7️⃣ Create Green Target Group
        ↓
8️⃣ Wait for Healthy
        ↓
9️⃣ Create ALB
        ↓
🔟 Default → Blue
        ↓
1️⃣1️⃣ Test Blue
        ↓
1️⃣2️⃣ Host rule → Green
        ↓
1️⃣3️⃣ /app1 → Blue
        ↓
1️⃣4️⃣ /app2 → Green
        ↓
1️⃣5️⃣ /release → 80/20
        ↓
1️⃣6️⃣ Test 50 requests
        ↓
1️⃣7️⃣ Enable stickiness
        ↓
1️⃣8️⃣ Test cookie
        ↓
1️⃣9️⃣ Stop Green nginx
        ↓
2️⃣0️⃣ Observe Unhealthy
        ↓
2️⃣1️⃣ Restart Green
        ↓
2️⃣2️⃣ Observe Healthy
        ↓
2️⃣3️⃣ Test Blue draining
        ↓
2️⃣4️⃣ Create NLB target group
        ↓
2️⃣5️⃣ Create NLB
        ↓
2️⃣6️⃣ Test TCP 80
        ↓
2️⃣7️⃣ Record NLB IPs
        ↓
2️⃣8️⃣ Review ALB vs NLB vs GWLB
```

# ⭐ The MOST Important Story

If you forget everything else, remember this:

```text
                 USER
                   |
                   v
          🧑‍💼 ALB = SMART
                   |
          "What did you request?"
             /     |      \
            /      |       \
       /app1     /app2    /release
          |         |          |
          v         v          v
        🔵 Blue   🟢 Green   🔵80/🟢20
```

Then:

```text
                 USER
                   |
                   v
              🚦 NLB = FAST
                   |
             "Network traffic?"
              /          \
             v            v
          🔵 Blue       🟢 Green
```

And:

```text
                 TRAFFIC
                    |
                    v
               🛡️ GWLB
                    |
             Security Appliance
                    |
                    v
                Destination
```

### 🧠 One sentence to memorize:

> **ALB decides based on the web request, NLB distributes network connections, and GWLB sends traffic through security appliances.**

That is the heart of your **Day 10 lab + SAA-C03 exam questions**.
