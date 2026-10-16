#!/usr/bin/env bash
# EC2 user data for the standard Ubuntu Server 24.04 LTS ARM64 AMI.
set -euo pipefail
source /etc/os-release
if [[ "$ID" != ubuntu || "$VERSION_ID" != 24.04 ]]; then
    echo 'This bootstrap requires Ubuntu Server 24.04 LTS.' >&2
    exit 1
fi
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y docker.io docker-compose-v2 ca-certificates
systemctl enable --now docker
install -d -m 0755 -o ubuntu -g ubuntu /opt/refinery
docker compose version
