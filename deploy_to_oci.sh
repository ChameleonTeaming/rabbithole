#!/bin/bash
# RabbitHole Auto-Deployer for Oracle Cloud
# This script guides you through deploying the honeypot using Terraform.

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}[+] RabbitHole OCI Auto-Deployer${NC}"
echo "------------------------------------------------"
echo "This script will deploy the RabbitHole honeypot to your Oracle Cloud account."
echo "It creates a VCN, Public Subnet, Firewall Rules, and an ARM Server (Always Free tier eligible)."
echo ""

# Check for Terraform
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}[!] Error: Terraform is not installed.${NC}"
    echo "Please install Terraform first: https://developer.hashicorp.com/terraform/install"
    exit 1
fi

# Check for OCI Config
if [ ! -f ~/.oci/config ] && [ -z "$TF_VAR_tenancy_ocid" ]; then
    echo -e "${RED}[!] Warning: OCI Configuration not detected.${NC}"
    echo "Terraform needs to authenticate with Oracle Cloud."
    echo "Please ensure you have run 'oci setup config' or set standard OCI environment variables."
    read -p "Press Enter to continue anyway (if you know what you are doing)..."
fi

echo "------------------------------------------------"
echo "Please provide the following details from your OCI Console:"
echo ""

# Get Compartment OCID
read -p "1. Enter Compartment OCID: " COMPARTMENT_OCID
while [[ -z "$COMPARTMENT_OCID" ]]; do
    echo "   OCID cannot be empty."
    read -p "1. Enter Compartment OCID: " COMPARTMENT_OCID
done

# Get Region
read -p "2. Enter Region (e.g., us-ashburn-1): " REGION
while [[ -z "$REGION" ]]; do
    echo "   Region cannot be empty."
    read -p "2. Enter Region (e.g., us-ashburn-1): " REGION
done

# Get SSH Key
DEFAULT_KEY="$HOME/.ssh/id_rsa.pub"
read -p "3. Enter path to SSH Public Key [Default: $DEFAULT_KEY]: " SSH_KEY_PATH
SSH_KEY_PATH=${SSH_KEY_PATH:-$DEFAULT_KEY}

if [ ! -f "$SSH_KEY_PATH" ]; then
    echo -e "${RED}[!] Warning: SSH key not found at $SSH_KEY_PATH${NC}"
    read -p "   Would you like to generate a new SSH key pair now? (y/n): " GENERATE_KEY
    if [[ "$GENERATE_KEY" =~ ^[Yy]$ ]]; then
        echo "   Generating new SSH key ($SSH_KEY_PATH)..."
        ssh-keygen -t rsa -b 4096 -f "${SSH_KEY_PATH%.pub}" -N "" -q
        echo -e "${GREEN}   [+] Key generated successfully.${NC}"
    else
        echo -e "${RED}[!] Error: Cannot deploy without an SSH key.${NC}"
        echo "   Please run 'ssh-keygen' manually or provide a path to an existing key."
        exit 1
    fi
fi
SSH_KEY_CONTENT=$(cat "$SSH_KEY_PATH")

echo "------------------------------------------------"
echo -e "${GREEN}[+] Configuration Ready.${NC}"
echo "Initializing Terraform..."

cd oci_terraform
terraform init

echo ""
echo -e "${GREEN}[+] Starting Deployment...${NC}"
echo "This may take 2-5 minutes."
echo ""

terraform apply \
  -var "compartment_ocid=$COMPARTMENT_OCID" \
  -var "region=$REGION" \
  -var "ssh_public_key=$SSH_KEY_CONTENT" \
  -auto-approve

echo ""
echo -e "${GREEN}[+] Deployment Complete!${NC}"
echo "Your honeypot server is now running."
echo "Copy the 'server_public_ip' from the output above."
echo ""
echo "To connect:"
echo "  ssh ubuntu@<SERVER_IP>"

echo ""
echo "Note: It may take another 5 minutes for the server to install Docker and start the honeypot."
