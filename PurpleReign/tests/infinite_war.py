import subprocess
import time
import sys
import os
import signal
import random
from colorama import Fore, Style, init

init(autoreset=True)

def run_infinite_war():
    print(f"{Fore.MAGENTA}==========================================")
    print(f"∞  INFINITE WAR: Continuous Attack Stream")
    print(f"=========================================={Style.RESET_ALL}")
    print(f"Press {Fore.RED}Ctrl+C{Style.RESET_ALL} to stop the war.")

    # 1. Start RabbitHole (if not already running)
    # Ideally, we assume you are running it separately or we launch it.
    # I'll launch it for you.
    print(f"{Fore.BLUE}[SETUP] Deploying RabbitHole...{Style.RESET_ALL}")
    rabbit_log = open("rabbithole_inf.log", "w")
    rabbit_process = subprocess.Popen(
        [sys.executable, "rabbithole.py"],
        stdout=rabbit_log,
        stderr=rabbit_log,
        cwd="/usr/lib/gemini-cli",
        preexec_fn=os.setsid
    )
    print(f"RabbitHole PID: {rabbit_process.pid}")
    print(f"\n{Fore.GREEN}--> OPEN DASHBOARD: http://localhost:8888{Style.RESET_ALL}\n")
    time.sleep(10)

    try:
        round_num = 1
        while True:
            attack_type = random.choice(["SSH_BRUTE", "PORT_SCAN", "C2_CONNECT"])
            print(f"{Fore.YELLOW}--- Round {round_num}: {attack_type} ---")
            
            if attack_type == "SSH_BRUTE":
                cmd = "hydra -l root -p password123 ssh://127.0.0.1 -s 22 -t 1 -f -V"
            elif attack_type == "PORT_SCAN":
                # Using nmap/nc if msfconsole is too slow for a loop
                cmd = "nc -z -v 127.0.0.1 21 22 80 8888"
            elif attack_type == "C2_CONNECT":
                # Connect to HTTP port pretending to be a bot
                cmd = "curl -A 'Botnet/1.0' http://127.0.0.1:80/shell.php"

            # Execute
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            delay = random.randint(3, 8)
            print(f"Attack sent. Sleeping {delay}s...")
            time.sleep(delay)
            round_num += 1

    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[STOP] Ceasefire initiated.{Style.RESET_ALL}")
    finally:
        os.killpg(os.getpgid(rabbit_process.pid), signal.SIGTERM)
        rabbit_log.close()
        print("RabbitHole Shutdown.")

if __name__ == "__main__":
    run_infinite_war()
