import time
import random
from colorama import Fore, Style

class PredatorEngine:
    def __init__(self, red_team, blue_team):
        self.red = red_team
        self.blue = blue_team
        self.campaign_active = False
        
        # Attack Library (The Playbook)
        self.playbook = {
            "Phase 1: Discovery": [
                {"id": "T1087", "cmd": "whoami", "stealth": False, "desc": "Basic Recon"},
                {"id": "T1087", "cmd": "id", "stealth": True, "desc": "Stealth Recon (Jitter)"}
            ],
            "Phase 2: Persistence": [
                {"id": "T1053", "cmd": "crontab -l", "stealth": False, "desc": "Check Crontab"},
                {"id": "T1053", "cmd": "ls /etc/cron.d", "stealth": True, "desc": "Passive File Check"}
            ],
            "Phase 3: Execution": [
                {"id": "T1059", "cmd": "echo 'test'", "stealth": False, "desc": "Simple Echo"},
                {"id": "T1027", "cmd": "echo 'dGVzdAo=' | base64 -d", "stealth": True, "desc": "Obfuscated Execution"}
            ]
        }

    def start_campaign(self):
        self.campaign_active = True
        print(f"{Fore.MAGENTA}[PREDATOR] Autonomous Campaign Started.{Style.RESET_ALL}")
        
        for phase_name, tactics in self.playbook.items():
            if not self.campaign_active: break
            
            print(f"\n{Fore.CYAN}--- {phase_name} ---
{Style.RESET_ALL}")
            success = self._execute_phase(tactics)
            
            if not success:
                print(f"{Fore.RED}[PREDATOR] Phase Failed. Aborting Campaign.{Style.RESET_ALL}")
                break
            else:
                print(f"{Fore.GREEN}[PREDATOR] Phase Complete. Advancing...{Style.RESET_ALL}")
                time.sleep(2)

    def _execute_phase(self, tactics):
        """
        Tries tactics in order. If one fails (caught), tries the next (stealthier) one.
        """
        for tactic in tactics:
            # 1. Execute
            print(f"[PREDATOR] Trying: {tactic['desc']}...")
            self.red.execute_tactic(
                tactic['id'], 
                tactic['cmd'], 
                tactic['desc'], 
                jitter=tactic['stealth']
            )
            
            # 2. Check for Detection (Wait 1s for logs)
            time.sleep(1)
            detections = self.blue.scan_processes()
            
            # 3. Adapt
            is_caught = False
            for d in detections:
                if tactic['id'] in d.get('threat', '') or tactic['cmd'] in d.get('command', ''):
                    is_caught = True
                    break
            
            if is_caught:
                print(f"{Fore.YELLOW}[PREDATOR] ⚠️  Attack Detected! Adapting strategy...{Style.RESET_ALL}")
                continue # Try next tactic in list
            else:
                print(f"{Fore.GREEN}[PREDATOR] ✅ Success! Undetected.{Style.RESET_ALL}")
                return True # Phase successful, move to next phase
                
        return False # All tactics in this phase failed
