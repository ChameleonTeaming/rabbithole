import subprocess
import time
import sys
import os
import signal
from colorama import Fore, Style, init

init(autoreset=True)

def run_radioactive_war():
    print(f"{Fore.MAGENTA}==========================================")
    print(f"☢️  S-TIER WAR: Radioactive Trap Test")
    print(f"=========================================={Style.RESET_ALL}")

    # 1. Start RabbitHole (S-Tier)
    print(f"{Fore.BLUE}[SETUP] Deploying RabbitHole S-Tier...{Style.RESET_ALL}")
    
    rabbit_log = open("rabbithole_s_tier.log", "w")
    # Using system python to ensure aiohttp etc are available
    rabbit_process = subprocess.Popen(
        ["/usr/bin/python3", "rabbithole.py"],
        stdout=rabbit_log,
        stderr=rabbit_log,
        cwd="/usr/lib/gemini-cli",
        preexec_fn=os.setsid
    )
    
    print(f"RabbitHole Active (PID: {rabbit_process.pid})")
    time.sleep(10)

    # 2. Launch Targeted Attack
    # We will use 'curl' to simulate an SSH session interaction with the trap
    # Since we can't easily script an interactive SSH 'cat' without paramiko,
    # we'll use the RabbitHole analysis engine directly via a mock connection if needed,
    # or just use the HTTP trap which also uses analyze_command.
    
    print(f"{Fore.RED}[ATTACK] Attempting to steal 'private_keys.txt'...{Style.RESET_ALL}")
    
    # Target the HTTP trap (Port 80) with a command injection payload that triggers 'cat'
    attack_cmd = "curl -s 'http://127.0.0.1:80/shell.php?cmd=cat+private_keys.txt'"
    
    try:
        result = subprocess.run(attack_cmd, shell=True, capture_output=True, text=True)
        print(f"\n{Fore.YELLOW}--- RECEIVED CONTENT (POISONED) ---")
        print(result.stdout)
        
        if "beacon" in result.stdout or "CANARY_DATA_ID" in result.stdout:
            print(f"\n{Fore.GREEN}✅ SUCCESS: Attacker received radioactive data.{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}❌ FAILED: Received standard or no content.{Style.RESET_ALL}")

    except Exception as e:
        print(f"Attack failed: {e}")

    # 3. Check RabbitHole Logs for Alert
    print(f"\n{Fore.BLUE}--- RABBITHOLE AUDIT ---")
    time.sleep(2)
    
    os.killpg(os.getpgid(rabbit_process.pid), signal.SIGTERM)
    rabbit_log.close()
    
    with open("rabbithole_s_tier.log", "r") as f:
        logs = f.read()
        if "DEEP_BAIT_TRIGGERED" in logs or "HONEYTOKEN_TRAP_TRIGGERED" in logs:
            print(f"{Fore.GREEN}✅ ALERT CONFIRMED: RabbitHole detected and flagged the theft.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ ALERT MISSING: Check logic paths.{Style.RESET_ALL}")

if __name__ == "__main__":
    run_radioactive_war()
