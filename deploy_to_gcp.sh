#!/bin/bash

# RabbitHole v3.2 - One-Click Google Cloud Deployer
# Run this script from the Google Cloud Shell (cloud.google.com/shell)

set -e

PROJECT_ID=$(gcloud config get-value project)
ZONE="us-central1-a"
INSTANCE_NAME="rabbithole-v3"
MACHINE_TYPE="e2-micro"
IMAGE_FAMILY="ubuntu-2204-lts"
IMAGE_PROJECT="ubuntu-os-cloud"

echo "=================================================="
echo "   DEPLOYING RABBITHOLE DEFENSE MESH (v3.2)       "
echo "   Target: Google Cloud ($PROJECT_ID)             "
echo "=================================================="

# 1. Enable Compute Engine API
echo "[*] Enabling Compute Engine API..."
gcloud services enable compute.googleapis.com

# 2. Configure Firewall Rules
echo "[*] Creating Firewall Rules..."
# Allow Honeypot Ports (21, 22, 80)
if ! gcloud compute firewall-rules describe rabbithole-allow-traps &>/dev/null;
then
    gcloud compute firewall-rules create rabbithole-allow-traps \
        --allow tcp:21,tcp:22,tcp:80 \
        --target-tags=rabbithole-node \
        --description="Allow external traffic to Honeypot traps"
    echo "    -> Firewall rule 'rabbithole-allow-traps' created."
else
    echo "    -> Firewall rule 'rabbithole-allow-traps' already exists."
fi

# 3. Create VM Instance
if ! gcloud compute instances describe $INSTANCE_NAME --zone=$ZONE &>/dev/null;
then
    echo "[*] Creating VM Instance ($INSTANCE_NAME)..."
    gcloud compute instances create $INSTANCE_NAME \
        --project=$PROJECT_ID \
        --zone=$ZONE \
        --machine-type=$MACHINE_TYPE \
        --image-family=$IMAGE_FAMILY \
        --image-project=$IMAGE_PROJECT \
        --tags=rabbithole-node,http-server,https-server \
        --boot-disk-size=30GB \
        --boot-disk-type=pd-standard \
        --description="RabbitHole AI Honeypot Sensor"
    echo "    -> VM created successfully."
else
    echo "    -> VM '$INSTANCE_NAME' already exists. proceeding..."
fi

# 4. Wait for SSH
echo "[*] Waiting for VM to initialize (30s)..."
sleep 30

# 5. Upload Project Files
echo "[*] Uploading RabbitHole codebase..."
# Zip current directory to transfer efficiently
cd ..
zip -r rabbithole_deploy.zip gemini-cli/ -x "*.git*" "gemini-cli/venv/*" "gemini-cli/__pycache__/*"
gcloud compute scp rabbithole_deploy.zip $INSTANCE_NAME:~/ --zone=$ZONE
rm rabbithole_deploy.zip
cd gemini-cli

# 6. Execute Installer Remotely
echo "[*] executing Remote Installer..."
gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command="
    sudo apt-get update && sudo apt-get install -y unzip
    unzip -o rabbithole_deploy.zip
    cd gemini-cli
    chmod +x install_gcp.sh
    # Run the installer non-interactively
    sudo ./install_gcp.sh
"

# 7. Get External IP
EXTERNAL_IP=$(gcloud compute instances describe $INSTANCE_NAME --zone=$ZONE --format='get(networkInterfaces[0].accessConfigs[0].natIP)')

echo "=================================================="
echo "   DEPLOYMENT SUCCESSFUL                          "
echo "=================================================="
echo "Your RabbitHole is LIVE at: $EXTERNAL_IP"
echo ""
echo "ACCESS INSTRUCTIONS:"
echo "1. To access the Secure Dashboard, run this command on YOUR LAPTOP:"
echo "   gcloud compute ssh $INSTANCE_NAME --zone=$ZONE -- -L 8888:127.0.0.1:8888 -L 9443:127.0.0.1:9443"
echo ""
echo "2. Open your browser to: https://localhost:8888"
echo "3. Login: admin / <Your .env Password>"
echo ""
echo "Monitoring has begun."
