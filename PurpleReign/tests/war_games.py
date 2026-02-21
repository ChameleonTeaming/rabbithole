import subprocess
import time
import sys
import os
import signal
from colorama import Fore, Style, init

init(autoreset=True)

def run_war_games():
    print(f"{Fore.MAGENTA}==========================================")
    print(f"⚔️  WAR GAMES: PurpleReign vs. RabbitHole (AI Honeypot)")
    print(f"=========================================={Style.RESET_ALL}")

    # 1. Start RabbitHole (Background)
    print(f"{Fore.BLUE}[SETUP] Deploying RabbitHole AI Honeypot...{Style.RESET_ALL}")
    
    # We need to run RabbitHole from its root directory so it finds config.json
    # We use 'sudo' if port 22 is required, but let's try without first or assume capability
    # Actually, we can't interactively sudo. Let's assume user permissions or port fallback.
    # We will pipe output to a log file to avoid clutter
    
    rabbit_log = open("rabbithole_war.log", "w")
    rabbit_process = subprocess.Popen(
        [sys.executable, "rabbithole.py"],
        stdout=rabbit_log,
        stderr=rabbit_log,
        cwd="/usr/lib/gemini-cli", # Root of workspace
        preexec_fn=os.setsid
    )
    
    print(f"{Fore.BLUE}[SETUP] RabbitHole PID: {rabbit_process.pid}{Style.RESET_ALL}")
    print("Waiting 10s for AI Core initialization...")
    time.sleep(10)

    # 2. Launch PurpleReign Attack
    print(f"{Fore.RED}[ATTACK] Launching PurpleReign Hydra Brute Force...{Style.RESET_ALL}")
    
    # We use the ExploitTools logic directly
    # Target: localhost, Service: ssh
    # Since PurpleReign is modular, we can just invoke hydra directly for this script
    # or import the module. Let's use hydra command directly for clarity in the test.
    
    # Check if RabbitHole is up
    try:
        # Simple netcat check
        check = subprocess.run("nc -z -v -w 2 127.0.0.1 22", shell=True, capture_output=True)
        if check.returncode != 0:
            print(f"{Fore.YELLOW}[WARNING] Port 22 not open. Checking logs...{Style.RESET_ALL}")
            # It might have failed to bind 22. Let's check 2222 just in case logic changed.
            check_alt = subprocess.run("nc -z -v -w 2 127.0.0.1 2222", shell=True, capture_output=True)
            if check_alt.returncode == 0:
                print(f"{Fore.GREEN}[INFO] Found RabbitHole on Port 2222{Style.RESET_ALL}")
                target_port = 2222
            else:
                print(f"{Fore.RED}[ERROR] RabbitHole unreachable.{Style.RESET_ALL}")
                target_port = 22 # Defaulting anyway
        else:
            print(f"{Fore.GREEN}[INFO] Found RabbitHole on Port 22{Style.RESET_ALL}")
            target_port = 22
            
    except Exception as e:
        print(f"Network check failed: {e}")
        target_port = 22

    # Attack Command
    attack_cmd = f"hydra -l root -p password123 ssh://127.0.0.1 -s {target_port} -t 1 -f -V"
    
    print(f"Executing: {attack_cmd}")
    
    attack_process = subprocess.run(attack_cmd, shell=True, capture_output=True, text=True)
    
    # 3. Analyze Results
    print(f"\n{Fore.YELLOW}--- ATTACK REPORT ---{Style.RESET_ALL}")
    print(attack_process.stdout)
    
    # 4. Check RabbitHole Reaction
    print(f"\n{Fore.BLUE}--- RABBITHOLE REACTION ---{Style.RESET_ALL}")
    
    # Kill RabbitHole
    os.killpg(os.getpgid(rabbit_process.pid), signal.SIGTERM)
    rabbit_log.close()
    
    with open("rabbithole_war.log", "r") as f:
        # Read the last 50 lines
        logs = f.readlines()[-50:]
        for line in logs:
            line = line.strip()
            if "Connection" in line or "AUTH" in line or "Honey" in line:
                print(f"{Fore.CYAN}{line}{Style.RESET_ALL}")
            elif "CRITICAL" in line:
                print(f"{Fore.RED}{line}{Style.RESET_ALL}")

if __name__ == "__main__":
    run_war_games()
