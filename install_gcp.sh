#!/bin/bash

# RabbitHole v3.2 (SECURED) - Google Cloud Installer
# Optimized for e2-micro (Free Tier) with Swap & Security Hardening

# ==============================================================================
# DEPLOYMENT GUIDE (For the Operator)
# ==============================================================================
# 1. Create VM:
#    - Launch an 'e2-micro' instance on Google Cloud Platform (GCP).
#    - Select OS: Ubuntu 22.04 LTS (x86/64).
#    - Enable "Allow HTTP traffic" and "Allow HTTPS traffic" in the firewall settings.
#
# 2. Upload Files:
#    - From your local machine (Laptop/PC), run:
#      scp -r gemini-cli/ <GCP_USER>@<YOUR_GCP_VM_IP>:~/
#
# 3. Run Installer:
#    - SSH into your GCP VM:
#      ssh <GCP_USER>@<YOUR_GCP_VM_IP>
#    - Execute the installer:
#      cd gemini-cli && sudo ./install_gcp.sh
#
# 4. Access (Secure Tunnel):
#    - From your local machine, run the SSH tunnel command printed at the end.
#    - Open https://localhost:8888 in your browser.
# ==============================================================================

set -e

echo "=================================================="
echo "   INSTALLING RABBITHOLE DEFENSE MESH (v3.2)      "
echo "   Target: Google Cloud e2-micro (Ubuntu 22.04)   "
echo "=================================================="

# 1. System Update & Dependencies
echo "[*] Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    ufw

# 2. Swap Space Configuration (Vital for Free Tier RAM)
echo "[*] Configuring 2GB Swap Space..."
if [ ! -f /swapfile ]; then
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo "    -> Swap active: $(free -h | grep Swap | awk '{print $2}')"
else
    echo "    -> Swap file already exists."
fi

# 3. Docker Installation
if ! command -v docker &> /dev/null; then
    echo "[*] Installing Docker Engine..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    # Install Docker Compose (v2 plugin is standard now)
    sudo apt-get install -y docker-compose-plugin
else
    echo "    -> Docker already installed."
fi

# 4. Firewall Configuration (UFW)
echo "[*] Configuring Host Firewall (UFW)..."
# Deny incoming by default
sudo ufw default deny incoming
sudo ufw default allow outgoing
# Allow SSH management (Standard port 22, will be moved later if desired)
sudo ufw allow 22/tcp
# Allow Honeypot Ports
sudo ufw allow 80/tcp   # HTTP Trap
sudo ufw allow 21/tcp   # FTP Trap
# Dashboard (8888) and Hub (9443) are blocked externally!
# Access via SSH Tunnel: ssh -L 8888:127.0.0.1:8888 user@ip
sudo ufw --force enable
echo "    -> Firewall active. Management ports locked to localhost."

# 5. Application Deployment
echo "[*] Deploying Containers..."
# Ensure .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file missing! Please upload it before running install."
    exit 1
fi
# Secure permissions
chmod 600 .env
chmod 600 key.pem cert.pem host.key 2>/dev/null || true

# Build & Launch
sudo docker compose build
sudo docker compose up -d

echo "=================================================="
echo "   INSTALLATION COMPLETE                          "
echo "=================================================="
echo "Status:"
sudo docker compose ps
echo ""
echo "ACCESS INSTRUCTIONS:"
echo "1. The Dashboard is running on 127.0.0.1:8888 (Hidden)."
echo "2. The Hive Hub is running on 127.0.0.1:9443 (Hidden)."
echo "3. To access them, run this on your LAPTOP:"
echo "   ssh -L 8888:127.0.0.1:8888 -L 9443:127.0.0.1:9443 $USER@<YOUR_GCP_IP>"

echo "4. Open https://localhost:8888 in your browser."
echo "5. Login: admin / <See .env file>"

echo "RabbitHole is now hunting."