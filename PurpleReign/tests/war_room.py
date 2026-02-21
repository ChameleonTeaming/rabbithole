import subprocess
import time
import sys
import os
import signal
import random
from colorama import Fore, Style, init

init(autoreset=True)

def run_war_room():
    print(f"{Fore.MAGENTA}==========================================")
    print(f"🏰  THE WAR ROOM: FULL S-TIER ORCHESTRATION")
    print(f"=========================================={Style.RESET_ALL}")

    # 1. Kill any existing instances
    print(f"{Fore.YELLOW}[CLEANUP] Clearing existing processes...{Style.RESET_ALL}")
    subprocess.run("ps aux | grep -E 'rabbithole.py|hive_mind_server.py' | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null", shell=True)
    time.sleep(2)

    # 2. Start Hive Mind Hub (The Brain)
    print(f"{Fore.BLUE}[SETUP] Deploying Secure Hive Mind Hub (HTTPS:9443)...{Style.RESET_ALL}")
    hub_log = open("war_room_hub.log", "w")
    hub_process = subprocess.Popen(
        ["/usr/bin/python3", "hive_mind_server.py"],
        stdout=hub_log,
        stderr=hub_log,
        cwd="/usr/lib/gemini-cli",
        preexec_fn=os.setsid
    )
    time.sleep(3) # Give hub time to bind port

    # 3. Start RabbitHole (The Trap)
    print(f"{Fore.BLUE}[SETUP] Deploying RabbitHole S-Tier (HTTPS:8888)...{Style.RESET_ALL}")
    rabbit_log = open("war_room_rabbithole.log", "w")
    rabbit_process = subprocess.Popen(
        ["/usr/bin/python3", "rabbithole.py"],
        stdout=rabbit_log,
        stderr=rabbit_log,
        cwd="/usr/lib/gemini-cli",
        preexec_fn=os.setsid
    )
    
    print(f"Hub PID: {hub_process.pid} | RabbitHole PID: {rabbit_process.pid}")
    time.sleep(10) # Give AI core time to initialize

    # 4. User Instructions
    print(f"\n{Fore.GREEN}================================================={Style.RESET_ALL}")
    print(f"{Fore.GREEN}   ACTION: OPEN YOUR DASHBOARD NOW               {Style.RESET_ALL}")
    print(f"{Fore.GREEN}================================================={Style.RESET_ALL}")
    print(f"Main Dashboard: {Fore.CYAN}https://localhost:8888{Style.RESET_ALL}")
    print(f"Intelligence Hub: {Fore.CYAN}https://localhost:9443/api/status{Style.RESET_ALL}")
    print(f"Credentials:    {Fore.YELLOW}admin / admin{Style.RESET_ALL}")
    print(f"=================================================\n")

    # 5. Infinite Attack Loop
    try:
        print(f"{Fore.RED}[ATTACKER] AI Predator Engaged. Launching continuous assault...{Style.RESET_ALL}")
        
        while True:
            attack_choice = random.choice([
                "SSH_BRUTE", 
                "RADIOACTIVE_THEFT", 
                "STEALTH_C2", 
                "PORT_SCAN"
            ])
            
            print(f"{Fore.YELLOW}[RED TEAM] Executing: {attack_choice}{Style.RESET_ALL}")
            
            if attack_choice == "SSH_BRUTE":
                cmd = "hydra -l root -p password123 ssh://127.0.0.1 -s 22 -t 1 -f"
            elif attack_choice == "RADIOACTIVE_THEFT":
                cmd = "curl -k -s 'http://127.0.0.1:80/shell.php?cmd=cat+private_keys.txt'"
            elif attack_choice == "STEALTH_C2":
                cmd = "python3 -c 'import socket; s=socket.socket(); s.connect((\"127.0.0.1\",4444)); s.close()'"
            elif attack_choice == "PORT_SCAN":
                cmd = "nc -z -v 127.0.0.1 21 22 80 8888 9443"

            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(random.randint(5, 10))

    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[SHUTDOWN] Ceasefire initiated.{Style.RESET_ALL}")
    finally:
        os.killpg(os.getpgid(hub_process.pid), signal.SIGTERM)
        os.killpg(os.getpgid(rabbit_process.pid), signal.SIGTERM)
        hub_log.close()
        rabbit_log.close()
        print("War Room Securely Closed.")

if __name__ == "__main__":
    run_war_room()