from rabbithole import HoneytokenGenerator, FakeFileSystem

print("Testing Apex Honeytoken Generator...")
fs = FakeFileSystem()
root = fs.root

# Check for .env
try:
    env_file = root['home']['user']['.env']
    print(f"[SUCCESS] Found .env honeytoken:\n{env_file}")
except KeyError:
    print("[FAIL] .env not found")

# Check for AWS
try:
    aws_creds = root['home']['user']['.aws']['credentials']
    print(f"\n[SUCCESS] Found AWS honeytoken:\n{aws_creds}")
except KeyError:
    print("[FAIL] .aws not found")
