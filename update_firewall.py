# update_firewall.py

import subprocess
import os
import sys
try:
    import re
except ImportError:
    print("Error: 're' module not found. Please install it.")
    sys.exit(1)

BLOCKLIST_FILE = 'ip_blocklist.txt'
IPTABLES_CHAIN = 'INPUT' # Or a custom chain if you prefer, e.g., 'GEMINI_BLOCK'

def get_current_blocked_ips():
    """Retrieves currently blocked IPs from iptables."""
    try:
        result = subprocess.run(['sudo', 'iptables', '-L', IPTABLES_CHAIN, '-n'], capture_output=True, text=True, check=True)
        blocked_ips = set()
        for line in result.stdout.splitlines():
            # Example line: DROP       all  --  192.168.1.100        0.0.0.0/0
            match = re.search(r'DROP\s+all\s+--\s+([\d.]+)', line)
            if match:
                blocked_ips.add(match.group(1))
        return blocked_ips
    except subprocess.CalledProcessError as e:
        print(f"Error checking iptables rules: {e.stderr}")
        return set()
    except FileNotFoundError:
        print("Error: iptables command not found. Is iptables installed?")
        sys.exit(1)

def add_iptables_rule(ip):
    """Adds an iptables rule to drop traffic from a specific IP."""
    try:
        print(f"Adding iptables rule to block IP: {ip}")
        subprocess.run(['sudo', 'iptables', '-A', IPTABLES_CHAIN, '-s', ip, '-j', 'DROP'], check=True)
        print(f"Successfully blocked {ip}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error adding iptables rule for {ip}: {e.stderr}")
        return False

def save_iptables_rules():
    """Saves current iptables rules to make them persistent across reboots."""
    print("Saving iptables rules...")
    try:
        # For Debian/Ubuntu based systems
        subprocess.run(['sudo', 'netfilter-persistent', 'save'], check=True)
        print("Rules saved using netfilter-persistent.")
    except subprocess.CalledProcessError:
        try:
            # For RHEL/CentOS based systems
            subprocess.run(['sudo', 'service', 'iptables', 'save'], check=True)
            print("Rules saved using service iptables save.")
        except subprocess.CalledProcessError:
            print("Could not automatically save iptables rules. You may need to save them manually:")
            print("  sudo sh -c 'iptables-save > /etc/iptables/rules.v4'")
            print("  (or equivalent for your distribution)")
    except FileNotFoundError:
        print("netfilter-persistent or service iptables command not found. Please save rules manually.")

def main():
    if not os.path.exists(BLOCKLIST_FILE):
        print(f"Error: Blocklist file '{BLOCKLIST_FILE}' not found.")
        print("Please ensure the ip_blocklist.txt from your honeypot is in the same directory.")
        sys.exit(1)

    print(f"Reading IPs from {BLOCKLIST_FILE}...")
    new_ips_to_block = set()
    try:
        with open(BLOCKLIST_FILE, 'r') as f:
            for line in f:
                ip = line.strip()
                if ip and re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip): # Basic IP validation
                    new_ips_to_block.add(ip)
    except Exception as e:
        print(f"Error reading blocklist file: {e}")
        sys.exit(1)

    if not new_ips_to_block:
        print("No new IPs found in the blocklist to process.")
        sys.exit(0)

    current_blocked_ips = get_current_blocked_ips()
    ips_added_count = 0

    for ip in new_ips_to_block:
        if ip not in current_blocked_ips:
            if add_iptables_rule(ip):
                ips_added_count += 1
        else:
            print(f"IP {ip} is already blocked. Skipping.")

    if ips_added_count > 0:
        print(f"\nAdded {ips_added_count} new IP blocking rules.")
        save_iptables_rules()
    else:
        print("\nNo new IP blocking rules were added.")

if __name__ == '__main__':
    main()
