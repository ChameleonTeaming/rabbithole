
import asyncio
import aiohttp
import random
import uuid
import datetime
import os
import ssl

HUB_URL = os.getenv('HUB_URL', "https://127.0.0.1:9443")
# Using the default token for demo purposes
AUTH_TOKEN = os.getenv('HIVE_MIND_TOKEN', "6d3574ff21cc17ab6b00405020f2a277") 

ATTACK_SCENARIOS = [
    {"ip": "116.203.44.1", "country": "DE", "type": "SSH Brute Force", "count": 50},
    {"ip": "185.199.111.153", "country": "RU", "type": "SQL Injection", "count": 12},
    {"ip": "45.155.205.233", "country": "CN", "type": "Mirai Botnet", "count": 200},
    {"ip": "192.99.14.22", "country": "CA", "type": "WordPress Scan", "count": 35},
    {"ip": "103.21.244.0", "country": "VN", "type": "Log4Shell Exploit", "count": 1},
    {"ip": "5.188.62.76", "country": "RU", "type": "Ransomware Beacon", "count": 5},
    {"ip": "167.99.163.8", "country": "US", "type": "Port Scan", "count": 1000},
    {"ip": "213.66.139.43", "country": "SE", "type": "SWIFT Transaction Interception", "count": 3},
    {"ip": "91.24.185.37", "country": "IR", "type": "Modbus/TCP Logic Injection", "count": 8},
    {"ip": "101.32.45.112", "country": "KP", "type": "Aerospace Schematic Exfiltration", "count": 1},
    {"ip": "77.210.63.142", "country": "UA", "type": "BGP Hijacking Attempt", "count": 15}
]

SIMULATED_NODES = [
    "RH-NODE-TOKYO-01",
    "RH-NODE-LONDON-03",
    "RH-NODE-NYC-05",
    "RH-NODE-FRANKFURT-02",
    "RH-NODE-SINGAPORE-09",
    "RH-NODE-SYDNEY-04",
    "RH-NODE-SAOPAULO-07",
    "RH-NODE-MUMBAI-08",
    "RH-NODE-TORONTO-06",
    "RH-NODE-SWIFT-GATEWAY-01",
    "RH-NODE-GRID-CONTROL-OSLO",
    "RH-NODE-PROPULSION-LAB-STAGING",
    "RH-NODE-ZURICH-VAULT-02",
    "RH-NODE-TEL-AVIV-CORE-01"
]

async def report_incident(session, node_id):
    scenario = random.choice(ATTACK_SCENARIOS)
    
    # Jitter the IP slightly to make it look real
    base_ip = scenario['ip'].rsplit('.', 1)[0]
    fake_ip = f"{base_ip}.{random.randint(1, 254)}"
    
    payload = {
        "node_id": node_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "ip": fake_ip,
        "type": scenario['type'],
        "country": scenario['country'],
        "details": f"Blocked {scenario['count']} attempts from {fake_ip}",
        "action": "BLOCKED"
    }
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        # Create a custom SSL context that ignores verification
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        
        async with session.post(f"{HUB_URL}/api/incident", json=payload, headers=headers, ssl=ssl_ctx) as resp:
            if resp.status == 201:
                print(f"[{node_id}] Reported {scenario['type']} from {fake_ip}")
            else:
                print(f"[{node_id}] Failed to report: {resp.status}")
    except Exception as e:
        print(f"[{node_id}] Error: {e}")

async def main():
    print(f"Starting Global Threat Simulation for {len(SIMULATED_NODES)} nodes...")
    async with aiohttp.ClientSession() as session:
        while True:
            # Randomly pick a node to report an incident
            node = random.choice(SIMULATED_NODES)
            await report_incident(session, node)
            
            # Random sleep between 2 and 10 seconds to simulate natural traffic
            await asyncio.sleep(random.uniform(2, 8))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSimulation stopped.")
