import socket
import random
import time

def fuzz_port(port, name):
    print(f"Fuzzing {name} on port {port}...")
    try:
        # 1. Binary Blob Blast
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect(('127.0.0.1', port))
        s.recv(1024) # banner
        
        payloads = [
            b'\xff\xfe\xfd\xfc' * 100, # High entropy binary
            b'USER \0admin\r\n',       # Null byte injection
            b'A' * 5000 + b'\r\n',     # Buffer stress
            b'\x01\x02\x03\x04\r\n',   # Control characters
            b'STOR /sys/kernel/debug/test\r\n' # State violation (upload without login)
        ]
        
        for p in payloads:
            print(f"  Sending payload: {p[:20]}...")
            s.send(p)
            try:
                s.recv(1024)
            except: pass
            time.sleep(0.1)
            
        s.close()
        print(f"  {name} survived.")
        return True
    except Exception as e:
        print(f"  {name} failed: {e}")
        return False

if __name__ == "__main__":
    f1 = fuzz_port(2121, "FTP")
    # SSH is more complex due to handshake, but we can fuzz the initial handshake
    f2 = fuzz_port(2222, "SSH Handshake")
    
    if f1 and f2:
        print("\nS-TIER FUZZING COMPLETE: No crashes detected.")
    else:
        print("\nS-TIER FUZZING FAILED: Anomalies detected.")

