import requests
import json
import time
from colorama import Fore, Style

class OSINTProfiler:
    def __init__(self):
        self.headers = {'User-Agent': 'PurpleReign-Intel/1.0'}

    def analyze_ip(self, ip_address):
        """
        Aggregates intelligence from multiple public sources.
        """
        print(f"{Fore.CYAN}[OSINT] Initiating Deep Dive on {ip_address}...{Style.RESET_ALL}")
        
        report = {
            "target": ip_address,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "geo": self._get_geo(ip_address),
            "reputation": self._get_reputation(ip_address),
            "ports": self._simulate_port_scan(ip_address), # Simulated for demo/safety
            "threat_level": "UNKNOWN"
        }
        
        # Calculate Threat Level
        score = 0
        if report['reputation']['abuse_score'] > 0: score += 50
        if report['geo']['country'] in ['RU', 'CN', 'KP', 'IR']: score += 20
        if 22 in report['ports'] or 23 in report['ports']: score += 10
        
        if score > 70: report['threat_level'] = "CRITICAL"
        elif score > 40: report['threat_level'] = "HIGH"
        elif score > 10: report['threat_level'] = "MODERATE"
        else: report['threat_level'] = "LOW"
        
        return report

    def _get_geo(self, ip):
        try:
            # Using ip-api (free tier, limited)
            url = f"http://ip-api.com/json/{ip}"
            r = requests.get(url, headers=self.headers, timeout=5)
            if r.status_code == 200:
                data = r.json()
                return {
                    "country": data.get("countryCode", "Unknown"),
                    "city": data.get("city", "Unknown"),
                    "isp": data.get("isp", "Unknown"),
                    "org": data.get("org", "Unknown")
                }
        except Exception as e:
            print(f"{Fore.YELLOW}[OSINT] Geo lookup failed: {e}{Style.RESET_ALL}")
        return {"country": "Unknown", "city": "Unknown", "isp": "Unknown"}

    def _get_reputation(self, ip):
        # In a production tool, this would query AbuseIPDB/VirusTotal APIs
        # For the prototype, we assume it's suspicious if it's hitting our honeypot
        return {
            "source": "Heuristic Analysis",
            "abuse_score": 85, # Simulated high score for demo context
            "known_botnet": False
        }

    def _simulate_port_scan(self, ip):
        # Instead of scanning (illegal), we infer common ports for this type of actor
        # Real OSINT would query Shodan API here
        return [22, 80, 443, 8080] # Common open ports for scanning infrastructure
