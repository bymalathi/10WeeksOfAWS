# 🌟 Day 8 — AWS Storage

First, imagine an **EC2 instance is your computer**.

Your computer needs somewhere to keep things.

AWS gives us different storage choices:

```text
EC2 Computer 🖥️
      |
      +---- EBS 💽  → Hard disk
      |
      +---- EFS 📁  → Shared folder
      |
      +---- Instance Store ⚡ → Temporary local storage
```

And we also learn:

```text
Snapshot 📸       → Backup
DLM 🤖            → Automatic backup
Multi-Attach 👥   → Same disk attached to multiple EC2s
Placement Groups 🪑 → Where EC2s are placed
```

---

# 1️⃣ EBS — Your EC2's Hard Disk 💽

Imagine you have a laptop.

Inside it is a hard disk:

```text
🖥️ Laptop
   |
   💽 Hard Disk
```

You save:

* photos
* games
* documents
* applications

**EBS is like that hard disk for EC2.**

```text
🖥️ EC2
  |
  💽 EBS
```

So remember:

> **EBS = hard disk for EC2**

---

# 2️⃣ Why do we need EBS?

When you launch EC2, it needs storage for its operating system.

For example:

```text
EC2
 |
 └── 💽 Root EBS
       |
       ├── Linux
       ├── Applications
       └── Files
```

You can also attach another EBS volume for your application data.

```text
        EC2
         |
   ┌─────┴─────┐
   ↓           ↓
💽 Root      💽 Data
```

---

# 3️⃣ EBS is tied to an Availability Zone

This is important.

Imagine Mumbai has:

```text
Mumbai Region
│
├── AZ-1
│    └── EC2
│         └── EBS
│
└── AZ-2
     └── EC2
```

The EBS volume is in **AZ-1**.

Normally, you cannot attach that EBS volume directly to an EC2 in AZ-2.

So remember:

> **EBS = Availability Zone scoped**

Very simple:

**EBS stays in one AZ.**

---

# 4️⃣ EBS Volume Types

You don't need to panic about these names.

Think of different types of hard disks.

## 🟢 gp3

This is your **normal everyday SSD**.

Use it for:

* EC2 boot disk
* normal applications
* general-purpose workloads

Remember:

> **gp3 = normal/general purpose**

---

## 🔴 io2

Imagine a bank database.

It needs very fast disk operations.

```text
Customer → Database
Customer → Database
Customer → Database
Customer → Database
```

It needs lots of IOPS.

**IOPS = how many input/output operations the disk can perform per second.**

So:

> **io2 = high IOPS / critical databases**

---

## 🟤 st1

Imagine you have a HUGE amount of data and usually read it continuously.

For example:

```text
BIG FILE
████████████████████████████
→ → → → → → → → → → → →
```

That's sequential data.

> **st1 = frequently accessed large sequential data**

---

## ⚫ sc1

Same idea, but the data is rarely accessed.

Think:

```text
Old files
Old files
Old files
```

> **sc1 = cold/infrequently accessed sequential data**

And remember:

> ❌ st1 and sc1 cannot be boot volumes.

---

# 🧠 EBS Type Memory

```text
gp3 → General purpose
io2 → High IOPS
st1 → Sequential + frequently used
sc1 → Sequential + cold
```

That's enough for now.

---

# 5️⃣ EBS Snapshot 📸

Imagine you have your hard disk:

```text
💽 EBS

📄 file1
📄 file2
📄 file3
```

You take a photograph of it:

```text
        📸
      Snapshot
```

That is basically the idea of an **EBS snapshot**.

> **Snapshot = point-in-time backup of an EBS volume**

---

# 6️⃣ Why is it called point-in-time?

Suppose:

### 10 AM

```text
💽 EBS

file1
file2
Version 1
```

You take a snapshot:

```text
📸 Snapshot
```

### 11 AM

You change the original:

```text
💽 EBS

file1
file2
Version 2
new-file
```

The snapshot still remembers the **10 AM version**.

So:

```text
Snapshot
   ↓
"Show me what the disk looked like at 10 AM."
```

That's **point-in-time**.

---

# 7️⃣ Can I directly attach a Snapshot to EC2?

❌ No.

A snapshot is a backup.

You first create a new EBS volume.

```text
📸 Snapshot
     |
     ↓
💽 New EBS Volume
     |
     ↓
🖥️ EC2
```

Remember:

> **Snapshot → Volume → EC2**

---

# 8️⃣ Cross-Region Snapshot

Suppose your EC2 is in Mumbai.

```text
🇮🇳 Mumbai
   |
   💽 EBS
   |
   📸 Snapshot
```

What if Mumbai has a disaster?

You can copy the snapshot to another Region.

```text
🇮🇳 Mumbai
   |
   📸 Snapshot
       |
       | Copy
       ↓
🇦🇺 Sydney
   |
   📸 Snapshot Copy
```

Then in Sydney:

```text
Snapshot
   ↓
New EBS
   ↓
EC2
```

So remember:

> **EBS itself doesn't move between Regions. Copy the snapshot.**

---

# 9️⃣ Encryption 🔐

Imagine your diary.

You don't want everyone reading it.

So you lock it.

EBS encryption does something similar.

```text
💽 EBS
 🔐
```

The encryption uses **AWS KMS**.

Important relationship:

```text
Encrypted EBS
      ↓
Encrypted Snapshot
      ↓
Encrypted restored EBS
```

Also:

> An existing unencrypted EBS volume cannot simply be switched to encrypted in place.

You create an encrypted copy/restore path.

---

# 🔟 EBS Resize

Suppose you have:

```text
💽 EBS
2 GiB
```

You need more space.

You increase it:

```text
💽 EBS
4 GiB
```

But there are **two layers**:

```text
EBS volume
    ↓
Filesystem
    ↓
/data
```

Making the EBS bigger doesn't automatically make the filesystem bigger.

So you:

```text
Increase EBS
     ↓
Linux sees bigger disk
     ↓
Grow filesystem
     ↓
More usable space
```

For your lab, you're using **XFS**.

So the lab uses:

```bash
xfs_growfs /data
```

You don't need to memorize the command yet. Understand the idea:

> **Increase EBS → then grow filesystem**

---

# 1️⃣1️⃣ EFS 📁

Now forget EBS.

Imagine your family has one shared folder:

```text
📁 Family Folder

photos
documents
videos
```

Everyone can access it.

AWS has something similar:

> **EFS = shared file storage**

For example:

```text
🖥️ EC2-1
      \
       \
        📁 EFS
       /
      /
🖥️ EC2-2
```

Both computers can use the same files.

So:

> **EFS = shared folder for multiple Linux EC2 instances**

---

# 1️⃣2️⃣ EBS vs EFS

This is VERY important.

### EBS

```text
🖥️ EC2
  |
  💽 EBS
```

Think:

> **My computer's hard disk**

### EFS

```text
🖥️ EC2-1
      \
       📁 EFS
      /
🖥️ EC2-2
```

Think:

> **Shared network folder**

### Easy memory:

> **EBS = MY disk**

> **EFS = SHARED files**

---

# 1️⃣3️⃣ EFS uses NFS

Don't worry about the technical word.

NFS is the technology that lets Linux computers access files over the network.

The important port is:

> **TCP 2049**

Think:

```text
EC2
 |
 | "Give me my files!"
 | TCP 2049
 ↓
EFS
```

---

# 1️⃣4️⃣ EFS Mount Target 🚪

Think of EFS as a building.

Your EC2 needs an entrance.

That entrance is the:

> **Mount Target**

```text
🖥️ EC2
   |
   ↓
🚪 Mount Target
   |
   ↓
📁 EFS
```

The security group on the mount target should allow:

```text
TCP 2049
```

from the **EC2 security group**.

Not:

```text
0.0.0.0/0 ❌
```

---

# 1️⃣5️⃣ Regional EFS

Normal EFS is Regional.

Think:

```text
             📁 EFS
            /     \
           /       \
        AZ-1       AZ-2
         |           |
        EC2         EC2
```

Multiple AZs can access the same EFS.

That's why the exam may say:

> "Multiple EC2 instances in different AZs need shared files."

Answer:

**EFS**

---

# 1️⃣6️⃣ EFS One Zone

There is also:

> **EFS One Zone**

It keeps the file system in one AZ.

It's cheaper, but it doesn't give you the same multi-AZ storage design as Regional EFS.

For now:

```text
Regional EFS
→ multiple AZ design

One Zone
→ one AZ
→ lower cost
```

---

# 1️⃣7️⃣ DLM 🤖

DLM stands for:

**Data Lifecycle Manager**

Don't worry about the name.

Imagine you tell a robot:

> "Every day, take a backup and keep only the last 7."

```text
🤖 DLM

Every 24 hours
      ↓
📸 Snapshot
      ↓
Keep 7
      ↓
Remove old ones
```

That's basically DLM.

Your lab uses a tag:

```text
Backup=Daily
```

DLM sees:

```text
💽 EBS
Backup=Daily
```

and creates snapshots according to the policy.

Remember:

> **DLM = automatic EBS snapshot management**

---

# 1️⃣8️⃣ Fast Snapshot Restore ⚡

Normally, after restoring from a snapshot, the blocks may initialize as they're accessed.

Imagine:

You have a big box of toys.

You say:

> "I need all my toys RIGHT NOW!"

Fast Snapshot Restore helps prepare the restored volume for fast/full performance.

So:

> **FSR = quickly get full performance from restored EBS volumes**

But:

💰 **It costs extra.**

Exam clue:

> "Need immediate restored-volume performance"

Answer:

**Fast Snapshot Restore**

---

# 1️⃣9️⃣ Multi-Attach 👨‍👩‍👦

Normally:

```text
EC2
 |
💽 EBS
```

Multi-Attach allows compatible EBS volumes to be attached to multiple EC2 instances.

```text
🖥️ EC2-1
     \
      \
       💽 io2
      /
     /
🖥️ EC2-2
```

But there's an important rule:

> **Same AZ**

And another important rule:

> **Applications/filesystems must coordinate writes.**

Imagine two children writing in the same notebook.

```text
👦 writes
👧 writes
💥
```

They need rules.

So:

> **Multi-Attach is NOT the same thing as EFS.**

EFS is designed for shared **files**.

Multi-Attach is shared **block storage** and needs coordination.

---

# 2️⃣0️⃣ Instance Store ⚡

Now imagine you have a temporary table.

You put some toys on it.

```text
⚡ Temporary table

🧸
🚗
⚽
```

If the table disappears, that's okay.

That's the idea of **Instance Store**.

It is local storage attached to the EC2 host.

Use it for:

* Cache
* Scratch data
* Temporary data
* Reproducible data

Don't use it for:

```text
❌ Only copy of important files
❌ Important permanent database
```

Because data can be lost when the underlying host/storage is lost.

---

# 2️⃣1️⃣ Instance Store vs EBS

Remember this:

```text
EBS
💽
"My important/persistent disk"


Instance Store
⚡
"My temporary local disk"
```

Very simple.

---

# 2️⃣2️⃣ Placement Groups 🪑

Placement Groups are NOT storage.

They answer:

> **"How should AWS place my EC2 instances?"**

There are three.

---

## Cluster 🤝

Keep computers close.

```text
🖥️ 🖥️ 🖥️
```

Why?

They need very fast communication.

Used for:

> HPC / tightly coupled workloads

Remember:

**Cluster = CLOSE**

---

## Spread ↔️

Keep computers apart.

```text
🖥️          🖥️          🖥️
```

Why?

If one physical hardware fails, you want the others separated.

Remember:

**Spread = APART**

---

## Partition 👥

Put computers into separate groups.

```text
Group 1    Group 2    Group 3

🖥️ 🖥️      🖥️ 🖥️      🖥️ 🖥️
```

Useful for:

* Kafka
* Hadoop
* Cassandra

Remember:

**Partition = GROUPS**

---

# 🧠 Your Day 8 Memory Map

This is what I want you to understand:

```text
                    DAY 8
                      |
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
       EBS           EFS       Instance Store
       💽             📁             ⚡
   Hard disk      Shared files   Temporary
        |
        ├── gp3
        ├── io2
        ├── resize
        ├── snapshot
        ├── restore
        ├── encryption
        ├── cross-Region
        ├── DLM
        └── Fast Snapshot Restore

        Multi-Attach
             ↓
      Shared block storage
        Same AZ only
       Coordinated writes

        Placement Groups
             |
       ┌─────┼─────┐
       ↓     ↓     ↓
    Cluster Spread Partition
     CLOSE   APART   GROUPS
```

# ⭐ What YOU should remember for the exam

Don't try to memorize all the lab commands yet.

First make these automatic:

| If you hear...                   | Think...                  |
| -------------------------------- | ------------------------- |
| EC2 hard disk                    | **EBS**                   |
| General purpose SSD              | **gp3**                   |
| High IOPS database               | **io2**                   |
| Sequential frequently accessed   | **st1**                   |
| Sequential cold data             | **sc1**                   |
| EBS backup                       | **Snapshot**              |
| Snapshot to another Region       | **Copy snapshot**         |
| Automatic snapshots              | **DLM**                   |
| Immediate restored performance   | **Fast Snapshot Restore** |
| Shared files                     | **EFS**                   |
| EFS Linux protocol               | **NFS**                   |
| EFS port                         | **2049**                  |
| Temporary local storage          | **Instance Store**        |
| Same block volume, multiple EC2s | **Multi-Attach**          |
| Multi-Attach boundary            | **Same AZ**               |
| HPC / low latency                | **Cluster**               |
| Separate hardware                | **Spread**                |
| Kafka/Hadoop/Cassandra           | **Partition**             |

### ❤️ Most important distinction

If you remember only **three things today**, remember:

> 💽 **EBS = one EC2's persistent hard disk**

> 📁 **EFS = shared files for multiple Linux EC2s**

> ⚡ **Instance Store = temporary local storage**

Everything else in Day 8 builds around these three.
