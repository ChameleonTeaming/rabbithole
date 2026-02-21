import psutil
import time
import re
import os
import sys
from colorama import Fore, Style, init

init(autoreset=True)

class SentinelXPro:
    def __init__(self):
        self.threat_score = 0
        self.suspicious_pids = set()
        self.running = True
        self.start_time = time.time()
        
        # S-Tier Heuristics
        self.signatures = {
            r"whoami|id": 10,
            r"crontab": 30,
            r"base64": 40,
            r"bash -i": 90,
            r"/dev/tcp": 90,
            r"shadow": 100,
            r"id_rsa": 80,
            r"socket\.socket": 80, # Direct python socket usage
            r"os\.dup2": 80,       # Shell redirection via python
            r"subprocess\.call": 50
        }
        
        # Deception (Honeypot)
        self.honeypots = ["/tmp/passwords.txt", "/tmp/secret.db"]
        self._deploy_honeypots()

    def _deploy_honeypots(self):
        for path in self.honeypots:
            if not os.path.exists(path):
                with open(path, "w") as f:
                    f.write("FAKE CREDENTIALS - DO NOT TOUCH")

    def start_monitoring(self):
        print(f"{Fore.CYAN}[SENTINEL-X PRO] S-Tier Defense Active.{Style.RESET_ALL}")
        
        try:
            while self.running:
                self.scan_behavior()
                self.check_honeypots()
                time.sleep(0.05) # Ultra-fast polling (20Hz)
        except KeyboardInterrupt:
            print("[SENTINEL-X] Deactivated.")

    def scan_behavior(self):
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.pid in self.suspicious_pids:
                    continue

                cmd = " ".join(proc.info['cmdline'] or [])
                if not cmd: continue

                score = 0
                reasons = []
                
                # Signature Matching
                for sig, weight in self.signatures.items():
                    if re.search(sig, cmd, re.IGNORECASE):
                        score += weight
                        reasons.append(sig)

                # Heuristic: Python spawning Shell
                if proc.name() == "python3":
                    try:
                        children = proc.children()
                        for child in children:
                            if child.name() in ['sh', 'bash', 'dash']:
                                score += 100
                                reasons.append("Behavior: Python->Shell")
                    except:
                        pass

                if score > 0:
                    self.suspicious_pids.add(proc.pid)
                    self.handle_threat(proc, score, reasons)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    def check_honeypots(self):
        # Ignore alerts in first 2 seconds (Startup Noise)
        if time.time() - self.start_time < 2.0:
            return

        for path in self.honeypots:
            try:
                if os.path.exists(path):
                    atime = os.path.getatime(path)
                    # If accessed AFTER sentinel started
                    if atime > self.start_time:
                        # Reset atime to avoid loops? No, just alert.
                        print(f"{Fore.RED}[SENTINEL-X] 🛑 HONEYPOT TRIGGERED! File: {path}{Style.RESET_ALL}")
                        # Update start time to avoid spamming the same alert
                        self.start_time = time.time()
            except:
                pass

    def handle_threat(self, proc, score, reasons):
        reason_str = ", ".join(reasons)
        if score >= 80:
            print(f"{Fore.RED}[SENTINEL-X] 🛑 BLOCKED THREAT (Score: {score}){Style.RESET_ALL}")
            print(f"    Target: PID {proc.pid} ({proc.name()})")
            print(f"    Reason: {reason_str}")
            try:
                proc.kill()
                print(f"    Action: {Fore.GREEN}TERMINATED{Style.RESET_ALL}")
            except:
                pass
        elif score >= 30:
            print(f"{Fore.YELLOW}[SENTINEL-X] ⚠️  SUSPICIOUS (Score: {score}){Style.RESET_ALL}")
            print(f"    PID: {proc.pid} | CMD: {reason_str}")

if __name__ == "__main__":
    edr = SentinelXPro()
    edr.start_monitoring()
