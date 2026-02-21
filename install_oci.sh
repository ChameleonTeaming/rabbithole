#!/bin/bash

# RabbitHole Oracle Cloud Infrastructure (OCI) Installer
# Supports Oracle Linux 8/9 and Ubuntu 20.04/22.04

set -e

echo "[+] Detecting OS..."
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
fi

echo "[+] Detected: $OS"
echo "[+] Updating system packages..."

if [[ "$OS" == *"Oracle"* ]] || [[ "$OS" == *"Red Hat"* ]] || [[ "$OS" == *"CentOS"* ]]; then
    # Oracle Linux / RHEL / CentOS
    sudo dnf update -y
    sudo dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo
    sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    sudo systemctl enable --now docker
    
    echo "[+] Configuring Firewalld (Oracle Linux default)..."
    # Open ports 2121 (FTP), 2222 (SSH), 8080 (HTTP), 8000 (Metrics)
    sudo firewall-cmd --permanent --add-port=2121/tcp
    sudo firewall-cmd --permanent --add-port=2222/tcp
    sudo firewall-cmd --permanent --add-port=8080/tcp
    sudo firewall-cmd --permanent --add-port=8000/tcp
    sudo firewall-cmd --reload
    
elif [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
    # Ubuntu / Debian
    sudo apt-get update && sudo apt-get upgrade -y
    sudo apt-get install -y docker.io docker-compose
    sudo systemctl enable --now docker
    
    echo "[+] Configuring iptables (OCI Ubuntu images often use netfilter-persistent)..."
    # OCI Ubuntu images usually have strict iptables rules by default
    sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 2121 -j ACCEPT
    sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 2222 -j ACCEPT
    sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8080 -j ACCEPT
    sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8000 -j ACCEPT
    
    # Save rules if netfilter-persistent is installed
    if dpkg -l | grep -q netfilter-persistent; then
        sudo netfilter-persistent save
    fi
else
    echo "[-] Unsupported OS: $OS. Please install Docker manually."
    exit 1
fi

sudo usermod -aG docker $USER

echo "[+] Setup complete. Please log out and log back in."
echo "    Then, run: docker-compose up -d"
