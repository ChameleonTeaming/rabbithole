#!/bin/bash
# cloud-init script for RabbitHole
# This runs automatically when the server is created.

set -e

echo "[+] Cloud-Init: Starting setup..."

# Detect OS and install Docker
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
fi

if [[ "$OS" == *"Oracle"* ]] || [[ "$OS" == *"Red Hat"* ]] || [[ "$OS" == *"CentOS"* ]]; then
    dnf update -y
    dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo
    dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin git
    systemctl enable --now docker
    
    # Firewalld Rules
    firewall-cmd --permanent --add-port=2121/tcp
    firewall-cmd --permanent --add-port=2222/tcp
    firewall-cmd --permanent --add-port=8080/tcp
    firewall-cmd --permanent --add-port=8000/tcp
    firewall-cmd --reload

elif [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
    apt-get update && apt-get upgrade -y
    apt-get install -y docker.io docker-compose git
    systemctl enable --now docker
    
    # IPTables Rules (OCI Ubuntu images use netfilter-persistent)
    iptables -I INPUT 6 -m state --state NEW -p tcp --dport 2121 -j ACCEPT
    iptables -I INPUT 6 -m state --state NEW -p tcp --dport 2222 -j ACCEPT
    iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8080 -j ACCEPT
    iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8000 -j ACCEPT
    
    if dpkg -l | grep -q netfilter-persistent; then
        netfilter-persistent save
    fi
fi

# Allow 'ubuntu' or 'opc' user to use Docker
usermod -aG docker ubuntu || usermod -aG docker opc || true

echo "[+] Cloud-Init: Setup complete."
