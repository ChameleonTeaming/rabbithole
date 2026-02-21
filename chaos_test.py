import threading
import socket
import time
import json
import random

# Configuration
HOST = '127.0.0.1'
PORT = 2121 # Using FTP for speed (SSH handshake is slow for stress testing)
THREADS = 50
OPERATIONS_PER_THREAD = 20

def attack_worker(thread_id):
    """Simulates a concurrent attacker trying to corrupt the filesystem."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        s.recv(1024) # Banner
        
        # Login
        s.send(b"USER stress_test\r\n")
        s.recv(1024)
        s.send(b"PASS 1234\r\n")
        s.recv(1024)
        
        # Hammer the filesystem
        for i in range(OPERATIONS_PER_THREAD):
            filename = f"corruption_test_{thread_id}_{i}.txt"
            # FTP MKD (Make Directory) maps to fake_fs.mkdir() which saves state
            s.send(f"MKD {filename}\r\n".encode())
            resp = s.recv(1024).decode()
            
            # Random sleep to interleave threads
            time.sleep(random.uniform(0.001, 0.01))
            
        s.close()
        return True
    except Exception as e:
        return False

def check_integrity():
    """Verifies if the JSON file is still valid and contains expected data."""
    try:
        with open('filesystem.json', 'r') as f:
            data = json.load(f)
        
        print("[INTEGRITY CHECK] JSON is valid.")
        
        # Count created directories
        # Note: MKD creates directories in current CWD (root by default)
        count = 0
        for key in data:
            if key.startswith("corruption_test_"):
                count += 1
        
        expected = THREADS * OPERATIONS_PER_THREAD
        print(f"[DATA AUDIT] Found {count}/{expected} created items.")
        
        if count == expected:
            return True
        else:
            print(f"[WARNING] Lost {expected - count} writes due to race conditions (Expected if no locking).")
            # If locking works, this should be close to 0 loss, but FTP protocol overhead might cause drops before FS
            return False
            
    except json.JSONDecodeError:
        print("[CRITICAL FAIL] filesystem.json is CORRUPTED (Invalid JSON).")
        return False
    except Exception as e:
        print(f"[FAIL] Error checking integrity: {e}")
        return False

def main():
    print(f"=== GOVERNMENT-LEVEL CORRUPTION STRESS TEST ===")
    print(f"Target: {HOST}:{PORT}")
    print(f"Load: {THREADS} Concurrent Threads x {OPERATIONS_PER_THREAD} Writes")
    print(f"Goal: Crash the persistence layer or corrupt JSON.")
    
    threads = []
    start_time = time.time()
    
    for i in range(THREADS):
        t = threading.Thread(target=attack_worker, args=(i,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    duration = time.time() - start_time
    print(f"\nAttack Complete in {duration:.2f}s.")
    
    if check_integrity():
        print("\n>>> S-TIER STATUS CONFIRMED: ZERO DATA CORRUPTION <<<")
    else:
        print("\n>>> SYSTEM FAILED: DATA CORRUPTION DETECTED <<<")

if __name__ == "__main__":
    main()
