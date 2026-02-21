#!/bin/bash

# ANSI Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== RabbitHole: Laptop Deployment Kit ===${NC}"

# 1. Check Prerequisites
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR] Python 3 could not be found. Please install it.${NC}"
    exit 1
fi

echo -e "${GREEN}[+] Python 3 detected.${NC}"

# 2. Install Dependencies
echo -e "${BLUE}[*] Installing dependencies...${NC}"
pip install -r requirements.txt &> /dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] Failed to install dependencies. Try running with sudo?${NC}"
    # Continuing anyway as they might be installed
fi

# 3. Cleanup Old Processes
echo -e "${BLUE}[*] Cleaning up old processes...${NC}"
pkill -f rabbithole.py
pkill -f hive_mind_server.py
sleep 2

# 4. Start Hive Mind (Local Hub)
echo -e "${BLUE}[*] Starting Hive Mind Intelligence Hub...${NC}"
python3 hive_mind_server.py > hivemind.log 2>&1 &
HIVEMIND_PID=$!
echo -e "${GREEN}[+] Hive Mind Active (PID: $HIVEMIND_PID) on port 9000${NC}"

# 5. Start RabbitHole
echo -e "${BLUE}[*] Starting RabbitHole Honeypot...${NC}"

# Load Dashboard Password
if [ -f "dashboard_password.txt" ]; then
    export DASHBOARD_PASS=$(cat dashboard_password.txt)
    echo -e "${GREEN}[+] Secured Dashboard with generated credentials.${NC}"
else
    echo -e "${RED}[WARNING] No password file found. Dashboard is insecure!${NC}"
fi

# Check for API Key
if [ -z "$GEMINI_API_KEY" ]; then
    echo -e "${RED}[WARNING] GEMINI_API_KEY is not set! The AI will run in fallback mode (Limited Deception).${NC}"
    echo -e "To enable full AI, run: export GEMINI_API_KEY='your_key_here' before this script."
fi

python3 rabbithole.py > rabbithole.log 2>&1 &
RABBIT_PID=$!

echo -e "${GREEN}[+] RabbitHole Active (PID: $RABBIT_PID)${NC}"
echo -e ""
echo -e "=================================================="
echo -e "   ${GREEN}MISSION CONTROL DASHBOARD:${NC} http://localhost:8888"
echo -e "   ${GREEN}SSH HONEYPOT:${NC}              ssh root@localhost"
echo -e "   ${GREEN}FTP HONEYPOT:${NC}              ftp localhost"
echo -e "   ${GREEN}HTTP HONEYPOT:${NC}             http://localhost"
echo -e "   ${GREEN}METRICS:${NC}                   http://localhost:8000"
echo -e "=================================================="
echo -e ""
echo -e "${BLUE}[*] Logs are being written to 'rabbithole.log' and 'alerts.log'.${NC}"
echo -e "${BLUE}[*] Press CTRL+C to stop all services.${NC}"

# Wait loop
trap "kill $RABBIT_PID $HIVEMIND_PID; exit" INT
wait
