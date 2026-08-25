# Day 15 Lab - Route 53, CloudFront, ACM, and Edge Security

Build this challenge in your own AWS account from a blank starting point. The
instructor may already have a certificate or domain configuration for the live
demonstration; learners must complete the ACM request and DNS validation steps
below themselves.

Use the AWS Management Console for resource creation. CloudShell is used only
for verification and CloudFront URL signing.

## Before You Begin

You need administrative lab permissions and a public domain or delegated
subdomain whose authoritative DNS you can edit. Replace every placeholder;
never copy an instructor's account ID, domain, IP address, distribution ID, or
certificate.

| Placeholder | Your value |
|---|---|
| `<LEARNER>` | Short lowercase name, for example `sanket` |
| `<PREFIX>` | Unique prefix, for example `sanket-w8` |
| `<ACCOUNT-ID>` | Current AWS account ID |
| `<ROOT-DOMAIN>` | Domain whose DNS you control |
| `<CDN-NAME>` | For example `cdn.<ROOT-DOMAIN>` |
| `<LAB-ZONE>` | For example `lab.<ROOT-DOMAIN>` |
| `<BUCKET>` | Globally unique Day 15 bucket name |

Regions and scope:

| Resource | Location |
|---|---|
| S3 origin and primary EC2 | Mumbai, `ap-south-1` |
| Secondary EC2 | N. Virginia, `us-east-1` |
| CloudFront viewer certificate | ACM `us-east-1`—required |
| CloudFront, Route 53, health checks | Global |
| CloudFront WAF web ACL | CloudFront scope |

Do not use the root user. Route 53 hosted zones and health checks, EC2, public
IPv4, CloudFront, WAF, and data transfer may generate charges.

## Domain Purchase and Learner Naming Plan

The classroom demonstration used an instructor-owned domain. Do not reuse that
domain. Purchase or use a domain that belongs to you and replace every example
below with your values.

You can register a domain through GoDaddy, Hostinger, Namecheap, Cloudflare
Registrar, Route 53, or another reputable registrar. Do not select a registrar
from the introductory price alone. At checkout, compare:

- first-year price and renewal price;
- taxes and mandatory fees;
- WHOIS/privacy protection;
- auto-renewal controls and account MFA;
- whether its authoritative DNS supports `CNAME` records; and
- whether it supports `NS` records at a subdomain, which is required for the
  exact delegated `lab.<ROOT-DOMAIN>` exercise.

Prices and promotions change. Use the live checkout page, remove optional
hosting/email/site-builder products you do not need, and verify the renewal
price before paying. A domain-only purchase is enough; web hosting is not
required for this challenge.

### Purchase checklist

1. Search for a short practice name based on a first name, GitHub username, or
   neutral alias, such as `sanketlab`, `sanketaws`, `aliyaaws`, or
   `devname-w8`.
2. Compare several available top-level domains at the registrar's live checkout.
3. Record the first-year price, renewal price, tax, privacy terms, and minimum
   registration period before choosing.
4. Purchase only the domain unless you independently need hosting or email.
5. Verify the registrant email address and enable MFA on the registrar account.
6. Review auto-renewal and payment settings so expiry is deliberate.
7. Wait until the domain status is Active, then run `dig NS` to identify the
   authoritative DNS provider.
8. Use only a disposable practice domain for nameserver changes. Do not use a
   business, production, or active-email domain.

Official domain search pages: [GoDaddy](https://www.godaddy.com/domains),
[Hostinger](https://www.hostinger.com/domain-name-search),
[Namecheap](https://www.namecheap.com/domains/),
[Cloudflare Registrar](https://www.cloudflare.com/products/registrar/), and
[Route 53 domain registration](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/domain-register.html).

### Recommended learner example

Suppose the learner is Sanket and purchases `sanketawslab.com`:

| Purpose | Template | Sanket's example |
|---|---|---|
| Learner name | `<LEARNER>` | `sanket` |
| Resource prefix | `<PREFIX>` | `sanket-w8` |
| Registered domain | `<ROOT-DOMAIN>` | `sanketawslab.com` |
| CloudFront hostname | `<CDN-NAME>` | `cdn.sanketawslab.com` |
| Delegated Route 53 zone | `<LAB-ZONE>` | `lab.sanketawslab.com` |
| Primary endpoint | `primary.<LAB-ZONE>` | `primary.lab.sanketawslab.com` |
| Secondary endpoint | `secondary.<LAB-ZONE>` | `secondary.lab.sanketawslab.com` |
| Weighted endpoint | `weighted.<LAB-ZONE>` | `weighted.lab.sanketawslab.com` |
| Failover endpoint | `app.<LAB-ZONE>` | `app.lab.sanketawslab.com` |
| S3 bucket | `<PREFIX>-edge-<ACCOUNT-ID>-ap-south-1` | `sanket-w8-edge-123456789012-ap-south-1` |

The example domain is illustrative and may not be available. Avoid your full
legal name if you do not want it public. Domain names, DNS records, certificate
transparency entries, and public hosted-zone data are publicly observable.

### Identify the authoritative DNS provider

The registrar that sold the domain and the service hosting its DNS can be
different. Add records only where the domain's current authoritative name
servers point.

Run:

```bash
dig NS <ROOT-DOMAIN> +short
```

Interpret the result:

- GoDaddy-style name servers -> manage active records in GoDaddy DNS.
- Hostinger name servers -> manage active records in Hostinger hPanel.
- Cloudflare name servers -> manage active records in Cloudflare DNS.
- `awsdns-*` name servers -> manage active records in Route 53.

Changing records in an inactive DNS panel has no effect. Record the provider
and current name servers before continuing.

## DNS Record Map for the Complete Practical

Keep these three jobs separate:

| Record job | Created where | Name | Value |
|---|---|---|---|
| Prove control to ACM | Parent authoritative DNS | ACM-generated `_token.cdn` | ACM-generated `_token.acm-validations.aws` |
| Send viewers to CloudFront | Parent authoritative DNS | `cdn` | `<DISTRIBUTION-DOMAIN>.cloudfront.net` |
| Delegate lab DNS to Route 53 | Parent authoritative DNS | `lab` | Four Route 53 name servers |
| Route lab endpoints | Route 53 `<LAB-ZONE>` | `primary`, `secondary`, `weighted`, `app` | Learner EC2 IPs and policies |

Never replace the root domain's name servers merely to add one `CNAME` unless
you deliberately choose the full-domain Route 53 method described below.

## Provider A - GoDaddy Exact DNS Steps

Use this path only when `dig NS <ROOT-DOMAIN>` confirms the domain uses GoDaddy
authoritative name servers.

### Add the ACM validation CNAME

1. Sign in to **GoDaddy → Domain Portfolio**.
2. Select `<ROOT-DOMAIN>` to open Domain Settings.
3. Select **DNS**.
4. Choose **Add New Record**.
5. Set **Type = CNAME**.
6. Copy the ACM validation name. GoDaddy expects the host portion without the
   root domain. Example:

```text
ACM displays: _abc123.cdn.sanketawslab.com.
GoDaddy Name: _abc123.cdn
```

7. Paste the complete ACM validation target in **Value**. Example shape:

```text
_xyz987.acm-validations.aws.
```

8. Select a short available TTL for the lab or keep GoDaddy's default.
9. Choose **Save** and complete account verification if prompted.
10. Do not add quotes, `https://`, a path, or an IP address.

### Add the CloudFront application CNAME

After CloudFront accepts `<CDN-NAME>` as an alternate domain:

1. Choose **Add New Record → CNAME**.
2. Enter:

```text
Type:  CNAME
Name:  cdn
Value: <DISTRIBUTION-DOMAIN>.cloudfront.net
TTL:   shortest practical value or provider default
```

3. Save. Do not delete the separate `_token.cdn` ACM record.

### Delegate `lab.<ROOT-DOMAIN>` to Route 53

After creating the Route 53 public hosted zone, copy all four name servers from
its automatically created `NS` record. Add four separate GoDaddy records:

```text
Type: NS   Name: lab   Value: ns-111.awsdns-11.com
Type: NS   Name: lab   Value: ns-222.awsdns-22.net
Type: NS   Name: lab   Value: ns-333.awsdns-33.org
Type: NS   Name: lab   Value: ns-444.awsdns-44.co.uk
```

The values above are shapes only. Use the four exact name servers from your
hosted zone. Do not enter `lab.<ROOT-DOMAIN>` in the **Name** field if GoDaddy
automatically appends the domain. Do not edit the default root `NS` records and
do not add the Route 53 `SOA` record to GoDaddy.

GoDaddy's official guides: [add a CNAME record](https://help-center.dc-aws.godaddy.com/help/add-a-cname-record-19236)
and [add an NS record](https://help-center.dc-aws.godaddy.com/help/add-an-ns-record-19212).

## Provider B - Hostinger Exact DNS Steps

Use this path only when `dig NS <ROOT-DOMAIN>` confirms the domain uses
Hostinger authoritative name servers.

### Add the ACM and CloudFront CNAME records in hPanel

1. Sign in to **Hostinger hPanel**.
2. Open **Domains → DNS**, then select `<ROOT-DOMAIN>`.
   - An account with hosting may instead show **Websites → select site →
     Advanced → DNS Zone Editor**.
3. In **Manage DNS records**, select **CNAME**.
4. For ACM validation, enter the name without the root-domain suffix. Example:

```text
Type:      CNAME
Name:      _abc123.cdn
Points to: _xyz987.acm-validations.aws
TTL:       provider default or a short available value
```

5. Choose **Add Record**.
6. After CloudFront is configured, add the application record:

```text
Type:      CNAME
Name:      cdn
Points to: <DISTRIBUTION-DOMAIN>.cloudfront.net
TTL:       provider default or a short available value
```

7. Save and keep both records.

Hostinger automatically appends the root domain to the **Name** field. Its
official documentation also says that active records must be managed at the
provider named by the current name servers.

### Important Hostinger limitation for the Route 53 lab zone

Hostinger's current official DNS documentation states that custom `NS` records
for subdomains are not supported. Therefore, do not attempt four `NS lab`
records in hPanel. They may be rejected or may not create a working delegation.

To perform the exact Route 53 routing-policy practical with a domain registered
at Hostinger, use a disposable practice domain and move the entire domain's
authoritative DNS to Route 53:

1. In Route 53, create a **public hosted zone** named `<ROOT-DOMAIN>`, not
   `<LAB-ZONE>`.
2. Copy the four Route 53 name servers.
3. Before changing anything, inventory every active Hostinger record, including
   `A`, `AAAA`, `CNAME`, `MX`, `TXT`, `CAA`, DKIM, SPF, and verification records.
4. Recreate every record that must remain active in the new Route 53 hosted
   zone. A nameserver change does not copy them automatically.
5. In hPanel, open **Domains → DNS → `<ROOT-DOMAIN>` → DNS / Nameservers →
   Change Nameservers**.
6. Choose **Change nameservers**, enter the four exact Route 53 values, and
   save.
7. Wait until `dig NS <ROOT-DOMAIN> +short` returns the Route 53 servers.
8. From this point forward, create the ACM validation record, `cdn` record, and
   all routing-policy records in Route 53. You may create `primary.lab`,
   `secondary.lab`, `weighted.lab`, and `app.lab` directly in the root hosted
   zone; a second delegated hosted zone is unnecessary.

Do not move the name servers of a production, business, or email domain for
this challenge. Missing `MX`/`TXT` records can break email, and changing DNSSEC
without planning can make the domain fail validation.

Hostinger's official guides: [manage CNAME records](https://www.hostinger.com/support/4738777-how-to-manage-cname-records-at-hostinger/),
[manage DNS records and the subdomain-NS limitation](https://www.hostinger.com/support/1583249-how-to-manage-dns-records-at-hostinger/),
and [change nameservers](https://www.hostinger.com/support/1696789-how-to-change-nameservers-at-hostinger/).

## Provider C - Namecheap or Cloudflare

### Namecheap BasicDNS/PremiumDNS/FreeDNS

1. Open **Domain List → Manage → Advanced DNS**.
2. Under **Host Records**, choose **Add New Record**.
3. Use **CNAME Record** for ACM validation and `cdn`; enter only the host label,
   not the root domain, when the panel appends it automatically.
4. Use **NS Record** four times with **Host = lab** and each Route 53 name server
   as the value.
5. Choose **Save All Changes**.

Reference: [Namecheap subdomain and NS-record setup](https://www.namecheap.com/support/knowledgebase/article.aspx/9776/2237/how-to-create-a-subdomain-for-my-domain/).

### Cloudflare authoritative DNS

1. Open **Cloudflare dashboard → `<ROOT-DOMAIN>` → DNS → Records**.
2. Choose **Add record**.
3. For ACM validation, add the exact `CNAME` and set **Proxy status = DNS only**.
4. For `cdn`, add a `CNAME` to the CloudFront domain. Keep it **DNS only** for
   this lab so CloudFront remains the viewer-facing CDN and certificate path.
5. For delegation, add four `NS` records with **Name = lab** and the four Route
   53 values.
6. Save each record and confirm that no conflicting `A`, `AAAA`, or `CNAME`
   exists at the same name.

References: [Cloudflare DNS record creation](https://developers.cloudflare.com/dns/manage-dns-records/how-to/create-dns-records/)
and [subdomain delegation](https://developers.cloudflare.com/dns/manage-dns-records/how-to/subdomains-outside-cloudflare/).

## Provider-Neutral Record Rule

For any other registrar or DNS provider:

1. Confirm it is authoritative with `dig NS`.
2. Find its DNS Zone, Zone Editor, or Manage Records page.
3. Determine whether **Name/Host** expects a relative label or full name.
4. Add the ACM `CNAME`, wait for public resolution, and keep it.
5. Add the `cdn` application `CNAME` only after CloudFront is configured.
6. Confirm the provider supports subdomain `NS` records before attempting the
   Route 53 delegation. If it does not, use a disposable domain with Route 53
   authoritative DNS or obtain instructor approval for design-only evidence.
7. Never replace an active domain's root nameservers without first copying all
   required records and understanding DNSSEC/email impact.

## Part A - Request and Validate ACM from Scratch

Do this first because DNS validation can take time.

1. Select **US East (N. Virginia), `us-east-1`**.
2. Open **AWS Certificate Manager → Request a certificate**.
3. Choose **Request a public certificate**.
4. Enter `<CDN-NAME>`, select **DNS validation**, and use RSA 2048.
5. Request the certificate. Its initial status should be **Pending validation**.
6. Open its **Domains** section and copy the exact validation `CNAME` name and
   value.
7. Create that `CNAME` at the authoritative DNS provider:
   - If the domain is hosted in Route 53, use **Create records in Route 53**.
   - Otherwise add the record at your DNS provider. Follow its rules for
     relative versus fully qualified record names so the suffix is not doubled.
8. Confirm publicly that the validation name resolves to the ACM
   `acm-validations.aws` target.
9. Refresh ACM until status is **Issued**. Do not submit duplicate requests
   while validation is pending.
10. Keep the validation `CNAME`; ACM uses it for managed renewal.

Verify from CloudShell or a local terminal using the complete ACM-generated
record name:

```bash
dig CNAME <ACM-VALIDATION-NAME> +short
```

Expected: the exact `acm-validations.aws` target shown by ACM. An empty answer
means the record is not yet visible from public authoritative DNS. A name that
contains `<ROOT-DOMAIN>` twice means the provider appended the suffix after you
entered a fully qualified name; correct the host field rather than requesting
another certificate.

Record sanitized proof of the requested name, `us-east-1`, validation method,
and **Issued** status. Do not continue to custom-domain attachment until it is
issued, but the default CloudFront-domain work can proceed while you wait.

The ACM validation record and the later application record are different:

```text
_<random-token>.<CDN-NAME> -> ACM validation target
<CDN-NAME>                 -> CloudFront distribution
```

## Part B - Create Two Regional HTTP Endpoints

### Create the Mumbai endpoint

1. Select **Asia Pacific (Mumbai), `ap-south-1`**.
2. Open **EC2 → Security Groups → Create security group**.
3. Create `<PREFIX>-day15-primary-sg` in the default or approved VPC.
4. Add HTTP TCP `80` from `0.0.0.0/0` because Route 53 public health checkers
   must reach this temporary endpoint. Do not add global SSH.
5. Open **EC2 → Instances → Launch instances**.
6. Configure:

| Setting | Value |
|---|---|
| Name | `<PREFIX>-day15-primary-mumbai` |
| AMI | Amazon Linux 2023 |
| Instance type | Small lab-eligible type |
| Key pair | None when using Session Manager/approved alternative |
| VPC | Same VPC as the primary SG |
| Subnet | Public subnet with internet-gateway route |
| Auto-assign public IPv4 | Enabled for this temporary lab |
| Security Group | `<PREFIX>-day15-primary-sg` |

7. Under **Advanced details → User data**, paste:

Launch a small Amazon Linux 2023 instance named
`<PREFIX>-day15-primary-mumbai` in a public Mumbai subnet. Enable a public
IPv4 only for the lab and use:

```bash
#!/bin/bash
dnf install -y nginx
cat <<'HTML' > /usr/share/nginx/html/index.html
<!doctype html><html><body style="font-family:Arial;text-align:center;padding:80px">
<h1>Primary - Mumbai</h1><p>Day 15 Route 53 endpoint</p>
</body></html>
HTML
systemctl enable --now nginx
```

8. Launch, wait for both instance status checks, record `<PRIMARY-IP>` privately,
   and open `http://<PRIMARY-IP>/`.

### Create the N. Virginia endpoint

Repeat the same process in **US East (N. Virginia), `us-east-1`** with a
Region-local Security Group named `<PREFIX>-day15-secondary-sg` and instance
`<PREFIX>-day15-secondary-virginia`. Security Groups are Regional, so the
Mumbai group cannot be selected in N. Virginia.

Use this user data:

```bash
#!/bin/bash
dnf install -y nginx
cat <<'HTML' > /usr/share/nginx/html/index.html
<!doctype html><html><body style="font-family:Arial;text-align:center;padding:80px">
<h1>Secondary - N. Virginia</h1><p>Day 15 Route 53 endpoint</p>
</body></html>
HTML
systemctl enable --now nginx
```

Record `<SECONDARY-IP>` privately and verify both pages show different Region
labels. If a page does not load, inspect EC2 status checks, public subnet
routing, public IPv4 assignment, Security Group TCP 80, and user-data logs
before continuing.

## Part C - Create the Private S3 Origin

In Mumbai, create `<BUCKET>` with:

- Block all public access enabled;
- Bucket owner enforced;
- versioning enabled; and
- default encryption enabled.

Do not enable S3 static website hosting. You may use the included
[sample origin page](./index.html), or create and upload `index.html`:

```html
<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Day 15</title></head>
<body style="font-family:Arial;text-align:center;padding:80px">
  <h1>AWS Day 15</h1>
  <p>Private S3 → CloudFront OAC → ACM → Route 53 → WAF</p>
  <strong>Page Version: 1</strong>
</body></html>
```

Create `private/learner-proof.txt` containing only synthetic text. Confirm its
direct S3 object URL returns `403 AccessDenied`.

## Part D - Create CloudFront with OAC

Open **CloudFront → Distributions → Create distribution**. Create
`<PREFIX>-day15-edge` with:

| Setting | Value |
|---|---|
| Origin | `<BUCKET>` S3 REST endpoint, not website endpoint |
| Private origin access | Origin Access Control enabled |
| Viewer protocol | Redirect HTTP to HTTPS |
| Methods | `GET`, `HEAD` |
| Cache policy | Managed `CachingOptimized` |
| Compression | Enabled |
| Certificate initially | Default CloudFront certificate |
| Default root object | `index.html` |

For the origin:

1. Choose the bucket from the S3 origin selector.
2. Confirm its hostname resembles
   `<BUCKET>.s3.ap-south-1.amazonaws.com`; reject any `s3-website` endpoint.
3. Choose the option that allows private S3 access through an Origin Access
   Control and create/associate the OAC when prompted.
4. Leave **Origin path** empty and Origin Shield disabled for the lab.
5. Use the default CloudFront certificate during initial creation.
6. Create the distribution, record its generated domain and distribution ID,
   and wait for **Deployed/Enabled**.
7. Open **Settings → Edit**, set **Default root object = `index.html`**, save,
   and wait for deployment again.

Allow CloudFront to update the bucket policy. Inspect it and confirm the
principal is `cloudfront.amazonaws.com`, access is `s3:GetObject`, and the
condition restricts `AWS:SourceArn` to your exact distribution ARN.

Validate:

```text
Direct S3 index URL                         -> 403
https://<DISTRIBUTION-DOMAIN>/              -> Version 1
https://<DISTRIBUTION-DOMAIN>/index.html    -> Version 1
```

## Part E - Prove Cache Behavior

Run twice from a terminal or CloudShell:

```bash
curl -I "https://<DISTRIBUTION-DOMAIN>/index.html"
curl -I "https://<DISTRIBUTION-DOMAIN>/index.html"
```

Record `X-Cache`, `Age`, `Via`, and `X-Amz-Cf-Pop`. A first miss is not
guaranteed if the object is already cached at that edge.

Change the page to `Version: 2` and upload it to the same key. Observe that the
old version may remain cached. Open **CloudFront → distribution → Invalidations
→ Create invalidation**, enter `/index.html`, wait for **Completed**, and verify
Version 2.

## Part F - Protect a Path with a Signed URL

In CloudShell, create the signing keys:

```bash
openssl genrsa -out cloudfront-private-key.pem 2048
openssl rsa -pubout -in cloudfront-private-key.pem -out cloudfront-public-key.pem
chmod 600 cloudfront-private-key.pem
cat cloudfront-public-key.pem
```

Never display, upload, or commit the private key.

1. In CloudFront, create public key `<PREFIX>-day15-public-key` by pasting the
   complete public PEM.
2. Create key group `<PREFIX>-day15-key-group` containing that public key.
3. Add behavior `private/*` using the S3 origin, `GET/HEAD`, HTTPS redirect,
   `CachingOptimized`, **Restrict viewer access = Yes**, and the trusted key
   group.
4. Wait for deployment.
5. Open `https://<DISTRIBUTION-DOMAIN>/private/learner-proof.txt` without a
   signature. Expect `403`/`MissingKey`.
6. Record the CloudFront public-key ID and choose an expiry no more than 15
   minutes in the future, in UTC.

```bash
aws cloudfront sign \
  --url "https://<DISTRIBUTION-DOMAIN>/private/learner-proof.txt" \
  --key-pair-id "<PUBLIC-KEY-ID>" \
  --private-key file://cloudfront-private-key.pem \
  --date-less-than "<FUTURE-UTC-TIME>"
```

Open the complete returned URL. Expect `200`. Do not publish the URL. After
expiry, confirm the same URL returns `403`, then securely remove the private
key from CloudShell before cleanup.

### Optional signed-cookie extension

Signed cookies are optional because the minimum challenge protects one object.
If implementing them, keep the same trusted key group and use a short custom
policy that authorizes only:

```text
https://<DISTRIBUTION-DOMAIN>/private/*
```

The signing application creates three cookie values: `CloudFront-Policy`,
`CloudFront-Signature`, and `CloudFront-Key-Pair-Id`. Set them as Secure cookies
and avoid logging or publishing them. Validate in a private browser session:

1. clear any old CloudFront signed cookies;
2. prove a private object fails without authorization;
3. set the three freshly generated cookies;
4. open two different objects under `private/*` without URL query signatures;
5. wait for expiry and prove access fails again; and
6. clear the cookies after the demonstration.

Do not reuse a signed-URL canned policy as if it were a cookie policy. In a
production application, the backend issues cookies only after authenticating
and authorizing the user.

## Part G - Attach Your ACM Certificate and DNS Name

After the certificate is **Issued**:

1. Open **CloudFront → Distributions → `<PREFIX>-day15-edge` → Settings → Edit**
   or **Add a domain**, depending on the current console layout.
2. Add alternate domain `<CDN-NAME>`.
3. Select your issued ACM certificate from `us-east-1`.
4. Choose the current recommended TLS 1.2 security policy and deploy.
5. At authoritative DNS, create the separate application record:
   - Route 53: alias `A`/`AAAA` to the CloudFront distribution; or
   - another provider: `CNAME <CDN-NAME> -> <DISTRIBUTION-DOMAIN>`.
6. Keep the random-token validation `CNAME` as well.
7. Wait until the distribution returns to **Deployed**.
8. Verify DNS and HTTPS:

```bash
dig CNAME <CDN-NAME> +short
curl -I "https://<CDN-NAME>/"
openssl s_client -connect <CDN-NAME>:443 -servername <CDN-NAME> </dev/null 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates
```

Expected: the DNS path reaches CloudFront, HTTP returns success, and the public
certificate covers `<CDN-NAME>` without a browser warning.

If the certificate is not offered by CloudFront, confirm it is `Issued`, is in
`us-east-1`, and covers the exact alternate name.

## Part H - Create Route 53 Health Checks and Records

### Create and delegate the lab hosted zone

Use one of these mutually exclusive designs:

- Parent DNS supports subdomain `NS`: create a Route 53 public hosted zone for
  `<LAB-ZONE>`, then add its four `NS` records at the parent using the provider
  instructions above.
- Whole practice domain already uses Route 53: keep the existing
  `<ROOT-DOMAIN>` hosted zone and create names such as `primary.lab` directly;
  do not create a redundant second zone.

For the delegated design:

1. Open **Route 53 → Hosted zones → Create hosted zone**.
2. Enter `<LAB-ZONE>`.
3. Select **Public hosted zone** and create it.
4. Open its automatically created `NS` record and copy all four name servers.
5. At the parent authoritative DNS provider, add four `NS` records with host
   `lab`, following the provider-specific procedure above.
6. Do not copy the Route 53 `SOA` record into the parent zone.
7. Verify:

```bash
dig NS <LAB-ZONE> +short
```

Expected: the exact four servers assigned to the learner's Route 53 zone. If
the answer is empty, query the parent authoritative server directly and inspect
the `NS lab` records before creating routing-policy records.

### Create simple endpoint records

Inside the authoritative Route 53 zone, create:

| Record | Type | Value | TTL | Policy |
|---|---|---|---:|---|
| `primary.<LAB-ZONE>` | `A` | `<PRIMARY-IP>` | 30 | Simple |
| `secondary.<LAB-ZONE>` | `A` | `<SECONDARY-IP>` | 30 | Simple |

Verify:

```bash
dig +short primary.<LAB-ZONE>
dig +short secondary.<LAB-ZONE>
curl "http://primary.<LAB-ZONE>/"
curl "http://secondary.<LAB-ZONE>/"
```

### Create public Route 53 health checks

Open **Route 53 → Health checks → Create health check**.

Primary:

```text
Name:              <PREFIX>-day15-primary-hc
Monitor:           Endpoint
Endpoint by:       IP address
IP address:        <PRIMARY-IP>
Protocol / port:   HTTP / 80
Path:              /
Request interval:  Standard 30 seconds
Failure threshold: 3
String matching:   Off
Invert status:     No
```

Create the secondary check as `<PREFIX>-day15-secondary-hc` with
`<SECONDARY-IP>`. Wait for both checks to become **Healthy**. A browser success
does not guarantee health-check success if the Security Group blocks public
health checkers or the path returns something other than `2xx`/`3xx`.

### Create the classroom `80/20` weighted records

Create two `A` records with the exact same name `weighted.<LAB-ZONE>`:

| Setting | Mumbai record | N. Virginia record |
|---|---|---|
| Routing policy | Weighted | Weighted |
| Value | `<PRIMARY-IP>` | `<SECONDARY-IP>` |
| TTL | 30 | 30 |
| Weight | 80 | 20 |
| Record ID | `Mumbai-80` | `Virginia-20` |
| Health check | Primary check | Secondary check |

Copy one of the Route 53 authoritative name servers without its trailing dot,
then query it directly:

```bash
for i in {1..20}; do
  dig +short weighted.<LAB-ZONE> @<ROUTE53-NAME-SERVER>
done | sort | uniq -c
```

Weights influence DNS-answer proportions; they do not guarantee an exact
request ratio because resolver caching affects viewers.

Change the weights to `50/50`, repeat the authoritative queries, and compare
the observations. A small sample will not always be exactly proportional.

### Optional latency-routing comparison

Create this only if the additional records fit the lab time. Create two `A`
records named `latency.<LAB-ZONE>`:

| Setting | Mumbai record | N. Virginia record |
|---|---|---|
| Routing policy | Latency | Latency |
| Value | `<PRIMARY-IP>` | `<SECONDARY-IP>` |
| Region | Asia Pacific (Mumbai) | US East (N. Virginia) |
| Record ID | `Mumbai-Latency` | `Virginia-Latency` |
| Health check | Primary check | Secondary check |

Query from different networks/resolvers where available and explain that the
policy uses AWS's latency measurements from the DNS resolver location. It is
not a fixed country-to-Region mapping. Delete the optional records in cleanup.

### Create the active-passive failover records

Create two `A` records named `app.<LAB-ZONE>`:

| Setting | Primary record | Secondary record |
|---|---|---|
| Routing policy | Failover | Failover |
| Failover record type | Primary | Secondary |
| Value | `<PRIMARY-IP>` | `<SECONDARY-IP>` |
| TTL | 30 | 30 |
| Record ID | `Mumbai-Primary` | `Virginia-Secondary` |
| Health check | Primary check | Secondary check |

Prove the healthy baseline:

```bash
dig +short app.<LAB-ZONE> @<ROUTE53-NAME-SERVER>
curl "http://app.<LAB-ZONE>/"
```

Expected: the Mumbai IP and primary page.

### Trigger a real application failure and prove failback

Connect to the Mumbai instance through Session Manager, EC2 Instance Connect,
or another approved path. Stop only Nginx so the instance and its public IP stay
unchanged:

```bash
sudo systemctl stop nginx
sudo systemctl status nginx --no-pager
curl --max-time 5 http://localhost || true
```

Wait for `<PREFIX>-day15-primary-hc` to become **Unhealthy**. With a 30-second
interval and threshold of 3, detection is not immediate. Query the authoritative
server until it returns `<SECONDARY-IP>`:

```bash
for i in {1..12}; do
  date
  dig +short app.<LAB-ZONE> @<ROUTE53-NAME-SERVER>
  sleep 15
done
```

Stop the loop with `Ctrl+C` after failover. Confirm the DNS hostname serves the
secondary page. Then restore the primary:

```bash
sudo systemctl start nginx
sudo systemctl status nginx --no-pager
curl --max-time 5 http://localhost
```

Wait for the health check to become **Healthy**, query the authoritative server
again, and confirm the answer returns to `<PRIMARY-IP>`.

An authoritative query proves Route 53's current decision. A normal recursive
resolver or browser can continue returning the earlier answer until cached TTLs
expire. Record health-check transition time, authoritative DNS transition time,
and observed client transition separately.

## Part I - Test WAF Safely

Use your own current public IPv4 only; keep it out of screenshots.

1. Find your current public IPv4 through an approved service and express it as
   `<YOUR-PUBLIC-IP>/32`. Do not use a learner's or shared-office IP.
2. Open **WAF & Shield → IP sets → Create IP set**.
3. Select **CloudFront (Global)** scope, IPv4, name
   `<PREFIX>-day15-learner-ip`, and add only your `/32`.
4. Open or create the CloudFront-scope web ACL associated with the distribution.
5. Choose **Rules → Add rules → Add my own rules and rule groups → Rule builder**.
6. Create `Block-Learner-IP`, match the IP set, and set **Action = Count**.
7. Save, request the public root page several times, and confirm the page still
   works because Count is non-terminating.
8. Open WAF traffic overview, metrics, or sampled requests and capture the rule
   match with the IP masked.
9. Edit only `Block-Learner-IP`, set **Action = Block**, and save.
10. After propagation, request the public root page—not the signed private URL.
    Expect a WAF/CloudFront `403`.
11. Immediately return the rule to Count or delete it, verify the page works,
    then delete the IP set after it is no longer referenced.

Do not enable Shield Advanced or create Global Accelerator for evidence.

## Decision Notes - Do Not Provision These Services

Complete the reason column:

| Requirement | Choose | Learner reason |
|---|---|---|
| Cache private S3 objects at edge locations | CloudFront |  |
| Authorize one private download | Signed URL |  |
| Authorize several restricted files | Signed cookies |  |
| Inspect Layer 7 HTTP requests | AWS WAF |  |
| Common infrastructure DDoS protection | Shield Standard |  |
| Paid enhanced DDoS response/protection | Shield Advanced |  |
| Static anycast IPs for TCP/UDP without caching | Global Accelerator |  |
| DNS answers without proxying traffic | Route 53 |  |

## Troubleshooting Order

### ACM remains Pending validation

1. Confirm the certificate was requested in `us-east-1`.
2. Run `dig NS <ROOT-DOMAIN> +short` and edit records at that provider.
3. Run `dig CNAME <ACM-VALIDATION-NAME> +short`.
4. Check that the host does not contain the root domain twice.
5. Check that the value is the exact ACM target, not the CloudFront domain.
6. Check restrictive `CAA` records and DNSSEC health.
7. Do not request duplicates while the existing request is valid.

### CloudFront returns `403 AccessDenied`

1. Confirm the origin is the S3 REST endpoint, not website hosting.
2. Confirm OAC is associated with the behavior's actual origin.
3. Confirm the object key and letter case.
4. Confirm the bucket policy contains the exact distribution ARN and bucket ARN.
5. Keep S3 Block Public Access enabled; do not solve this by making S3 public.

### Unsigned URL does not return `MissingKey`

Confirm `private/*` is above less-specific behaviors, viewer restriction is
enabled, the trusted key group is selected, and the distribution is deployed.

### Signed URL still returns `403`

Check the full public-key ID, key-group membership, exact hostname/object path,
UTC expiry, private/public key pair, and whether the URL was truncated or
modified. Generate a new short-lived URL after changing from the default
CloudFront hostname to `<CDN-NAME>`.

### Route 53 delegation is empty

1. Confirm the parent DNS provider supports subdomain `NS` records.
2. Confirm all four records use host `lab` and the exact Route 53 values.
3. Confirm you did not replace root nameservers by mistake.
4. Query the parent authoritative server directly.
5. Hostinger users must follow the full-domain Route 53 method above because
   Hostinger does not support custom subdomain `NS` records.

### Health check stays Unhealthy

Open the endpoint by IP, confirm Nginx and TCP 80, inspect the Security Group,
confirm the path returns `2xx`/`3xx`, and verify the IP did not change after an
instance stop/start.

### Failover still shows the primary

Separate the health-check state, authoritative DNS answer, recursive-resolver
cache, and browser cache. Query the Route 53 authoritative server directly
before concluding the routing policy is wrong.

## Official References

- [ACM DNS validation](https://docs.aws.amazon.com/acm/latest/userguide/dns-validation.html)
- [CloudFront alternate domains and HTTPS](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cnames-and-https-procedures.html)
- [CloudFront certificate Region requirements](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cnames-and-https-requirements.html)
- [Route 53 subdomain delegation](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/CreatingNewSubdomain.html)
- [Route 53 routing policies](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy.html)
- [CloudFront OAC for S3](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html)

## Validation Checklist

- [ ] ACM certificate was requested by the learner in `us-east-1`
- [ ] ACM validation `CNAME` resolves and certificate is `Issued`
- [ ] Direct S3 access fails and CloudFront OAC access succeeds
- [ ] Cache headers and invalidation behavior are recorded
- [ ] Unsigned private path fails and short-lived signed URL succeeds
- [ ] Custom HTTPS hostname works with the learner's certificate
- [ ] Both Route 53 health checks are healthy at baseline
- [ ] Weighted authoritative queries return both endpoints
- [ ] `80/20` and `50/50` weighted observations are compared
- [ ] Primary failure changes failover answer; recovery produces failback
- [ ] WAF Count and Block are proven and normal access is restored
- [ ] All evidence is sanitized and cleanup is complete

Continue with [Week 8 cleanup](./06-cleanup.md).
