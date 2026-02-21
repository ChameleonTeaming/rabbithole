import psutil
import time
import os
import re
from colorama import Fore, Style
from core.armor import AIArmor

class BlueTeamObserver:
    def __init__(self, log_path='/var/log/syslog'):
        self.log_path = log_path
        self.detections = []
        self.start_monitoring = 0
        self.armor = AIArmor()
        
        # Simple regex signatures (can be expanded to YARA/Sigma later)
        self.signatures = {
            "T1087_Discovery": r"(whoami|id|groups|users)",
            "T1059_Persistence": r"(crontab|systemctl enable|rc.local)",
            "T1574_Hijack": r"LD_PRELOAD",
            "T1003_Credential": r"(/etc/shadow|mimikatz|hashdump)",
            "T1027_Obfuscation": r"(base64|xor|rot13)",
            "T1059_ReverseShell": r"(/dev/tcp|bash -i|nc -e|socket)",
            "T1552_SSHKeys": r"(id_rsa|id_dsa|\.ssh/config)",
            "T1595_PortScan": r"(nmap|masscan|rustscan)",
            "T1110_BruteForce": r"(hydra|medusa|crackmapexec|john)",
            "T1059_Metasploit": r"(msfconsole|msfvenom|meterpreter|payload)"
        }

    def start(self):
        print(f"{Fore.BLUE}[BLUE TEAM] Monitoring active processes & logs...{Style.RESET_ALL}")
        self.start_monitoring = time.time()
        
    def scan_processes(self):
        """
        Scans currently running processes for suspicious names/commands.
        """
        # SHIELD: Anti-Flood
        if self.armor.is_under_attack():
            return []

        found = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
                if proc.info['create_time'] < self.start_monitoring:
                    continue # Skip old processes
                
                raw_cmd = " ".join(proc.info['cmdline'] or [])
                
                # FILTER: Sanitize input
                cmd = self.armor.sanitize_input(raw_cmd)
                
                for threat, regex in self.signatures.items():
                    if re.search(regex, cmd, re.IGNORECASE):
                        detection = {
                            "pid": proc.info['pid'],
                            "threat": threat,
                            "command": cmd,
                            "detected_at": time.time()
                        }
                        self.detections.append(detection)
                        found.append(detection)
                        print(f"   {Fore.CYAN}[ALERT]{Style.RESET_ALL} Detected {threat} (PID: {proc.info['pid']})")
                        
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
            
        return found
        
    def check_log_file(self):
        """
        Checks system log file for entries matching signatures.
        """
        # SHIELD: Anti-Flood
        if self.armor.is_under_attack():
            return []

        if not os.path.exists(self.log_path):
            return []
            
        # Simplified log parsing: Read last 100 lines
        # In production, use tail -f or a proper log ingestion pipeline
        try:
            with open(self.log_path, 'r') as f:
                lines = f.readlines()[-100:]
                
            for raw_line in lines:
                # FILTER: Sanitize input
                line = self.armor.sanitize_input(raw_line)
                
                for threat, regex in self.signatures.items():
                    if re.search(regex, line, re.IGNORECASE):
                        # Avoid duplicate detections for same line
                        pass
        except PermissionError:
            print(f"{Fore.YELLOW}[WARNING] Permission denied reading {self.log_path}. Run as root for full visibility.{Style.RESET_ALL}")
            return []
        except Exception:
            pass
        return []
