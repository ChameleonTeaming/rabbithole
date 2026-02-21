import socket
import time
import statistics

def measure_latency(port, cmd):
    latencies = []
    for _ in range(5):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', port))
        s.recv(1024) # banner
        
        start = time.time()
        s.send(cmd.encode() + b'\r\n')
        s.recv(1024)
        latencies.append(time.time() - start)
        s.close()
        time.sleep(0.5)
    return latencies

if __name__ == "__main__":
    print("Measuring FTP response jitter (Stealth Audit)...")
    # Benign command (should be fast)
    benign = measure_latency(2121, "USER admin")
    # AI command (should have tarpit + AI delay)
    malicious = measure_latency(2121, "RECON_PROBE")
    
    print(f"\nBenign Avg: {statistics.mean(benign):.4f}s | StDev: {statistics.stdev(benign):.4f}s")
    print(f"Malicious Avg: {statistics.mean(malicious):.4f}s | StDev: {statistics.stdev(malicious):.4f}s")
    
    # S-Tier Requirement: High Standard Deviation (Jitter)
    if statistics.stdev(malicious) > 0.1:
        print("\nSTEALTH AUDIT PASSED: High response jitter detected. Timing attacks mitigated.")
    else:
        print("\nSTEALTH AUDIT FAILED: Constant response timing detected. Fingerprinting possible.")
