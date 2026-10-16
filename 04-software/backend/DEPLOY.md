# Deploy the backend on AWS EC2

One small CPU server runs the HiGHS API and Caddy for HTTPS. It needs no GPU,
database, load balancer, NAT gateway or paid container registry. Existing API
paths stay at the hostname root. There is no frontend source in this repository;
its API base URL must be updated separately.

## Recommended starting instance

For occasional demos and one solve at a time:

| Setting | Value |
|---|---|
| Region | `ap-south-1` (Mumbai): inexpensive T4g pricing, also close to India |
| Instance | `t4g.small`: 2 ARM vCPUs, 2 GiB RAM |
| OS | Ubuntu Server 24.04 LTS, **64-bit Arm**, standard free Ubuntu AMI |
| Storage | 8 GiB encrypted gp3, default IOPS/throughput, delete on termination |
| Purchase model | On-Demand, CPU credits **Standard** |
| Networking | Public subnet, internet gateway and one public IPv4 |
| Inbound | TCP 80/443 from internet; TCP 22 only from your own IP |
| Metadata | Require IMDSv2; no application AWS credentials or IAM role needed |

2 GiB provides room for the OS, API, proxy and bounded solver process. Compose
limits target this size. A micro has only 1 GiB; do not downsize without reducing
worker/container limits and measuring your largest uploads. A nano is too tight
for this configuration. Spot interruptions are unsuitable for a dependable demo.

### Cost, checked 26 September 2026

AWS currently offers **750 aggregate t4g.small hours/month through 31 December
2026**. The allowance is shared across regions and, under consolidated billing,
across the organization. Confirm remaining allowance in your account. Only
instance compute is covered; CPU-credit overages and other resources are
separate. [AWS T4g trial terms](https://aws.amazon.com/ec2/faqs/)

The official Mumbai price list quotes Linux shared-tenancy `t4g.small` at
**$0.0112/hour** (about **$8.18/month** at 730 hours), and `t4g.micro` at
$0.0056/hour. Covered compute is $0 during the small-instance trial.
[AWS regional price list](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/ap-south-1/index.csv)

Budget another **$3.65/month for one public IPv4**, plus the small gp3 volume,
bandwidth beyond included allowances, taxes and any domain registration. Expect
roughly **$4–5/month during the trial and $12–13/month afterward**, before
taxes/domain/extra traffic. A static Elastic IP has the same IPv4 hourly charge;
keep only one and release it when finished. Recheck prices at launch.
[IPv4 pricing](https://aws.amazon.com/vpc/pricing/),
[EBS pricing](https://aws.amazon.com/ebs/pricing/)

Set CPU credits to **Standard**, explicitly. Unlimited can add charges during
sustained computation. Standard avoids surplus-credit charges but throttles
when credits run out. This suits intermittent demos, not sustained full-CPU
throughput. Watch CPUCreditBalance, CPU use and memory under real traffic.
[AWS burstable performance modes](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/burstable-performance-instances-how-to.html)

## 1. Create the server in the AWS console

Use a checkout of the published
[HyperGrey-SIH-26 repository](https://github.com/InsaneJSK/HyperGrey-SIH-26).
The backend is in `04-software/backend/`, relative to the repository root.
For a new checkout:

```sh
git clone https://github.com/InsaneJSK/HyperGrey-SIH-26.git
cd HyperGrey-SIH-26
```

The upload example in step 3 uses Windows PowerShell from this repository root.
The server commands run in the EC2 Ubuntu shell.

1. Open **EC2** and select **Asia Pacific (Mumbai), ap-south-1**.
2. Choose **Launch instance**, with name `sih-backend`.
3. Select the standard Canonical **Ubuntu Server 24.04 LTS** AMI and **64-bit Arm**.
   Select `t4g.small` as the instance type.
4. Create an RSA key pair named `sih-backend`, format **.pem**, and save the
   downloaded `sih-backend.pem` in your Windows Downloads folder.
5. In Network settings, choose the default VPC and a public subnet, and enable
   auto-assigned public IPv4. Create security group `sih-backend-sg` with:
   TCP 22 from **My IP**, TCP 80 from `0.0.0.0/0`, and TCP 443 from `0.0.0.0/0`.
   Leave the default outbound rule. Port 8000 stays closed.
6. Set the root volume to **8 GiB gp3**, encrypted, with delete-on-termination.
7. In Advanced details, set **Credit specification → Standard** and
   **Metadata version → V2 only (token required)**. Leave User data empty for
   this walkthrough; we run the bundled bootstrap after uploading the files.
8. Launch one instance and wait for its status checks to pass.

A default VPC normally supplies the internet gateway and public routing. If your
account has no default VPC, create/choose a VPC with a public subnet routed to an
internet gateway; this deployment does not need a NAT gateway.

[EC2 launch instructions](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html),
[credit specification settings](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/burstable-performance-instances-how-to.html)

## 2. Give it a stable public address

In **EC2 → Network & Security → Elastic IP addresses**, choose **Allocate
Elastic IP address** in this region. Then select it, choose **Actions → Associate
Elastic IP address**, choose resource type **Instance**, and select
`sih-backend` and its primary private IPv4. Associate the address.

Copy this **Elastic IP** for the commands below. It replaces the automatically
assigned public IP and stays stable across stop/start operations. Do not keep
an extra unused allocation. Set a billing budget alert for the project.
[Elastic IP association](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/working-with-eips.html)

## 3. Package and upload the backend — Windows PowerShell

Open PowerShell at the root of your repository checkout. This creates an archive
containing only the required runtime/deployment files; it excludes local
environment files, virtual environments, caches and the research folders.

Run this block; enter the Elastic IP when prompted. Change `$KeyPath` if you
saved your key elsewhere.

```powershell
$Backend = (Resolve-Path -LiteralPath "04-software/backend").Path
$KeyPath = Join-Path $env:USERPROFILE "Downloads\sih-backend.pem"
$Archive = Join-Path $env:TEMP "sih-backend-deploy.tar.gz"
$Ec2Ip = Read-Host "Paste the instance's Elastic IP"

if (-not (Test-Path -LiteralPath $KeyPath)) {
    throw "Key file not found: $KeyPath"
}

$DeployFiles = @(
    "app.py", "solve.py", "worker.py", "config.py", "limits.py",
    "requirements.txt", "Dockerfile", ".dockerignore",
    "compose.yaml", "Caddyfile", ".env.example", "smoke_test.py",
    "THIRD_PARTY_NOTICES.md", "examples", "licences",
    "deploy/ec2-user-data.sh"
)
tar -czf "$Archive" -C "$Backend" @DeployFiles
if ($LASTEXITCODE -ne 0) { throw "Could not create deployment archive" }

scp -i "$KeyPath" "$Archive" "ubuntu@${Ec2Ip}:sih-backend-deploy.tar.gz"
if ($LASTEXITCODE -ne 0) { throw "Upload failed" }

ssh -i "$KeyPath" "ubuntu@$Ec2Ip"
```

The last command opens a shell **on EC2**. Ubuntu's login user is `ubuntu`.
On the first SSH connection, OpenSSH asks to trust the host key; confirm that
you are connecting to the Elastic IP assigned to this instance.
[AWS SSH](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/connect-linux-inst-ssh.html),
[SCP](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/linux-file-transfer-scp.html)

If OpenSSH reports that the private key file's permissions are too open, use
these commands in local PowerShell, then retry SCP/SSH:

```powershell
$KeyOwner = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
icacls.exe "$KeyPath" /inheritance:r
icacls.exe "$KeyPath" /grant:r "${KeyOwner}:(R)"
```

## 4. Install Docker and start the API — EC2 Ubuntu shell

Run these commands in the SSH session, not in PowerShell:

```bash
sudo cloud-init status --wait
sudo install -d -m 0755 -o ubuntu -g ubuntu /opt/refinery/backend
tar -xzf "$HOME/sih-backend-deploy.tar.gz" -C /opt/refinery/backend
cd /opt/refinery/backend

sudo bash deploy/ec2-user-data.sh
sudo docker version
sudo docker compose version

if [ ! -f .env ]; then cp .env.example .env; fi
sudo docker compose config --quiet
sudo docker compose up -d --build --wait --wait-timeout 180

sudo docker compose ps
python3 smoke_test.py http://localhost
```

The bootstrap verifies Ubuntu 24.04, installs `docker.io`,
`docker-compose-v2` and certificates, and enables Docker at boot. First build
can take several minutes, especially while Standard-mode CPU credits are low.
The 180-second Compose wait applies to service readiness after building.

Expect `ALL PASS`. Health should be:

```json
{"ok": true, "engine": "reference"}
```

`reference` means **HiGHS**. `GET /capabilities` identifies HiGHS 1.12.0.
The initial configuration is HTTP-only on public port 80. You can check it
from your computer with `curl.exe http://YOUR_ELASTIC_IP/health`.

If any command fails, inspect the failure before continuing. These diagnostics
show container status, startup failures and disk availability:

```bash
sudo docker compose ps -a
sudo docker compose logs --tail=100 api proxy
df -h /
```

If Ubuntu cannot locate `docker-compose-v2`, check that the Ubuntu Universe
repository is enabled; that is where Ubuntu provides this package.
[Ubuntu package](https://packages.ubuntu.com/noble/docker-compose-v2)

## 5. Configure the API domain and HTTPS

Use a subdomain you control, for example `api.your-domain.com`. In your DNS
provider, add this record:

| DNS field | Value |
|---|---|
| Type | A |
| Name/host | `api` (some providers expect the complete hostname) |
| Value | The EC2 Elastic IP |
| TTL | 300 seconds or the provider default |

Initially use ordinary DNS-only routing if the provider offers an optional
proxy. Remove a stale AAAA record unless you have configured working IPv6.
This does not require transferring DNS to Route 53 or buying another domain.

Once DNS resolves to your Elastic IP, run the block below **on EC2**, replacing
the first two values with your actual API hostname and frontend origin.
`API_DOMAIN` is a hostname only; `FRONTEND_ORIGIN` includes `https://`
and has no trailing slash or path. Multiple origins may be comma-separated.

```bash
cd /opt/refinery/backend
API_DOMAIN='api.your-domain.com'
FRONTEND_ORIGIN='https://your-frontend.example'

getent ahostsv4 "$API_DOMAIN"
printf 'API_ADDRESS=%s\nCORS_ORIGINS=%s\n' "$API_DOMAIN" "$FRONTEND_ORIGIN" > .env

sudo docker compose config --quiet
sudo docker compose up -d --wait --wait-timeout 180

curl --retry 6 --retry-all-errors --retry-delay 5 --max-time 10 -fsS "https://${API_DOMAIN}/health"
python3 smoke_test.py "https://${API_DOMAIN}"
```

Check that the DNS output contains your Elastic IP. Caddy obtains/renews the
certificate automatically while ports 80 and 443 are reachable; it stores
certificate data in Docker volumes. Initial certificate issuance may take a
minute. If HTTPS fails, inspect `sudo docker compose logs --tail=100 proxy`
and check DNS and the security-group rules.
[Caddy automatic HTTPS](https://caddyserver.com/docs/automatic-https)

Without a domain, you can stop after the HTTP smoke test to validate the server.
Complete HTTPS before connecting an HTTPS frontend; browsers block calls from
an HTTPS page to an HTTP API.

## 6. Connect and check the frontend

Set your frontend's existing API-base setting to:

```text
https://api.your-domain.com
```

Keep the variable name already used by your frontend. For a Vite frontend, a
name such as `VITE_API_BASE_URL` is an example, not an established setting in this
repository. Rebuild/redeploy when that setting is incorporated at build time.

Keep paths `/solve`, `/examples`, `/refinery/plan` and
`/refinery/sensitivity`, without an `/api` prefix. Apply the frontend handling
described in [FRONTEND_MIGRATION.md](FRONTEND_MIGRATION.md), particularly 429
responses, nullable results and incomplete sensitivity curves.

On EC2, using the variables set above, check browser preflight:

```bash
curl -i -X OPTIONS "https://${API_DOMAIN}/solve" \
  -H "Origin: ${FRONTEND_ORIGIN%%,*}" \
  -H 'Access-Control-Request-Method: POST' \
  -H 'Access-Control-Request-Headers: content-type'
```

Expect HTTP 200 and `Access-Control-Allow-Origin` matching the first origin.
Then run a real refinery plan and production solve from the frontend.
A public demo request needs Content-Type: application/json; there is no API key
or cookie authentication. CORS is not authentication. Add authentication if
you later make the service private.

## 7. Update and operate it

For a later update, recreate the archive and upload it using step 3. On EC2:

```bash
cd /opt/refinery/backend
tar -xzf "$HOME/sih-backend-deploy.tar.gz" -C /opt/refinery/backend
sudo docker compose up -d --build --wait --wait-timeout 180
python3 smoke_test.py https://api.your-domain.com
```

The archive excludes `.env`, so it preserves your deployed hostname and CORS
settings. Replace the smoke-test hostname with your own. To inspect operations:

```bash
sudo docker compose ps
sudo docker compose logs --tail=100 api proxy
sudo docker stats --no-stream
df -h /
```

Containers restart after crashes or host reboot; logs rotate. Health checks
mark unhealthy processes but do not themselves trigger restarts. Keep exactly
one API worker: additional workers bypass the single-process admission limit.
Uploaded models and results are temporary, with no persistent job history.

Monitor the small root volume and review images before removing obsolete ones.
Do not use `docker compose down --volumes` as an update command: it would remove
the stored certificate data. Increase worker/upload limits only alongside
container memory and host RAM.

Stopping EC2 retains storage and allocated Elastic IP charges. When retiring
the demo, terminate the instance, delete unneeded volumes/snapshots and release
its Elastic IP. The instructions here create resources only when you run the
AWS launch steps.
