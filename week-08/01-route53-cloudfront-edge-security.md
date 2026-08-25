# Route 53, CloudFront, and Edge Security

Day 15 follows a request from DNS resolution to the edge and then to a private
origin. Each layer solves a different problem: Route 53 selects an endpoint,
CloudFront delivers and caches content, OAC authorizes origin access, ACM
provides the viewer certificate, and WAF inspects HTTP requests.

## DNS Records

| Record | Use |
|---|---|
| `A` / `AAAA` | Name to IPv4 / IPv6 address |
| `CNAME` | One hostname to another; not normally at the zone apex |
| Alias | Route 53 name to a supported AWS target; works at the apex |
| `MX` | Mail routing |
| `TXT` | Verification and policy text such as SPF |
| `NS` | Authoritative name servers or subdomain delegation |
| `CAA` | Restrict which certificate authorities may issue certificates |

An ACM DNS-validation record is a random-token `CNAME`. It proves domain
control and supports managed renewal. The application record, such as `cdn`,
is a separate alias or `CNAME` that directs viewers to CloudFront.

## Route 53 Routing Policies

| Requirement | Policy |
|---|---|
| One ordinary answer | Simple |
| Controlled traffic percentage or canary | Weighted |
| Lowest measured AWS network latency | Latency |
| Active-passive recovery | Failover |
| Route by viewer country/continent | Geolocation |
| Route by coordinates, bias, and optionally traffic flow | Geoproximity |
| Route by client CIDR | IP-based |
| Several healthy answers | Multivalue answer |

DNS failover is not instantaneous. Health-check intervals, failure thresholds,
record TTLs, recursive resolvers, and client caches all affect observed RTO.
Querying an authoritative name server proves Route 53's current answer without
waiting for a recursive resolver's cached answer to expire.

## CloudFront Private S3 Origin

```text
Viewer --HTTPS--> CloudFront --signed origin request (OAC)--> private S3
                         |
                         `--> AWS WAF
```

Keep S3 Block Public Access enabled. Origin Access Control signs CloudFront's
requests with SigV4, and the bucket policy grants `s3:GetObject` only to the
specific distribution ARN. Direct S3 access should fail while the CloudFront
URL succeeds.

Use a managed cache policy unless the application needs a deliberate custom
key. Forwarding unnecessary cookies, headers, or query strings reduces the
cache-hit ratio. An invalidation removes selected paths from edge caches but
is not a substitute for sensible versioned object names and TTLs.

## Private Content

A trusted key group contains CloudFront public keys. The signer retains the
private key and creates a time-limited signed URL or signed cookies.

- Signed URL: one file or a small number of explicit resources.
- Signed cookies: access to several restricted files without changing every URL.
- OAC: protects CloudFront-to-S3 access; it does not authorize individual users.

Never upload or commit the private signing key. Rotate keys by overlapping old
and new public keys before removing the old one.

## ACM and CloudFront

CloudFront viewer certificates are a special Regional exception: request or
import the certificate in ACM `us-east-1`, even when the origin is elsewhere.
The certificate must cover every alternate domain name attached to the
distribution. For DNS validation:

1. Request the public certificate in `us-east-1`.
2. Copy the exact ACM validation `CNAME` name and value into authoritative DNS.
3. Wait for status `Issued` and keep the validation record for renewal.
4. Add the alternate domain and issued certificate to CloudFront.
5. Create the separate application DNS record pointing to CloudFront.

## WAF, Shield, and Global Accelerator

Start WAF rules in Count mode, inspect sampled requests and metrics, then move
to Block only after validating the match scope. A CloudFront-scoped web ACL is
global and is managed through the CloudFront scope.

Shield Standard is automatically included for supported AWS resources. Shield
Advanced adds paid capabilities and should not be enabled for this lab.

| Need | Direction |
|---|---|
| Cacheable HTTP content and edge functions | CloudFront |
| Static anycast IPs for TCP/UDP or HTTP, endpoint health routing | Global Accelerator |
| DNS policy and health-based answers | Route 53 |
| Layer 7 request filtering | AWS WAF |

## Exam Cues

- Private S3 content globally -> CloudFront + OAC + restrictive bucket policy
- Custom CloudFront HTTPS name -> ACM certificate in `us-east-1`
- Canary percentage -> weighted routing
- Primary/secondary endpoint -> failover records plus health check
- Country-specific content -> geolocation routing
- Protect many restricted files -> signed cookies
- Inspect web requests -> WAF

## Official AWS References

- [Route 53 routing policies](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy.html)
- [Route 53 health checks and failover](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-failover.html)
- [Restricting S3 access with OAC](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html)
- [CloudFront cache behavior](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/DownloadDistValuesCacheBehavior.html)
- [CloudFront private content](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/PrivateContent.html)
- [CloudFront certificate requirements](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cnames-and-https-requirements.html)
- [ACM DNS validation](https://docs.aws.amazon.com/acm/latest/userguide/dns-validation.html)
- [AWS WAF with CloudFront](https://docs.aws.amazon.com/waf/latest/developerguide/cloudfront-features.html)
