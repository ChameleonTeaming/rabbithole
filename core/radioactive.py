import hashlib
import time
import os

class RadioactiveFiles:
    """Generates 'radioactive' honeytokens that track attackers after they leave."""
    def __init__(self, hub_url="https://localhost:9443"):
        self.hub_url = hub_url
        self.salt = "RADIOACTIVE_RABBIT_2026"

    def generate_token(self, ip, filename):
        """Creates a unique tracking token for a specific file and attacker."""
        raw = f"{ip}:{filename}:{self.salt}:{time.time()}"
        return hashlib.md5(raw.encode()).hexdigest()

    def get_radioactive_content(self, ip, filename):
        """Returns 'poisoned' content for a file that includes a tracking beacon."""
        token = self.generate_token(ip, filename)
        beacon_url = f"{self.hub_url}/api/beacon/{token}"
        
        if filename.endswith(".pdf") or filename.endswith(".doc"):
            return f"%PDF-1.4\n%Radioactive Beacon: {beacon_url}\n[CANARY_DATA_ID:{token}]\n"
        elif filename.endswith(".json") or filename.endswith(".txt"):
            return f"{{\n  \"status\": \"encrypted\",\n  \"trace_id\": \"{token}\",\n  \"callback\": \"{beacon_url}\",\n  \"data\": \"S-TIER_DECEPTION_ACTIVE\"\n}}\n"
        
        return f"Tracking ID: {token}\nBeacon: {beacon_url}\n"

    def log_beacon_hit(self, token, request_info):
        """Logic to call when a beacon is triggered."""
        # In a real scenario, this would be handled by the CommandCenter/Hub
        print(f"[RADIOACTIVE] !!! BEACON TRIGGERED !!! Token: {token}")
        print(f"[RADIOACTIVE] Attacker Info: {request_info}")
