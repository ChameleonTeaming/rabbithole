import subprocess
import time
import sys
import os
import signal
from colorama import Fore, Style, init

init(autoreset=True)

def run_visual_war():
    print(f"{Fore.MAGENTA}==========================================")
    print(f"👁️  VISUAL WAR GAMES: PurpleReign vs. RabbitHole")
    print(f"=========================================={Style.RESET_ALL}")

    # 1. Start RabbitHole
    print(f"{Fore.BLUE}[SETUP] Deploying RabbitHole AI Honeypot...{Style.RESET_ALL}")
    
    rabbit_log = open("rabbithole_viz.log", "w")
    rabbit_process = subprocess.Popen(
        [sys.executable, "rabbithole.py"],
        stdout=rabbit_log,
        stderr=rabbit_log,
        cwd="/usr/lib/gemini-cli",
        preexec_fn=os.setsid
    )
    
    print(f"{Fore.BLUE}[SETUP] RabbitHole Active (PID: {rabbit_process.pid}){Style.RESET_ALL}")
    print("Waiting 10s for Dashboard initialization...")
    time.sleep(10)

    # 2. Instructions for User
    print(f"\n{Fore.GREEN}================================================={Style.RESET_ALL}")
    print(f"{Fore.GREEN}   ACTION REQUIRED: OPEN THE DASHBOARD NOW       {Style.RESET_ALL}")
    print(f"{Fore.GREEN}================================================={Style.RESET_ALL}")
    print(f"1. Open your browser to: {Fore.CYAN}http://localhost:8888{Style.RESET_ALL}")
    print(f"2. Login with: {Fore.YELLOW}admin{Style.RESET_ALL} / {Fore.YELLOW}admin{Style.RESET_ALL}")
    print(f"3. You should see the 'RabbitHole Intelligence Hub'.")
    print(f"4. Watch the 'Live Attack Feed' or 'Active Sessions'.")
    
    # 3. Countdown
    for i in range(10, 0, -1):
        print(f"Attack launching in {i} seconds...", end="\r")
        time.sleep(1)
    print("\n")

    # 4. Launch Attack
    print(f"{Fore.RED}[ATTACK] Launching PurpleReign Hydra Brute Force...{Style.RESET_ALL}")
    
    attack_cmd = "hydra -l root -p password123 ssh://127.0.0.1 -s 22 -t 1 -f -V"
    attack_process = subprocess.run(attack_cmd, shell=True, capture_output=True, text=True)
    
    print(f"{Fore.RED}[ATTACK] Attack Complete. Check the Dashboard for the alert!{Style.RESET_ALL}")
    
    # Keep RabbitHole alive for a bit so user can see the result
    print("Keeping Honeypot alive for 30 seconds...")
    time.sleep(30)
    
    # Cleanup
    os.killpg(os.getpgid(rabbit_process.pid), signal.SIGTERM)
    rabbit_log.close()
    print(f"{Fore.BLUE}[CLEANUP] RabbitHole Shutdown.{Style.RESET_ALL}")

if __name__ == "__main__":
    run_visual_war()
