# Day 13 Lab - RDS, Aurora Serverless v2, Recovery, and RDS Proxy

Use the AWS Management Console for resource operations. Commands run only
inside the EC2 database client. This lab creates billable database resources;
review the estimate and complete cleanup.

## Resources

| Resource | Exact name |
|---|---|
| EC2 client | `cloudadhar-rds-client-day13` |
| EC2 IAM role | `cloudadhar-ec2-ssm-role-day13` |
| EC2 client Security Group | `cloudadhar-ec2-rds-client-sg-day13` |
| Database Security Group | `cloudadhar-rds-sg-day13` |
| Source RDS | `cloudadhar-rds-day13` |
| Initial database | `cloudadhardb` |
| Manual snapshot | `cloudadhar-rds-day13-snapshot` |
| PITR restore | `cloudadhar-rds-day13-pitr` |
| Read replica | `cloudadhar-rds-day13-read-replica` |
| Aurora cluster | `cloudadhar-aurora-serverless-day13` |
| Aurora reader | `cloudadhar-aurora-serverless-day13-reader-1` |
| Aurora proxy | `cloudadhar-aurora-proxy-day13` |
| Aurora proxy Security Group | `cloudadhar-aurora-proxy-sg-day13` |
| Table-backup bucket | `cloudadhar-rds-table-backups-<account-id>-ap-south-1` |
| Table-backup prefix | `day13/mysql-table-backups/` |
| Table-backup secret | `cloudadhardb-backup-secret-day13` |
| SSM Command document | `CloudAdhar-RDS-MySQL-Table-Backup-To-S3` |
| State Manager association | `cloudadhar-rds-orders-backup-daily` |
| Association dispatch role | `cloudadhar-ssm-association-dispatch-day13` |
| Region | Mumbai, `ap-south-1` |

Apply:

| Tag | Value |
|---|---|
| `Project` | `AWS-Zero-To-Hero` |
| `Day` | `13` |
| `Module` | `RDS-Aurora-Migration` |
| `Environment` | `Training` |
| `Owner` | `CloudAdhar` |
| `DataClassification` | `Training-Only` |
| `CleanupAfter` | `16-Aug-2026` |

## Safety and Cost Gate

- [ ] Use an IAM training identity, not root.
- [ ] Select Mumbai and confirm the correct account.
- [ ] Use synthetic data only.
- [ ] Review the RDS estimate before creating resources.
- [ ] Keep the database private.
- [ ] Never allow the database port from `0.0.0.0/0` or `::/0`.
- [ ] Prefer Session Manager; do not add public SSH merely for this lab.
- [ ] Retrieve the managed password only while not screen sharing.
- [ ] Never put a password, secret, endpoint, account ID, ARN, connection
      string, or Security Group ID into evidence.

The source DB, read replica, PITR restore, two Aurora Serverless v2 instances,
and RDS Proxy are separate billable resources. Secrets Manager, snapshots,
retained backups, EC2, storage, I/O, and public IPv4 may also add cost. Use the
smallest instructor-approved settings, perform the challenge in one session,
and complete cleanup the same day. Do not create the optional Global Database
or DMS deployment without explicit instructor approval. The table-backup
extension also creates S3 objects and an additional Secrets Manager secret.

## 1. Prepare Session Manager Access

If the Day 13 EC2 role does not already exist:

1. Open **IAM -> Roles -> Create role**.
2. Select **AWS service** and **EC2**.
3. Attach `AmazonSSMManagedInstanceCore`.
4. Name the role `cloudadhar-ec2-ssm-role-day13`.
5. Add Day 13 tags and create it.

The instance also needs outbound connectivity to Systems Manager and to
download the database client and RDS CA bundle. Use the approved VPC endpoints,
NAT path, or controlled public-subnet lab path.

## 2. Create the EC2 Client Security Group

1. Open **EC2 -> Security Groups -> Create security group**.
2. Name it `cloudadhar-ec2-rds-client-sg-day13`.
3. Select the class/default VPC.
4. Add no inbound rules when using Session Manager.
5. Keep the approved outbound rule needed for SSM, package, CA, DNS, and
   database connectivity.
6. Add tags and create it.

## 3. Launch the EC2 Database Client

1. Open **EC2 -> Instances -> Launch instances**.
2. Configure:
   - Name: `cloudadhar-rds-client-day13`
   - AMI: Amazon Linux 2023
   - Instance type: smallest instructor-approved burstable type
   - VPC: class/default VPC
   - Subnet: one with the required outbound connectivity
   - Public IPv4: only if required by the approved lab access path
   - Security Group: `cloudadhar-ec2-rds-client-sg-day13`
   - IAM instance profile: `cloudadhar-ec2-ssm-role-day13`
   - Root storage: encrypted gp3
3. Add Day 13 tags and launch.
4. Wait for **Running**, both status checks, and a connected SSM managed-node
   state.

## 4. Create the RDS Security Group

1. Open **EC2 -> Security Groups -> Create security group**.
2. Name it `cloudadhar-rds-sg-day13`.
3. Select the same VPC as the EC2 client.
4. Add inbound:
   - Type: MySQL/Aurora
   - Protocol/port: TCP `3306`
   - Source: `cloudadhar-ec2-rds-client-sg-day13`
5. Do not use an IP CIDR as the source.
6. Add tags and create it.

## 5. Create the Private RDS MySQL Source

1. Open **RDS -> Databases -> Create database**.
2. Choose **Standard create** or the full configuration flow.
3. Select **MySQL Community**.
4. Select a current instructor-approved MySQL version that does not require
   Extended Support for this lab.
5. Select the Sandbox, Dev/Test, or equivalent training template.
6. Choose **Single-AZ DB instance**.
7. Set:
   - Identifier: `cloudadhar-rds-day13`
   - Master username: `admin`
   - Credentials: managed in AWS Secrets Manager
8. Choose the smallest instructor-approved burstable class, such as
   `db.t4g.micro` when available.
9. Configure:
   - Storage: gp3
   - Allocated storage: minimum supported value, commonly 20 GiB
   - Encryption: enabled with `aws/rds` for this basic lab
   - Storage autoscaling: off for the controlled lab, or use a deliberate
     maximum
10. Under connectivity:
    - VPC: same as EC2
    - DB subnet group: approved group containing subnets in at least two AZs
    - Public access: **No**
    - VPC Security Group: `cloudadhar-rds-sg-day13`
11. Select password authentication for the basic client test.
12. Set initial database name to `cloudadhardb`.
13. Enable automated backups with retention of 1 day.
14. Keep Enhanced Monitoring off for the cost-controlled lab.
15. Keep deletion protection off only because cleanup is required.
16. Select Standard Database Insights when included and appropriate; do not
    enable an unapproved paid monitoring tier.
17. Add Day 13 tags, review the estimate, and create the database.
18. Wait for **Available**.

Validate on the database page:

- [ ] Publicly accessible: No
- [ ] Correct VPC and DB subnet group
- [ ] RDS SG allows `3306` only from the client SG
- [ ] Encryption enabled
- [ ] Automated backups enabled
- [ ] Managed master credential configured
- [ ] Expected engine, class, and storage

## 6. Retrieve the Password Privately

1. Open the source RDS database.
2. Locate its **Master credentials ARN**.
3. Choose **View/Manage in Secrets Manager**.
4. Retrieve the secret only while not screen sharing.
5. Do not paste it into chat, commands, screenshots, shell history, or files.

Enter the password interactively at the MySQL prompt.

## 7. Connect from EC2 with TLS

1. Open **EC2 -> Instances**, select the client, and choose
   **Connect -> Session Manager**.
2. Install a compatible MariaDB/MySQL client and download the RDS CA bundle:

```bash
sudo dnf install mariadb105 -y

curl -o global-bundle.pem \
  https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem
```

If `mariadb105` is unavailable, run `dnf search mariadb` and install the
instructor-approved compatible client.

3. Copy the source endpoint privately from RDS and connect:

```bash
mysql \
  -h <source-rds-endpoint> \
  -P 3306 \
  -u admin \
  -p \
  --ssl-ca=global-bundle.pem \
  --ssl-verify-server-cert \
  cloudadhardb
```

Enter the password only at the prompt.

If the connection fails, check status, VPC, subnet routes, DNS, endpoint,
database name, credentials, SG source, and TLS CA before weakening security.

## 8. Create and Validate Synthetic InnoDB Data

Run inside the MySQL client:

```sql
SELECT VERSION();
SELECT DATABASE();

CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

INSERT INTO orders (customer_name, product_name, amount)
VALUES
('CloudAdhar', 'AWS Training', 4999.00),
('TrainWithShubham', 'SAA-C03 Lab', 2999.00),
('Demo Learner', 'RDS Practical', 999.00);

SELECT * FROM orders ORDER BY order_id;
SHOW STATUS LIKE 'Ssl_cipher';
```

Expected:

- three rows;
- `cloudadhardb` selected;
- InnoDB table; and
- a non-empty TLS cipher.

## 9. Create a Manual Snapshot

1. Open **RDS -> Databases**.
2. Select `cloudadhar-rds-day13`.
3. Choose **Actions -> Take snapshot**.
4. Name it `cloudadhar-rds-day13-snapshot`.
5. Open **RDS -> Snapshots -> Manual**.
6. Wait for **Available**.

Snapshot restore creates a new database; it does not overwrite or rewind the
source.

## 10. Inspect Automated Backups

1. Open the source database's **Maintenance & backups** tab.
2. Record the one-day retention, backup window, automated snapshot, and latest
   restorable time.
3. Verify the training table's engine:

```sql
SELECT TABLE_NAME, ENGINE
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'cloudadhardb';
```

Expected: `orders` uses `InnoDB`.

## 11. Create a Safe PITR Window

PITR selection may be minute-based. Create a clear window between insertion
and deletion.

1. Insert a marker and record UTC:

```sql
INSERT INTO orders (customer_name, product_name, amount)
VALUES ('PITR Marker', 'Recover This Record', 1500.00);

SELECT order_id, customer_name, created_at
FROM orders
ORDER BY order_id;

SELECT UTC_TIMESTAMP() AS marker_created_utc;
```

2. Wait at least two complete minutes.
3. Delete the marker and record UTC:

```sql
DELETE FROM orders
WHERE customer_name = 'PITR Marker';

SELECT ROW_COUNT() AS deleted_rows;
SELECT UTC_TIMESTAMP() AS deletion_time_utc;
```

4. Wait until **Latest restorable time** is later than the chosen recovery
   minute.
5. Select the source and choose **Actions -> Restore to point in time**.
6. Choose a complete minute strictly after creation and before deletion.
7. Set the new identifier to `cloudadhar-rds-day13-pitr`.
8. Use the same VPC, private access, RDS SG, Single-AZ deployment, and smallest
   approved class.
9. Review the estimate.

10. Create the restore and wait for **Available**.
11. Connect from the EC2 client to the new PITR endpoint with TLS and confirm
    that the marker exists at the selected restore time.
12. Confirm that the source still has no marker, proving that PITR created a
    separate database rather than rewinding the source.

Do not overwrite the source. PITR always creates a new database and can take
tens of minutes.

## 12. Compare Multi-AZ Options Without Provisioning

Open the RDS create or modify flow and compare:

1. Single-AZ DB instance: one writer, no standby.
2. Multi-AZ DB instance: writer plus synchronous non-readable standby.
3. Multi-AZ DB cluster: writer plus two readable DB instances across three
   AZs for supported configurations.

Cancel without provisioning unless additional cost is approved.

## 13. Create a Read Replica

1. Select `cloudadhar-rds-day13`.
2. Choose **Actions -> Create read replica**.
3. Configure:
   - Identifier: `cloudadhar-rds-day13-read-replica`
   - Region: Mumbai
   - Class: smallest instructor-approved class
   - Storage: encrypted gp3 with the source-compatible size
   - Deployment: Single-AZ for this disposable lab
   - Public access: No
   - DB subnet group: same approved group
   - VPC Security Group: `cloudadhar-rds-sg-day13`
   - Enhanced Monitoring: Off
   - Deletion protection: Off
4. Review the estimate, create, and wait for **Available**.

## 14. Validate Asynchronous Read Scaling

On the source database, insert:

```sql
INSERT INTO orders (customer_name, product_name, amount)
VALUES ('Replica Test', 'Asynchronous Replication', 2500.00);
```

Connect from the same EC2 client to the replica's separate endpoint with the
same TLS verification pattern. Then run:

```sql
SELECT * FROM orders
WHERE customer_name = 'Replica Test';

SELECT @@global.read_only;
SHOW REPLICA STATUS\G

INSERT INTO orders (customer_name, product_name, amount)
VALUES ('Should Fail', 'Replica Write Test', 1.00);
```

Expected:

1. The row appears after replication catches up.
2. `read_only` returns `1`.
3. Replica I/O and SQL threads report healthy status.
4. `Seconds_Behind_Source` can be zero when caught up but can increase.
5. The write fails with a read-only error.

## 15. Create an Aurora Serverless v2 Cluster

This section creates two billable Aurora instances. Continue only in the
instructor-approved account and remove them during the same lab session.

1. Open **RDS -> Databases -> Create database**.
2. Select **Standard create**.
3. Select **Amazon Aurora** and **Aurora MySQL-Compatible Edition**.
4. Choose a current version that supports Aurora Serverless v2 in Mumbai.
5. Under templates, select **Dev/Test** or the approved training option.
6. Configure:
   - DB cluster identifier: `cloudadhar-aurora-serverless-day13`
   - Master username: `admin`
   - Credentials: managed in AWS Secrets Manager
   - Initial database: `cloudadhardb`
7. Under instance configuration, select **Serverless v2**.
8. Set the capacity range to the smallest supported instructor-approved range,
   such as minimum `0.5` ACU and maximum `1` ACU. A zero-ACU auto-pause option
   is version-dependent; do not assume it is available.
9. Configure:
   - Storage configuration: Aurora Standard for the small lab
   - VPC and DB subnet group: same private database design as the RDS source
   - Public access: **No**
   - VPC Security Group: `cloudadhar-rds-sg-day13`
   - Encryption: enabled
   - Backup retention: 1 day
   - Deletion protection: off only because same-day cleanup is required
10. Review the estimate, create the cluster, and wait for the cluster and
    writer instance to become **Available**.

An ACU represents a combination of memory, CPU, and networking capacity;
approximately 2 GiB of memory is associated with each ACU.

## 16. Add an Aurora Reader

1. Open the new Aurora cluster.
2. Select the writer DB instance and choose **Actions -> Add reader**.
3. Set the reader identifier to
   `cloudadhar-aurora-serverless-day13-reader-1`.
4. Select Serverless v2 and use the cluster capacity range.
5. Choose a different Availability Zone from the writer when the console
   permits the choice.
6. Create the reader and wait until the cluster, writer, and reader are all
   **Available**.
7. On the cluster **Connectivity & security** tab, privately record:
   - cluster/writer endpoint;
   - reader endpoint;
   - writer instance endpoint; and
   - reader instance endpoint.

Use the stable cluster endpoint for writes and the reader endpoint for
load-balanced reads. Instance endpoints are mainly for diagnosis or deliberate
instance targeting.

## 17. Validate Aurora Writer and Reader Endpoints

Retrieve the Aurora-managed password privately from Secrets Manager. From the
existing EC2 client, connect to the cluster/writer endpoint:

```bash
mysql \
  -h <aurora-cluster-writer-endpoint> \
  -P 3306 \
  -u admin \
  -p \
  --ssl-ca=global-bundle.pem \
  --ssl-verify-server-cert \
  cloudadhardb
```

Run:

```sql
SELECT @@hostname AS writer_instance,
       @@innodb_read_only AS read_only_status;

CREATE TABLE endpoint_demo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    endpoint_type VARCHAR(40) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

INSERT INTO endpoint_demo (endpoint_type)
VALUES ('writer-endpoint');

SELECT * FROM endpoint_demo;
SHOW STATUS LIKE 'Ssl_cipher';
```

Expected: `@@innodb_read_only=0`, TLS is active, and the write succeeds.

Exit and reconnect with the same command, replacing the host with the Aurora
reader endpoint. Run:

```sql
SELECT @@hostname AS reader_instance,
       @@innodb_read_only AS read_only_status;

SELECT * FROM endpoint_demo;

INSERT INTO endpoint_demo (endpoint_type)
VALUES ('reader-write-test');
```

Expected: `@@innodb_read_only=1`, the read succeeds, and the write fails. For
Aurora MySQL v3, use `@@innodb_read_only` for this validation rather than
relying on `@@read_only`.

## 18. Perform and Validate an Aurora Cross-AZ Failover

1. Before failover, connect through the cluster/writer endpoint and record the
   sanitized result of:

```sql
SELECT @@hostname AS writer_before_failover,
       @@innodb_read_only AS read_only_status;
```

2. In **RDS -> Databases**, select the parent cluster
   `cloudadhar-aurora-serverless-day13`.
3. Choose **Actions -> Failover** and confirm.
4. Wait for the cluster and both instances to return to **Available**.
5. Verify that the previous reader became writer and the previous writer became
   reader.
6. Reconnect through the same cluster/writer endpoint and run:

```sql
SELECT @@hostname AS writer_after_failover,
       @@innodb_read_only AS read_only_status;

SELECT * FROM endpoint_demo;

INSERT INTO endpoint_demo (endpoint_type)
VALUES ('after-failover-writer');

SELECT * FROM endpoint_demo;
```

Pass when the backend hostname changes, the cluster endpoint name remains the
same, `@@innodb_read_only=0`, old data remains, and a new write succeeds.
Existing connections may be interrupted, so applications still need retry and
transaction-handling logic.

## 19. Create and Validate RDS Proxy

RDS Proxy pools and reuses database connections. It does not cache queries and
does not replace Aurora readers.

### 19.1 Configure the Security Group Path

1. Create `cloudadhar-aurora-proxy-sg-day13` in the same VPC.
2. Add inbound MySQL/Aurora TCP `3306` from
   `cloudadhar-ec2-rds-client-sg-day13`.
3. Keep only the approved outbound path needed to reach the database.
4. Add an inbound MySQL/Aurora TCP `3306` rule to
   `cloudadhar-rds-sg-day13` with source
   `cloudadhar-aurora-proxy-sg-day13`.

The intended path is:

```text
EC2 client SG --3306/TLS--> Proxy SG --3306/TLS--> Aurora database SG
```

### 19.2 Create the Proxy and Read-Only Endpoint

1. Open **RDS -> Proxies -> Create proxy**.
2. Configure:
   - Engine family: MariaDB and MySQL
   - Proxy identifier: `cloudadhar-aurora-proxy-day13`
   - Database target: `cloudadhar-aurora-serverless-day13`
   - Idle client connection timeout: 30 minutes
   - Maximum connections: 100 percent
   - Maximum idle connections: 50 percent
   - Authentication: database credentials from the Aurora master secret
   - IAM authentication: not required for this password-based lab
   - IAM role: create or select the least-privilege proxy service role
   - Require TLS: enabled
   - VPC: database VPC
   - Subnets: at least two private subnets in different AZs
   - Security Group: `cloudadhar-aurora-proxy-sg-day13`
3. Create the proxy and wait for **Available**.
4. Open the proxy's endpoints and confirm the default endpoint is
   read/write. If the creation flow did not include a reader endpoint, choose
   **Create proxy endpoint**, select **Read only**, use the same VPC/subnets
   and proxy SG, and create it.
5. Record both endpoint names privately.

### 19.3 Verify Target Health in the Console

An endpoint can be available before its database target is ready.

1. Open **RDS -> Proxies -> cloudadhar-aurora-proxy-day13**.
2. Open **Target groups**, select `default`, and inspect **Targets**.
3. Continue only when the required writer and reader targets show
   **Available**. If a target reports pending proxy capacity, wait without
   repeatedly modifying the proxy.

### 19.4 Test Both Proxy Endpoints

Connect from EC2 to the proxy read/write endpoint using the same TLS options:

```bash
mysql \
  -h <proxy-read-write-endpoint> \
  -P 3306 \
  -u admin \
  -p \
  --ssl-ca=global-bundle.pem \
  --ssl-verify-server-cert \
  cloudadhardb
```

Run:

```sql
SELECT @@hostname AS proxy_writer_backend,
       @@innodb_read_only AS read_only_status;
SHOW STATUS LIKE 'Ssl_cipher';
INSERT INTO endpoint_demo (endpoint_type) VALUES ('rds-proxy-writer');
SELECT * FROM endpoint_demo;
```

Expected: read-only status is `0`, TLS is active, and the insert succeeds.

Reconnect through the read-only proxy endpoint and run:

```sql
SELECT @@hostname AS proxy_reader_backend,
       @@innodb_read_only AS read_only_status;
SELECT * FROM endpoint_demo;
INSERT INTO endpoint_demo (endpoint_type)
VALUES ('proxy-reader-write-test');
```

Expected: the read succeeds and the write fails in read-only mode.

## 20. Aurora Global Database Decision Challenge

Document, but do not deploy without explicit instructor approval:

1. The primary Region accepts writes during normal operation.
2. Secondary Regions serve local reads and provide cross-Region recovery.
3. Cross-Region replication is asynchronous, so an unplanned recovery can
   have non-zero data loss.
4. Use a planned switchover for a controlled regional transition and managed
   failover for disaster recovery.

```text
Users in Region A -> Primary Aurora cluster -> async replication
                                             -> Secondary Aurora cluster
                                                local reads / DR
```

Creating the secondary cluster and instance is an optional paid extension.
Do not initiate a cross-Region failover in a shared environment.

## 21. AWS DMS Decision Challenge

Open **AWS DMS** and identify:

1. Replication capacity or replication instance/serverless configuration.
2. Source endpoint.
3. Target endpoint.
4. Migration task.
5. Full load.
6. CDC only.
7. Full load plus CDC.

For the scenario below, choose **Full load plus CDC** and write the sequence:

```text
Source: cloudadhar-rds-day13 / cloudadhardb.orders
Target: Aurora MySQL / cloudadhardb.orders
Goal: low-downtime migration
```

1. Prepare the source engine for DMS.
2. Create private DMS networking and replication capacity.
3. Create and test the source and target endpoints using Secrets Manager.
4. Map `cloudadhardb.orders` and run premigration assessment.
5. Start Full load plus CDC and validate row counts and ongoing changes.
6. Pause application writes briefly at cutover.
7. Allow replication lag to reach zero.
8. Redirect the application to Aurora and monitor.

Do not create paid DMS resources without explicit approval. DMS moves data;
heterogeneous migrations can also require schema conversion and application
testing.

## 22. Automate a Logical Table Backup with Systems Manager

Native RDS automated backups, snapshots, and PITR protect the complete
database. This extension creates a separate logical export of only the
`orders` table by running an SSM Command document on the EC2 client and
scheduling it with State Manager.

```text
State Manager schedule -> SSM Command document -> EC2 client
                                                   |-- read backup secret
                                                   |-- dump orders over TLS
                                                   `-- upload .sql.gz to S3
```

### 22.1 Create the Private Backup Bucket

1. Open **Amazon S3 -> Buckets -> Create bucket**.
2. Use `cloudadhar-rds-table-backups-<account-id>-ap-south-1`, replacing the
   placeholder with the current account ID. Add a short learner suffix only if
   the globally unique name is already taken.
3. Select Mumbai, `ap-south-1`.
4. Keep Object Ownership set to **Bucket owner enforced**.
5. Keep all **Block Public Access** settings enabled.
6. Enable versioning.
7. Enable default encryption with **Amazon S3 managed keys (SSE-S3)** for this
   lab. A customer-managed KMS key requires additional least-privilege KMS
   permissions.
8. Add Day 13 tags and create the bucket.

Do not create a public bucket policy or an empty folder object. The first
upload creates the `day13/mysql-table-backups/` prefix naturally.

### 22.2 Create a Dedicated Backup User and Secret

Use a dedicated database user rather than the master user for scheduled
exports.

1. Connect from EC2 to the primary RDS endpoint as `admin` using TLS.
2. While not screen sharing, create a strong unique password and run:

```sql
CREATE USER 'backup_user'@'%' IDENTIFIED BY '<strong-unique-password>';
GRANT SELECT ON cloudadhardb.orders TO 'backup_user'@'%';
```

Do not save or publish the password. Disable or clear local client history in
accordance with the instructor's credential-handling policy.

3. Open **Secrets Manager -> Store a new secret**.
4. Choose **Other type of secret** and add these key/value pairs in the
   console, replacing every placeholder:

```json
{
  "username": "backup_user",
  "password": "<strong-unique-password>",
  "host": "<private-rds-primary-endpoint>",
  "port": 3306,
  "dbname": "cloudadhardb"
}
```

5. Name the secret `cloudadhardb-backup-secret-day13`.
6. Use the default Secrets Manager encryption key for the lab, add tags, and
   create the secret.
7. Record its ARN privately without exposing the secret value.

If an existing secret already contains all five required keys and is approved
for this workload, reuse it rather than creating a duplicate.

### 22.3 Add Least-Privilege Permissions to the EC2 Role

The EC2 instance role lets the managed node use SSM, retrieve the one backup
secret, and write only to the backup prefix. It is different from the State
Manager association dispatch role.

1. Open **IAM -> Roles -> cloudadhar-ec2-ssm-role-day13**.
2. Confirm `AmazonSSMManagedInstanceCore` is attached.
3. Choose **Add permissions -> Create inline policy -> JSON**.
4. Replace the bucket and secret placeholders, then add:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListBackupPrefix",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::cloudadhar-rds-table-backups-<account-id>-ap-south-1",
      "Condition": {
        "StringLike": {
          "s3:prefix": "day13/mysql-table-backups/*"
        }
      }
    },
    {
      "Sid": "ManageTableBackupObjects",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:AbortMultipartUpload"
      ],
      "Resource": "arn:aws:s3:::cloudadhar-rds-table-backups-<account-id>-ap-south-1/day13/mysql-table-backups/*"
    },
    {
      "Sid": "ReadDatabaseBackupSecret",
      "Effect": "Allow",
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "<backup-secret-arn>"
    }
  ]
}
```

5. Name the inline policy `CloudAdharDay13TableBackupAccess` and save it.
6. If the secret or bucket uses a customer-managed KMS key, separately allow
   only the required KMS operations on that exact key.
7. Allow instance-profile credentials to refresh, then confirm the node is
   **Online** in **Systems Manager -> Fleet Manager**.

### 22.4 Verify the Managed-Node Prerequisites

Connect with Session Manager and run only inside the EC2 client:

```bash
sudo dnf install -y mariadb105 jq gzip

curl -fsSL \
  https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem \
  -o /tmp/global-bundle.pem

mariadb --version || mysql --version
aws --version
jq --version
```

Do not print the secret during a shared screen or place its value in shell
history.

### 22.5 Create the SSM Command Document

1. Open **Systems Manager -> Documents**.
2. Choose **Create document -> Command or Session**.
3. Set:
   - Name: `CloudAdhar-RDS-MySQL-Table-Backup-To-S3`
   - Document type: **Command**
   - Format: **YAML**
4. Paste the complete document below and choose **Create document**:

```yaml
schemaVersion: '2.2'
description: Export one RDS MySQL table and upload the compressed dump to S3.
parameters:
  TableName:
    type: String
    description: MySQL table to back up
    allowedPattern: '^[A-Za-z0-9_]+$'
    interpolationType: ENV_VAR
  SecretArn:
    type: String
    description: Secret containing username, password, host, port and dbname
    allowedPattern: '^arn:aws[a-zA-Z-]*:secretsmanager:[a-z0-9-]+:[0-9]{12}:secret:[A-Za-z0-9/_+=.@-]+$'
    interpolationType: ENV_VAR
  BackupBucket:
    type: String
    description: Destination bucket without s3://
    allowedPattern: '^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$'
    interpolationType: ENV_VAR
  BackupPrefix:
    type: String
    description: Destination prefix without a leading slash
    default: day13/mysql-table-backups
    allowedPattern: '^[A-Za-z0-9/_-]+$'
    interpolationType: ENV_VAR
mainSteps:
  - action: aws:runShellScript
    name: BackupMySQLTableToS3
    inputs:
      timeoutSeconds: '1800'
      runCommand:
        - |
          #!/bin/bash
          set -Eeuo pipefail

          TABLE_NAME="${SSM_TableName}"
          SECRET_ARN="${SSM_SecretArn}"
          BACKUP_BUCKET="${SSM_BackupBucket}"
          BACKUP_PREFIX="${SSM_BackupPrefix%/}"
          WORK_DIR="/opt/cloudadhar/rds-table-backup"
          CA_FILE="${WORK_DIR}/global-bundle.pem"
          TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"

          install -d -m 0700 "${WORK_DIR}"

          command -v jq >/dev/null 2>&1 || dnf install -y jq
          if ! command -v mariadb-dump >/dev/null 2>&1 && \
             ! command -v mysqldump >/dev/null 2>&1; then
            dnf install -y mariadb105
          fi

          if [[ ! -s "${CA_FILE}" ]]; then
            curl -fsSL \
              https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem \
              -o "${CA_FILE}"
            chmod 0644 "${CA_FILE}"
          fi

          SECRET_JSON="$(aws secretsmanager get-secret-value \
            --secret-id "${SECRET_ARN}" \
            --query SecretString \
            --output text)"

          DB_USER="$(jq -er '.username' <<<"${SECRET_JSON}")"
          DB_PASSWORD="$(jq -er '.password' <<<"${SECRET_JSON}")"
          DB_HOST="$(jq -er '.host' <<<"${SECRET_JSON}")"
          DB_PORT="$(jq -er '.port // 3306' <<<"${SECRET_JSON}")"
          DB_NAME="$(jq -er '.dbname // .database' <<<"${SECRET_JSON}")"
          unset SECRET_JSON

          CREDENTIAL_FILE="$(mktemp "${WORK_DIR}/client.XXXXXX.cnf")"
          BACKUP_BASENAME="${DB_NAME}-${TABLE_NAME}-${TIMESTAMP}.sql.gz"
          BACKUP_FILE="${WORK_DIR}/${BACKUP_BASENAME}"
          trap 'rm -f "${CREDENTIAL_FILE}" "${BACKUP_FILE}"' EXIT
          chmod 0600 "${CREDENTIAL_FILE}"

          if command -v mariadb-dump >/dev/null 2>&1; then
            DUMP_TOOL="$(command -v mariadb-dump)"
            cat >"${CREDENTIAL_FILE}" <<EOF
          [client]
          user=${DB_USER}
          password=${DB_PASSWORD}
          host=${DB_HOST}
          port=${DB_PORT}
          ssl-ca=${CA_FILE}
          ssl-verify-server-cert
          EOF
          else
            DUMP_TOOL="$(command -v mysqldump)"
            cat >"${CREDENTIAL_FILE}" <<EOF
          [client]
          user=${DB_USER}
          password=${DB_PASSWORD}
          host=${DB_HOST}
          port=${DB_PORT}
          ssl-ca=${CA_FILE}
          ssl-mode=VERIFY_IDENTITY
          EOF
          fi

          "${DUMP_TOOL}" \
            --defaults-extra-file="${CREDENTIAL_FILE}" \
            --single-transaction \
            --quick \
            --skip-lock-tables \
            --no-tablespaces \
            "${DB_NAME}" "${TABLE_NAME}" | gzip -9 >"${BACKUP_FILE}"

          test -s "${BACKUP_FILE}"
          aws s3 cp \
            "${BACKUP_FILE}" \
            "s3://${BACKUP_BUCKET}/${BACKUP_PREFIX}/${BACKUP_BASENAME}" \
            --only-show-errors

          aws s3api head-object \
            --bucket "${BACKUP_BUCKET}" \
            --key "${BACKUP_PREFIX}/${BACKUP_BASENAME}" \
            --query '{Bytes:ContentLength,Encryption:ServerSideEncryption}'

          echo "Backup completed: s3://${BACKUP_BUCKET}/${BACKUP_PREFIX}/${BACKUP_BASENAME}"
```

The opening `schemaVersion: '2.2'` is mandatory. Environment-variable
interpolation and restrictive patterns reduce command-injection risk. Keep the
SSM Agent current so it supports these document features.

### 22.6 Test the Document Once with Run Command

Do not schedule an untested document.

1. Open **Systems Manager -> Run Command -> Run command**.
2. Select `CloudAdhar-RDS-MySQL-Table-Backup-To-S3`.
3. Enter:

| Parameter | Value |
|---|---|
| Table Name | `orders` |
| Secret ARN | ARN of `cloudadhardb-backup-secret-day13` |
| Backup Bucket | The bucket name without `s3://` |
| Backup Prefix | `day13/mysql-table-backups` |

4. Select the SSM-managed EC2 database client and run the command.
5. Confirm command status is **Success**.
6. Open the S3 prefix and verify a non-empty timestamped object such as:

```text
day13/mysql-table-backups/cloudadhardb-orders-20260816T120000Z.sql.gz
```

7. Download this synthetic-data backup to the EC2 client and validate it:

```bash
gzip -t cloudadhardb-orders-<timestamp>.sql.gz
gzip -dc cloudadhardb-orders-<timestamp>.sql.gz | head
```

Do not restore the dump over the active class database. Use a separate
temporary database if the instructor approves a restore test.

### 22.7 Create the Association Dispatch Role

Do not select the EC2 instance role as the dispatch role. The EC2 role trusts
`ec2.amazonaws.com`; State Manager requires a separate role that trusts
`ssm.amazonaws.com` and can dispatch the approved document to the approved
instance.

1. Open **IAM -> Roles -> Create role -> Custom trust policy**.
2. Paste:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"Service": "ssm.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }
  ]
}
```

3. Name the role `cloudadhar-ssm-association-dispatch-day13`.
4. Add an inline policy after replacing the account and instance placeholders:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "SendBackupCommand",
      "Effect": "Allow",
      "Action": "ssm:SendCommand",
      "Resource": [
        "arn:aws:ssm:ap-south-1:<account-id>:document/CloudAdhar-RDS-MySQL-Table-Backup-To-S3",
        "arn:aws:ec2:ap-south-1:<account-id>:instance/<instance-id>"
      ]
    }
  ]
}
```

5. Name the policy `CloudAdharDay13AssociationDispatch` and save it.

AWS currently recommends a custom dispatch role because it gives explicit
permission control. If the account uses a supported service-linked-role path,
follow the console guidance. A selected custom role must trust
`ssm.amazonaws.com`.

### 22.8 Create the Scheduled State Manager Association

1. Tag the EC2 client with `BackupWorker=RDS-Table-Backup`.
2. Open **Systems Manager -> State Manager -> Create association**.
3. Set:
   - Name: `cloudadhar-rds-orders-backup-daily`
   - Document: `CloudAdhar-RDS-MySQL-Table-Backup-To-S3`
   - Document version: **Default at runtime**
4. Enter the same four parameters used in the successful Run Command test.
5. Target only the EC2 client, either by selecting it directly or using the
   tag `BackupWorker=RDS-Table-Backup`.
6. Select the dedicated association dispatch role.
7. Choose **On Schedule** and use `rate(24 hours)`.
8. Set compliance severity to **Low**, concurrency to **1 target**, and error
   threshold to **1 target**.
9. Optionally send command logs to a separate private S3 logging prefix. This
   stores execution output, not the `.sql.gz` database backup.
10. Create the association. State Manager normally runs a new association
    immediately and then on its schedule.
11. If it does not run immediately, choose **Apply association now**.

### 22.9 Validate the Scheduled Backup

Confirm:

- [ ] Association execution and detailed status are **Success**.
- [ ] A new timestamped `.sql.gz` object exists under the backup prefix.
- [ ] Object size is greater than zero and server-side encryption is present.
- [ ] Output shows the object URI but never the database password.
- [ ] A second manual association run creates a second timestamped object.
- [ ] `gzip -t` succeeds on a downloaded synthetic backup.

### 22.10 Restore and Validate a Backup from S3

Never restore the logical dump over the active `cloudadhardb` database. Use a
separate temporary schema so the test cannot overwrite the source table.

The required sequence is:

```text
S3 object -> download to EC2 -> gzip validation -> local decompression
          -> import into isolated MySQL database -> validate -> remove test data
```

#### Phase A - Download the Backup from S3 to EC2

1. In the S3 console, select one successful timestamped `.sql.gz` object and
   copy its S3 URI. Do not use a backup created before the `orders` table
   existed.
2. Connect to the EC2 client with Session Manager and create a private working
   directory. Replace the two placeholders with the copied URI and exact
   timestamped filename:

```bash
restore_dir=/tmp/cloudadhar-day13-restore
install -d -m 0700 "${restore_dir}"

aws s3 cp \
  "s3://<backup-bucket>/day13/mysql-table-backups/<backup-file>.sql.gz" \
  "${restore_dir}/<backup-file>.sql.gz" \
  --only-show-errors

gzip -t "${restore_dir}/<backup-file>.sql.gz"
gzip -dk "${restore_dir}/<backup-file>.sql.gz"
chmod 0600 "${restore_dir}/<backup-file>.sql"
```

Expected: the download succeeds and `gzip -t` returns no error.

Do not begin the database import until the compressed backup exists on EC2 and
passes `gzip -t`.

#### Phase B - Import the Downloaded Backup into MySQL

3. Prevent this training session from recording SQL history, then connect to
   the private RDS primary as `admin` using TLS. Enter the password only at the
   prompt:

```bash
export MYSQL_HISTFILE=/dev/null

mysql \
  -h <private-rds-primary-endpoint> \
  -P 3306 \
  -u admin \
  -p \
  --ssl-ca=global-bundle.pem \
  --ssl-verify-server-cert
```

4. Inside the MySQL client, create the isolated target and import the file.
   Replace `<backup-file>` with the same filename without `.sql.gz`:

```sql
CREATE DATABASE cloudadhardb_restore_test;
USE cloudadhardb_restore_test;
SOURCE /tmp/cloudadhar-day13-restore/<backup-file>.sql;

SHOW TABLES;
SELECT COUNT(*) AS restored_rows FROM orders;
SELECT * FROM orders ORDER BY order_id;
```

5. In the same session, compare the active and restored tables:

```sql
SELECT
  (SELECT COUNT(*) FROM cloudadhardb.orders) AS current_source_rows,
  (SELECT COUNT(*) FROM cloudadhardb_restore_test.orders) AS restored_backup_rows;
```

The counts should match when the source did not change after the backup. If
they differ, confirm that the restored rows correctly represent the selected
backup timestamp; a logical backup is a point-in-time copy.

6. Capture sanitized evidence showing the restored table and rows. Then remove
   only the temporary test schema:

```sql
DROP DATABASE cloudadhardb_restore_test;
SHOW DATABASES LIKE 'cloudadhardb_restore_test';
EXIT;
```

7. Remove only the explicitly named temporary restore files from EC2:

```bash
rm -f \
  "${restore_dir}/<backup-file>.sql" \
  "${restore_dir}/<backup-file>.sql.gz"
rmdir "${restore_dir}"
```

Pass conditions:

- the chosen S3 object downloads successfully;
- gzip integrity validation succeeds;
- the dump creates `orders` only in `cloudadhardb_restore_test`;
- restored rows are readable and match the selected backup point;
- the active `cloudadhardb.orders` table is unchanged; and
- the temporary schema and local files are removed after evidence.

### 22.11 Troubleshoot Safely

| Symptom | Likely cause | Correction |
|---|---|---|
| `Missing schemaVersion` | Incomplete SSM document | Paste the complete document beginning with schema version `2.2` |
| `GetSecretValue` denied | EC2 role cannot read the exact secret | Correct the secret ARN in the EC2 role policy |
| `InvalidAssociationDispatchAssumeRole` | EC2 role selected as dispatch role | Use the role trusted by `ssm.amazonaws.com` |
| `s3 cp` denied | Incorrect bucket or object ARN | Correct the exact bucket/prefix policy |
| Dump command missing | Client package absent | Install the compatible MariaDB/MySQL client |
| TLS failure | Missing CA or wrong endpoint | Verify CA bundle and secret host |
| Empty or failed export | Wrong table or insufficient grant | Verify `orders` and the backup-user privilege |
| Import says table exists | Active database selected accidentally | Stop and use the empty `cloudadhardb_restore_test` schema |
| Restored count differs | Source changed after selected backup | Compare against the backup timestamp, not later source state |

Standard SSM document parameters accept strings or statically allowed values;
they do not dynamically discover RDS databases and tables for dropdown lists.
Dynamic discovery requires a separate approved application or Automation
workflow and does not justify broad access to every secret.

Official references:

- [SSM document schemas and features](https://docs.aws.amazon.com/systems-manager/latest/userguide/documents-schemas-features.html)
- [Creating State Manager associations](https://docs.aws.amazon.com/systems-manager/latest/userguide/state-manager-associations-creating.html)
- [How State Manager uses association dispatch roles](https://docs.aws.amazon.com/systems-manager/latest/userguide/state-manager-about.html)

## Troubleshooting Order

1. Account and Region.
2. Database status is **Available**.
3. EC2 and RDS VPC, DNS, subnets, and routes.
4. RDS SG references the client SG on TCP `3306`.
5. Endpoint, port, username, and initial database name.
6. Current RDS-managed secret.
7. RDS CA bundle and server-certificate verification.
8. For PITR: automated backups, restorable window, InnoDB, and selected time.
9. For replica: rule out lag or replication failure.
10. For Aurora: confirm the endpoint type and `@@innodb_read_only` value.
11. For Proxy: check endpoint status, target health, secrets, IAM role, TLS,
    client-to-proxy SG, and proxy-to-database SG.
12. For table backup: check managed-node status, exact secret and S3 ARNs,
    database grant, dispatch-role trust, document version, and association
    execution detail.
13. RDS events, CloudWatch metrics, and engine logs without exposing secrets.

## Evidence Checklist

- [ ] Private RDS, VPC, subnet group, and SG-to-SG access
- [ ] Encryption, backups, and managed credentials
- [ ] TLS connection with non-empty cipher
- [ ] Three synthetic `orders` rows and InnoDB engine
- [ ] Manual snapshot `Available`
- [ ] Retention, backup window, and latest restorable time
- [ ] PITR insert/delete UTC window and completed restored-database validation
- [ ] Read replica `Available` and separate endpoint
- [ ] Replicated row, read-only value, replication health, and failed write
- [ ] Aurora Serverless v2 writer and reader `Available`
- [ ] Aurora writer read/write success and reader failed-write proof
- [ ] Cross-AZ failover with stable cluster endpoint and changed backend writer
- [ ] RDS Proxy read/write and read-only endpoints with healthy targets
- [ ] Proxy TLS, successful writer insert, reader select, and failed reader write
- [ ] Multi-AZ, Global Database, DMS, and logical-backup decision notes
- [ ] Private versioned encrypted backup bucket and least-privilege EC2 policy
- [ ] SSM Command document schema `2.2` and successful Run Command test
- [ ] Dedicated dispatch role and daily State Manager association
- [ ] Two non-empty encrypted `.sql.gz` objects and successful gzip validation
- [ ] S3 download and isolated restore into `cloudadhardb_restore_test`
- [ ] Restored rows validated without changing the active database
- [ ] Temporary restore schema and EC2 files removed
- [ ] One troubleshooting lesson with symptom, root cause, and fix

Proceed to [06-cleanup.md](./06-cleanup.md) after evidence.
