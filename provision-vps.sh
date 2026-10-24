#!/usr/bin/env bash
set -euo pipefail
if [ "$(id -u)" -ne 0 ]; then echo "Run as root on a fresh Ubuntu VPS."; exit 1; fi
apt-get update
apt-get install -y ca-certificates curl git ufw openssl
./deploy/install-docker.sh
./deploy/configure-firewall.sh
echo "VPS prerequisites installed. Clone this repository and run ./deploy/one-click.sh"
