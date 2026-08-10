# EC2 Fundamentals and Pricing

Choose EC2 capacity only after identifying the workload requirements.

## Instance Selection

| Workload signal | Family pattern | Typical use |
|---|---|---|
| Balanced CPU and memory | General purpose (`T`, `M`) | Web and application servers |
| Sustained CPU | Compute optimized (`C`) | Batch, encoding, compute services |
| Large memory | Memory optimized (`R`, `X`) | Caches and in-memory databases |
| High local storage or I/O | Storage optimized (`I`, `D`) | Search and data processing |
| GPU or accelerator | Accelerated (`P`, `G`, `Inf`, `Trn`) | ML, graphics, inference |

Check vCPU architecture, memory, network bandwidth, EBS bandwidth, local
storage, accelerator, operating-system, and software requirements. Burstable
`T` instances fit low-baseline workloads with occasional CPU bursts, not
continuous heavy CPU.

## AMIs and Golden Images

An AMI is a Regional launch image containing an operating-system baseline,
block-device mappings, and related launch configuration.

| Type | Owner | Best use |
|---|---|---|
| AWS AMI | AWS | Supported operating-system baseline |
| Marketplace AMI | Vendor | Licensed appliance or packaged software |
| Custom AMI | Your account | Reusable configured server |
| Golden AMI | Approved process | Patched, hardened, tested baseline |

A Golden AMI must be approved, versioned, tested, and governed. Do not bake
credentials, private keys, logs, or host-specific data into it.

Mutable patching changes running servers and can cause drift. Immutable
patching builds a new image, tests it, updates the launch configuration, and
replaces old instances. EC2 Image Builder automates image build, validation,
test, and distribution.

## User Data, Launch Templates, and IMDSv2

Linux User Data is normally processed by `cloud-init` on first boot and runs as
root. Use it for small repeatable bootstrap tasks, not secrets.

A Launch Template is a versioned launch configuration containing settings such
as AMI, instance type, role, security groups, storage, metadata options, tags,
and User Data.

The Instance Metadata Service is available inside EC2 at `169.254.169.254`.
IMDSv2 requires a session token. Set metadata to **V2 only (token required)**.
A tokenless `401 Unauthorized` response is useful expected-deny evidence.
Never publish metadata tokens or role credentials.

## Pricing Decisions

| Option | Best signal | Interruption |
|---|---|---:|
| On-Demand | Unknown or short-term usage | No |
| Reserved Instance | Steady matching EC2 usage | No |
| Savings Plans | Steady compute spend with flexibility | No |
| Spot | Fault-tolerant, flexible work | Yes |
| Dedicated Instance | Single-tenant instance requirement | No |
| Dedicated Host | Host visibility or server-bound licensing | No |

Reserved Instances and Savings Plans are billing discounts, not server
objects. Spot workloads must support interruption, checkpointing, retries, and
graceful termination.

## Exam Cues

- Repeatable approved baseline -> Golden AMI
- Automated image pipeline -> EC2 Image Builder
- First-boot setup -> User Data
- Versioned launch settings -> Launch Template
- Token-required metadata -> IMDSv2
- Unknown demand -> On-Demand
- Steady compute spend -> Savings Plans
- Interruptible batch -> Spot
- Server-bound licensing -> Dedicated Host

Answer decisions as `requirement -> choice -> reason`.

## Official References

- [AMIs](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AMIs.html)
- [EC2 Image Builder](https://docs.aws.amazon.com/imagebuilder/latest/userguide/what-is-image-builder.html)
- [User Data](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html)
- [Instance Metadata Service](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html)
- [EC2 purchasing options](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-purchasing-options.html)
