import argparse
import time
import os
import sys
from colorama import Fore, Style, init
from core.red import RedTeamExecutor
from core.blue import BlueTeamObserver

init(autoreset=True)

class PurpleReign:
    def __init__(self, target_log_path='/var/log/syslog'):
        self.red = RedTeamExecutor()
        self.blue = BlueTeamObserver(target_log_path)
        
    def start_simulation(self):
        print(f"{Fore.MAGENTA}================================================={Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}  PURPLE REIGN: Advanced Adversary Simulation    {Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}================================================={Style.RESET_ALL}")
        
        # 1. Start Blue Team (Monitoring)
        self.blue.start()
        
        # 2. Run Attack Scenarios (Red Team)
        self._run_phase_1_discovery()
        self._run_phase_2_persistence()
        self._run_phase_3_obfuscation()
        
        # 3. Analyze Results (Purple Team)
        self._generate_report()

    def _run_phase_1_discovery(self):
        print(f"\n{Fore.YELLOW}PHASE 1: DISCOVERY{Style.RESET_ALL}")
        
        # Attack 1: User Discovery
        self.red.execute_tactic("T1087", "whoami && id", "Discover Current User")
        time.sleep(1) # Allow logs to propagate
        self.blue.scan_processes()

        # Attack 2: System Time Discovery
        self.red.execute_tactic("T1124", "date", "Discover System Time")
        time.sleep(1)
        self.blue.scan_processes()

    def _run_phase_2_persistence(self):
        print(f"\n{Fore.YELLOW}PHASE 2: PERSISTENCE{Style.RESET_ALL}")
        
        # Attack 3: Scheduled Task check
        self.red.execute_tactic("T1053", "crontab -l", "List Scheduled Tasks")
        time.sleep(1)
        self.blue.scan_processes()

    def _run_phase_3_obfuscation(self):
        print(f"\n{Fore.YELLOW}PHASE 3: DEFENSE EVASION{Style.RESET_ALL}")
        
        # Attack 4: Base64 Obfuscation
        self.red.execute_tactic("T1027", "echo 'Hello World' | base64", "Obfuscated Command Execution")
        time.sleep(1)
        self.blue.scan_processes()

    def _generate_report(self):
        print(f"\n{Fore.MAGENTA}================================================={Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}  SIMULATION REPORT                              {Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}================================================={Style.RESET_ALL}")
        
        detections = len(self.blue.detections)
        attacks = len(self.red.history)
        
        print(f"Total Attacks Executed: {attacks}")
        print(f"Total Detections: {detections}")
        
        score = (detections / attacks) * 100 if attacks > 0 else 0
        color = Fore.GREEN if score > 80 else (Fore.YELLOW if score > 50 else Fore.RED)
        
        print(f"Detection Rate: {color}{score:.1f}%{Style.RESET_ALL}")
        
        if score < 100:
            print(f"\n{Fore.CYAN}Recommendations:{Style.RESET_ALL}")
            print("- Enable Process Creation Monitoring (Event ID 4688 / Auditd execve)")
            print("- Deploy Sysmon for granular command line logging.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PurpleReign - Adversary Emulation")
    parser.add_argument("--log", default="/var/log/syslog", help="Path to system log file")
    args = parser.parse_args()
    
    reign = PurpleReign(args.log)
    reign.start_simulation()
