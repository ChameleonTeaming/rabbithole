import subprocess
import time
import random
from colorama import Fore, Style

class RedTeamExecutor:
    def __init__(self):
        self.history = []

    def execute_tactic(self, tactic_id, command, description, jitter=False):
        """
        Executes a specific MITRE ATT&CK Tactic.
        """
        if jitter:
            delay = random.uniform(2.0, 5.0)
            print(f"{Fore.YELLOW}[STEALTH] Jitter enabled. Sleeping for {delay:.1f}s...{Style.RESET_ALL}")
            time.sleep(delay)

        print(f"{Fore.RED}[RED TEAM] Executing {tactic_id}: {description}{Style.RESET_ALL}")
        start_time = time.time()
        
        try:
            # Execute command safely
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            status = "SUCCESS" if result.returncode == 0 else "FAILED"
            output = result.stdout.strip() if status == "SUCCESS" else result.stderr.strip()
            
        except Exception as e:
            status = "ERROR"
            output = str(e)

        end_time = time.time()
        
        log_entry = {
            "tactic_id": tactic_id,
            "description": description,
            "command": command,
            "status": status,
            "output": output,
            "timestamp": start_time,
            "duration": end_time - start_time
        }
        self.history.append(log_entry)
        
        color = Fore.GREEN if status == "SUCCESS" else Fore.RED
        print(f"   -> Result: {color}{status}{Style.RESET_ALL} (Output len: {len(output)})")
        
        return log_entry
