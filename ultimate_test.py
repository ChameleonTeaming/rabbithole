import subprocess
import time
import os
import signal
import sys
import asyncio
import aiohttp

# ANSI Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_status(msg):
    print(f"{YELLOW}[*] {msg}{RESET}")

def print_success(msg):
    print(f"{GREEN}[+] {msg}{RESET}")

def print_fail(msg):
    print(f"{RED}[-] {msg}{RESET}")

async def test_http():
    print_status("Testing HTTP Honeypot (Port 8080)...")
    try:
        async with aiohttp.ClientSession() as session:
            # Normal Request
            async with session.get('http://127.0.0.1:8080/', timeout=5) as resp:
                if resp.status == 200:
                    print_success("HTTP Normal Request: OK")
                else:
                    print_fail(f"HTTP Normal Request Failed: {resp.status}")

            # Malicious Request (SQL Injection attempt)
            async with session.get('http://127.0.0.1:8080/admin.php?id=1 OR 1=1', timeout=5) as resp:
                text = await resp.text()
                # The AI should respond with something, effectively '200 OK' usually
                if resp.status == 200 and len(text) > 0:
                     print_success("HTTP Attack Request: Captured & Responded")
                else:
                     print_fail(f"HTTP Attack Request Failed: {resp.status}")
        return True
    except Exception as e:
        print_fail(f"HTTP Test Error: {e}")
        return False

def main():
    print(f"{GREEN}=== RABBITHOLE S-TIER VERIFICATION SUITE ==={RESET}")
    
    # 1. Start Honeypot
    print_status("Initializing RabbitHole Core...")
    # Use unbuffered output to catch startup errors immediately
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    
    log_file = open('rabbithole_test.log', 'w')
    process = subprocess.Popen(
        [sys.executable, 'rabbithole.py'], 
        stdout=log_file, 
        stderr=subprocess.STDOUT,
        env=env
    )
    
    # Wait for startup
    print_status("Waiting for services to bind...")
    time.sleep(10) # Give it generous time to bind 4 ports
    
    if process.poll() is not None:
        print_fail("RabbitHole failed to start! Check logs.")
        # stdout, stderr = process.communicate() # No longer valid with file redirection
        log_file.flush()
        with open('rabbithole_test.log', 'r') as f:
            print(f"LOGS:\n{f.read()}")
        log_file.close()
        return

    print_success(f"RabbitHole is ALIVE (PID: {process.pid})")

    try:
        # 2. Run Botnet Surge
        print_status("Phase 1: Botnet Surge Simulation (250 Concurrent Attackers)")
        try:
            subprocess.run([sys.executable, 'botnet_surge.py'], check=False, timeout=20)
        except subprocess.TimeoutExpired:
            print_success("Botnet Surge finished (timeout applied to infinite simulation).")
        
        # 3. Run Deception Audit
        print_status("Phase 2: AI Deception Entropy Audit")
        subprocess.run([sys.executable, 'deception_audit.py'], check=False)
        
        # 4. Run Fuzzer
        print_status("Phase 3: Protocol Fuzzing (Crash Resistance)")
        subprocess.run([sys.executable, 'fuzzer.py'], check=False)

        # 5. HTTP Test
        print_status("Phase 4: Web Honeypot Verification")
        asyncio.run(test_http())

    except Exception as e:
        print_fail(f"Test Suite Error: {e}")
    finally:
        print_status("Terminating RabbitHole...")
        os.kill(process.pid, signal.SIGTERM)
        process.wait()
        
        # Final check if it survived
        if process.returncode is not None and process.returncode != -15: # -15 is SIGTERM
             print_fail(f"RabbitHole crashed during test! Return code: {process.returncode}")
        else:
             print_success("RabbitHole survived the S-Tier Stress Test.")
             
        print_success("Test Complete.")

if __name__ == "__main__":
    main()
