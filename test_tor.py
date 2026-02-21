from rabbithole import ForensicTracer
import json

def test_tor_detection():
    print("Initializing ForensicTracer and fetching live Tor exit list...")
    tracer = ForensicTracer()
    
    # Test 1: Localhost (Should NOT be Tor)
    ip_local = "127.0.0.1"
    res_local = tracer.trace_ip(ip_local)
    print(f"\nTest 1: {ip_local}")
    print(f"  Is Tor? {res_local['is_tor']}")
    
    # Test 2: Known Tor Exit Node
    ip_tor = "171.25.193.25"
    res_tor = tracer.trace_ip(ip_tor)
    print(f"\nTest 2: {ip_tor}")
    print(f"  Is Tor? {res_tor['is_tor']}")
    
    if not res_local['is_tor'] and res_tor['is_tor']:
        print("\nTOR DETECTION TEST: PASSED")
    else:
        print("\nTOR DETECTION TEST: FAILED")

if __name__ == "__main__":
    test_tor_detection()
