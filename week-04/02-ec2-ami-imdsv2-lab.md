# Day 7 Lab - Secure nginx Golden AMI

## Resources

| Resource | Exact name |
|---|---|
| Builder EC2 | `cloudadhar-ec2-ami-builder-01` |
| Security group | `cloudadhar-sg-nginx-public` |
| IAM role | `cloudadhar-role-ec2-ssm` |
| Golden AMI v1 | `cloudadhar-ami-nginx-golden-v1-20260725` |
| Patched AMI v2 | `cloudadhar-ami-nginx-golden-v2-20260725` |
| Test EC2 | `cloudadhar-ec2-ami-test-v2-01` |

Tag resources with `Project=AWS-Zero-to-Hero`,
`Module=EC2 Fundamentals`, `Environment=Training`,
`Owner=CloudAdhar`, `ManagedBy=Manual`,
`CleanupAfter=25 July 2026`, and `DataClassification=Training-Only`.

## Build

1. Create `cloudadhar-role-ec2-ssm` for EC2 and attach
   `AmazonSSMManagedInstanceCore`.
2. Create `cloudadhar-sg-nginx-public`. Prefer HTTP from your public `/32`.
   Do not add public SSH.
3. Launch Amazon Linux 2023 as `cloudadhar-ec2-ami-builder-01`.
4. Attach the SSM role and security group.
5. Set metadata to **V2 only (token required)**.
6. Use this User Data:

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

## Validate Bootstrap

Connect with Session Manager:

```bash
sudo cloud-init status --wait
sudo systemctl status nginx --no-pager
curl -I http://localhost
sudo tail -n 40 /var/log/cloud-init-output.log
```

## Validate IMDSv2

Tokenless request:

```bash
curl -sS -o /dev/null \
  -w 'IMDSv1 HTTP status: %{http_code}\n' \
  --max-time 3 \
  http://169.254.169.254/latest/meta-data/instance-id
```

Expected: `IMDSv1 HTTP status: 401`.

Token-based requests:

```bash
TOKEN=$(curl -sS -X PUT \
  -H 'X-aws-ec2-metadata-token-ttl-seconds: 21600' \
  http://169.254.169.254/latest/api/token)

curl -sS -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/instance-id

curl -sS -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/placement/availability-zone

unset TOKEN
```

Do not query or publish role credential endpoints. Mask the dynamic output.

## Patch and Image

Check and apply only the release update tested for class:

```bash
cat /etc/os-release
sudo dnf check-update || test $? -eq 100
sudo dnf upgrade -y
sudo systemctl restart nginx
curl -I http://localhost
sudo dnf clean all
```

Remove secrets, host-specific content, and temporary files. Confirm nginx is
enabled and active. Create
`cloudadhar-ami-nginx-golden-v2-20260725` with reboot enabled and wait for
`Available`.

Launch `cloudadhar-ec2-ami-test-v2-01` from v2 with:

- The SSM role and IMDSv2 required
- No User Data

Validate:

```bash
sudo systemctl is-enabled nginx
sudo systemctl is-active nginx
curl -I http://localhost
cat /etc/os-release
```

Success means nginx starts from the image without User Data.

## Evidence

- Builder role, security group, AMI, and IMDSv2 setting
- nginx and cloud-init success
- Tokenless `401`
- Token-based safe metadata success
- Golden AMI v2 `Available`
- Test instance serving nginx without User Data

## EC2 Image Builder Automation

The manual workflow above explains what happens inside an image build. This
section automates the same Golden AMI lifecycle through the AWS Management
Console.

```text
Amazon Linux 2023
        |
        v
update-linux
        |
        v
nginx build component
        |
        v
output AMI
        |
        v
nginx test component
        |
        v
private tested Golden AMI
```

Image Builder launches temporary EC2 build and test instances. Run the pipeline
once for the class and complete the cleanup steps.

### Image Builder resource names

| Resource | Exact name |
|---|---|
| Pipeline | `cloudadhar-pipeline-nginx-golden` |
| Image recipe | `cloudadhar-recipe-nginx-golden` |
| Build component | `cloudadhar-component-nginx-build` |
| Test component | `cloudadhar-component-nginx-test` |
| Infrastructure configuration | `cloudadhar-infra-nginx-image-builder` |
| Distribution configuration | `cloudadhar-distribution-nginx-golden` |
| Instance role | `cloudadhar-role-image-builder` |
| Security Group | `cloudadhar-sg-image-builder` |

Use the mandatory tags from the start of this lab. For Image Builder resources,
set `ManagedBy=EC2-Image-Builder`.

### 1. Create the Image Builder role

1. Open **IAM -> Roles -> Create role**.
2. Select **AWS service** and the **EC2** use case.
3. Add:
   - `EC2InstanceProfileForImageBuilder`
   - `AmazonSSMManagedInstanceCore`
4. Name the role `cloudadhar-role-image-builder`.
5. Add the mandatory tags and create the role.
6. Confirm its trust relationship allows EC2 to assume it.

Do not attach `AdministratorAccess`.

### 2. Create the build Security Group

1. Open **EC2 -> Security Groups -> Create security group**.
2. Enter:
   - Name: `cloudadhar-sg-image-builder`
   - Description: `No-inbound Security Group for Image Builder`
   - VPC: the VPC used for the build
3. Add no inbound rules.
4. Keep the outbound access required for Systems Manager and Amazon Linux
   package repositories.
5. Add the mandatory tags and create the Security Group.

### 3. Create the nginx build component

1. Open **EC2 Image Builder -> Components**.
2. Choose **Create component**.
3. Enter:
   - Operating system: Linux
   - Category: Build
   - Name: `cloudadhar-component-nginx-build`
   - Version: `1.0.0`
   - Description: `Install and configure nginx for the Week 4 Golden AMI`
4. Select **Define document content**.
5. Paste:

```yaml
name: CloudAdharNginxBuild
description: Install and configure nginx on Amazon Linux 2023.
schemaVersion: 1.0

phases:
  - name: build
    steps:
      - name: InstallAndConfigureNginx
        action: ExecuteBash
        inputs:
          commands:
            - dnf install -y nginx
            - systemctl enable --now nginx
            - |
              cat > /usr/share/nginx/html/index.html <<'HTML'
              <!doctype html>
              <html>
                <head><title>CloudAdhar Golden AMI</title></head>
                <body>
                  <h1>CloudAdhar EC2 Image Builder Golden AMI</h1>
                  <p>nginx was installed by a versioned Image Builder component.</p>
                </body>
              </html>
              HTML

  - name: validate
    steps:
      - name: ValidateNginxBuild
        action: ExecuteBash
        inputs:
          commands:
            - systemctl is-enabled nginx
            - systemctl is-active nginx
            - test -f /usr/share/nginx/html/index.html
            - grep -q "CloudAdhar EC2 Image Builder" /usr/share/nginx/html/index.html
```

6. Add the mandatory tags.
7. Choose **Create component**.

Components are immutable. Create version `1.0.1` only if the document changes.

### 4. Create the nginx test component

1. Choose **Components -> Create component**.
2. Enter:
   - Operating system: Linux
   - Category: Test
   - Name: `cloudadhar-component-nginx-test`
   - Version: `1.0.0`
   - Description: `Test nginx in the AMI produced by Image Builder`
3. Select **Define document content**.
4. Paste:

```yaml
name: CloudAdharNginxTest
description: Verify nginx on the Image Builder test instance.
schemaVersion: 1.0

phases:
  - name: test
    steps:
      - name: TestNginxImage
        action: ExecuteBash
        inputs:
          commands:
            - systemctl is-enabled nginx
            - systemctl start nginx
            - systemctl is-active nginx
            - curl -fsS http://localhost | grep -q "CloudAdhar EC2 Image Builder"
```

5. Add the mandatory tags and create the component.

The test component must contain only the `test` phase. It runs on an instance
launched from the image produced by the build stage.

### 5. Create the image recipe

1. Open **Image recipes -> Create image recipe**.
2. Select:
   - Output type: Amazon Machine Image (AMI)
   - Name: `cloudadhar-recipe-nginx-golden`
   - Version: `1.0.0`
   - Description: `Amazon Linux 2023 nginx Golden AMI recipe for Week 4`
3. Select the AWS-managed Amazon Linux 2023 x86 image and use its latest
   available OS version.
4. Keep the SSM Agent in the output image.
5. Leave User Data blank and use the default `/tmp` working directory.
6. Add build components in this order:
   1. Amazon-managed `update-linux`
   2. `cloudadhar-component-nginx-build/1.0.0`
7. Add test component:
   - `cloudadhar-component-nginx-test/1.0.0`
8. Use the base-image root volume. If a size is required, use at least 8 GiB
   gp3 with encryption and Delete on termination enabled.
9. Keep the AMI private and do not add a watermark for the training image.
10. Add the mandatory AMI and recipe tags.
11. Create the recipe.

Recipes are immutable. If version `1.0.0` was created without components,
create version `1.0.1` and attach the components. A new component version is
not required unless its YAML content changes.

### 6. Create the infrastructure configuration

1. Open **Infrastructure configurations**.
2. Choose **Create infrastructure configuration**.
3. Enter:
   - Name: `cloudadhar-infra-nginx-image-builder`
   - Instance profile: `cloudadhar-role-image-builder`
   - Instance type: a small instructor-approved type
   - VPC and subnet: a subnet with outbound package-repository access
   - Security Group: `cloudadhar-sg-image-builder`
   - Key pair: none
4. Require IMDSv2 for the build and test instances.
5. Keep termination of temporary instances enabled.
6. Add the mandatory tags and create the configuration.

### 7. Create the distribution configuration

1. Open **Distribution settings**.
2. Choose **Create distribution settings**.
3. Enter:
   - Name: `cloudadhar-distribution-nginx-golden`
   - Region: `ap-south-1`
   - Output AMI name:

     ```text
     cloudadhar-ami-nginx-golden-{{imagebuilder:buildDate}}
     ```

   - Launch permission: Private
4. Do not add another account or Region for the training run.
5. Add the mandatory AMI tags and create the configuration.

### 8. Create and run the pipeline

1. From the correct recipe version, choose **Create pipeline from this
   recipe**.
2. Enter:
   - Pipeline name: `cloudadhar-pipeline-nginx-golden`
   - Schedule: Manual
   - Image tests: Enabled
3. Select:
   - The recipe version containing the build and test components
   - `cloudadhar-infra-nginx-image-builder`
   - `cloudadhar-distribution-nginx-golden`
4. Review and create the pipeline.
5. Before running it, confirm the pipeline's **Image recipe** tab shows the
   correct recipe version.
6. Choose **Actions -> Run pipeline**.
7. Do not start another execution while the image is building.

### 9. Monitor the workflows

The build workflow normally progresses through:

1. `LaunchBuildInstance`
2. `ApplyBuildComponents`
3. `InventoryCollection`
4. `RunSanitizeScript`
5. `RunSysPrepScript`
6. `CreateOutputAMI`
7. `TerminateBuildInstance`

The separate test workflow then launches a test instance and applies the test
component. Wait for the final image status to become `Available`.

If a step fails, open the failed step and its CloudWatch log stream. Do not
select Retry until the cause is understood and corrected. Skipped optional
workflow steps are not failures when the workflow completes with zero failed
steps.

### 10. Validate the Image Builder output

1. Confirm that both build and test workflows completed.
2. Open **EC2 -> AMIs -> Owned by me**.
3. Select the new private Golden AMI.
4. Launch one small test instance:
   - Name: `cloudadhar-ec2-ami-test-v2-01`
   - Public subnet and public IPv4 enabled
   - HTTP Security Group rule from **My IP**
   - IMDSv2 required
   - No key pair
   - User Data left empty
5. Wait for Running and 2/2 status checks.
6. Open `http://PUBLIC-IP` in a browser.
7. Confirm that the CloudAdhar nginx page appears.

This proves that nginx and the page came from the AMI rather than test-instance
User Data.

### Image Builder evidence

- Build and test component versions
- Recipe version showing attached components
- Pipeline status and correct recipe
- Successful build and test workflows
- Output image status `Available`
- Private output AMI
- Test instance launched without User Data
- nginx page opened through HTTP
- Sanitized cleanup evidence

### Image Builder cleanup

Delete in dependency order:

1. Terminate the test instance.
2. Delete or cancel unused image build versions.
3. Delete the Image Builder pipeline.
4. Deregister output AMIs.
5. Delete output AMI EBS snapshots.
6. Delete recipe versions.
7. Delete the infrastructure configuration.
8. Delete the distribution configuration.
9. Delete the custom build and test components.
10. Delete `cloudadhar-sg-image-builder`.
11. Delete the Image Builder role and instance profile if used only for this
    lab.
12. Check for failed-build EC2 instances, EBS volumes, snapshots, and log
    groups.
13. Verify every Region used and review billing later.
