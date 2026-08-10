# Elastic Load Balancing - ALB, NLB, and GWLB

## Selection First

| Hard requirement | Select | Reason |
|---|---|---|
| HTTP/HTTPS host, path, header, query, redirect, authentication, or WAF | ALB | Layer 7 listener rules understand HTTP |
| TCP, TLS, UDP, static zonal IP, optional EIP, or extreme performance | NLB | Layer 4 flow load balancing |
| Transparent firewall, IDS, IPS, or deep-packet inspection | GWLB | Inserts compatible appliances through GENEVE |

ALB is an HTTP-aware receptionist, NLB is a Layer 4 junction, and GWLB is a
transparent security checkpoint. Start with protocol and hard requirements,
then consider health, target type, AZ design, observability, and cost.

## Application Load Balancer

An ALB has nodes in enabled subnets, listeners, ordered rules, target groups,
and health checks. Non-default rules run from the lowest priority number upward;
the first match wins. The default action runs only when none match.

| Condition or action | Example or purpose |
|---|---|
| Host header | `api.cloudadhar.local` |
| Path pattern | `/app1/*` |
| HTTP header or query | Route beta/version traffic |
| Source IP | Match an intended CIDR |
| Forward | Send to one or more target groups |
| Redirect | Commonly HTTP to HTTPS |
| Fixed response | Return a response without a backend |
| Authenticate | OIDC or Cognito on supported HTTPS listeners |

Use HTTPS with ACM in production. Allow only listener ports from intended
clients, and allow the backend port from the ALB Security Group only. Enable at
least two AZs, keep target AZ participation aligned, use a lightweight health
endpoint, and monitor metrics and logs. Associate AWS WAF when Layer 7 attack
filtering is required.

## Weighted Releases and Stickiness

ALB can forward to multiple target groups with relative weights from `0` to
`999`. Move from Blue to Green gradually, monitor health, errors, latency, and
business metrics, and keep rollback ready. A small sample will not exactly
match the configured percentage. An empty or unhealthy weighted target group
does not automatically donate its weight to another group.

Prefer stateless applications or an external session store. Target-group
stickiness keeps a client on its selected weighted group; target stickiness
keeps it on a target within a group. Enable affinity only when required, use the
shortest useful duration, and test unhealthy-target behavior.

## Health and Draining

`Initial` means checks are running, `Unhealthy` means checks failed, `Unused`
often indicates an AZ or listener association problem, and `Draining` means
deregistration delay is active. During draining, the load balancer sends no new
requests to the target while existing connections may finish. Set the delay
from real request duration rather than using one value for every workload.

## Network Load Balancer

NLB supports Layer 4 protocols and static IP per enabled AZ; an internet-facing
NLB can receive an EIP per AZ during creation. Depending on current Regional
support and configuration, listener choices include TCP, TLS, UDP, TCP_UDP,
QUIC, and TCP_QUIC. A TLS listener terminates TLS, while a TCP `443` listener
passes encrypted bytes to a backend that terminates TLS. Cross-zone behavior,
client-IP preservation, and health-check support depend on configuration and
target type.

Attach the intended Security Group when creating the NLB. If an NLB is created
without Security Groups, they cannot be added later. Reference the NLB Security
Group from the backend Security Group.

NLB does not inspect paths or Host headers. Use a real UDP service and client to
test UDP; HTTP `curl` is not a UDP test.

## Gateway Load Balancer

GWLB distributes flows to compatible virtual appliances using GENEVE on UDP
`6081`. A consumer route points to a GWLB endpoint, which reaches the endpoint
service, GWLB, and appliance fleet. Design symmetric forward and return paths,
use multiple AZs and health checks, and understand stateful appliance failover.
Do not use a normal nginx instance as a fake security appliance.

## Exam Cues

| Requirement | Best direction |
|---|---|
| Path or host routing | ALB |
| Static public IP allowlist | NLB with EIP per AZ |
| UDP application | NLB |
| Web application firewall | ALB or CloudFront with AWS WAF |
| TLS pass-through | NLB TCP `443` |
| Third-party firewall fleet | GWLB |
| Blue/Green HTTP percentage | ALB weighted target groups |
| Graceful target removal | Deregistration delay |

## Official References

- [Elastic Load Balancing](https://docs.aws.amazon.com/elasticloadbalancing/latest/userguide/what-is-load-balancing.html)
- [Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html)
- [ALB listener rules](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-listeners.html)
- [ALB health checks](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html)
- [Network Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/introduction.html)
- [NLB Security Groups](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/load-balancer-security-groups.html)
- [Gateway Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/gateway/introduction.html)
