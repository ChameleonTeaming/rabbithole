from modules.osint import OSINTProfiler

# Initialize
profiler = OSINTProfiler()

# Target
target_ip = "185.247.137.194"

# Run Analysis
print(f"--- RUNNING INTEL PROBE ON {target_ip} ---")
report = profiler.analyze_ip(target_ip)

print(f"\n--- DOSSIER ---")
print(f"Target: {report['target']}")
print(f"Geo: {report['geo']['city']}, {report['geo']['country']}")
print(f"ISP: {report['geo']['isp']}")
print(f"Abuse Score: {report['reputation']['abuse_score']}")
print(f"Threat Level: {report['threat_level']}")
