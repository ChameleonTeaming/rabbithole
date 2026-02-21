#!/bin/bash

# Configuration
if [ -f .env ]; then
    export $(cat .env | xargs)
else
    echo "ERROR: .env file not found. Please create one with DASHBOARD_USER, DASHBOARD_PASS, etc."
    exit 1
fi

echo "=================================================="
echo "   STARTING RABBITHOLE DEFENSE MESH (v3.2)        "
echo "=================================================="

# 1. Kill any existing instances
echo "[*] Cleaning up old processes..."
pkill -f hive_mind_server.py
pkill -f rabbithole.py
pkill -f simulate_global_traffic.py

# 2. Start the Hive Mind Hub (The Central Brain)
echo "[*] Launching Hive Mind Intelligence Hub..."
# Use setsid to detach from the script's process group
setsid nohup python3 hive_mind_server.py > hive_mind.log 2>&1 &
PID_HUB=$!
echo "    -> Hub active on PID $PID_HUB (https://localhost:9443)"
sleep 2

# 3. Start the RabbitHole Honeypot (The Local Sensor)
echo "[*] Launching RabbitHole AI Honeypot..."
setsid nohup python3 rabbithole.py > rabbithole.log 2>&1 &
PID_POT=$!
echo "    -> Honeypot active on PID $PID_POT"
echo "    -> Dashboard: http://localhost:8888"
echo "    -> User: $DASHBOARD_USER"
echo "    -> Pass: $DASHBOARD_PASS"
sleep 5

# 4. Start the Global Traffic Simulator (The "War Room" Effect)
echo "[*] initializing Global Traffic Simulation..."
setsid nohup python3 simulate_global_traffic.py > traffic_sim.log 2>&1 &
PID_SIM=$!
echo "    -> Simulation active on PID $PID_SIM"

echo "=================================================="
echo "   SYSTEM FULLY OPERATIONAL                       "
echo "=================================================="
echo "Logs available in:"
echo "  - hive_mind.log"
echo "  - rabbithole.log"
echo "  - traffic_sim.log"
echo ""
echo "Services are running in background."