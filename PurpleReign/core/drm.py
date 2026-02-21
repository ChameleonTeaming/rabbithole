import hashlib
import os
import sys
from colorama import Fore, Style

class LicenseManager:
    def __init__(self):
        self.license_file = "license.key"
        # In production, this secret would be hidden in compiled C-code or a remote server
        self.secret_salt = "PURPLE_REIGN_OFFICIAL_RELEASE_2026_SECURE"

    def generate_license(self, user_id):
        """Generates a valid license string for a given user."""
        raw = f"{user_id}:{self.secret_salt}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def validate_license(self):
        """
        Checks if the local license.key is valid.
        Terminates the program if invalid.
        """
        if not os.path.exists(self.license_file):
            self._violation("License file missing.")

        try:
            with open(self.license_file, 'r') as f:
                key_data = f.read().strip()
            
            # For this strict prototype, we expect a specific Authorized User key
            expected_key = self.generate_license("AUTHORIZED_ADMIN")
            
            if key_data != expected_key:
                self._violation("Invalid or pirated license key detected.")
                
            return True
            
        except Exception as e:
            self._violation(f"License check failed: {e}")

    def _violation(self, reason):
        print(f"\n{Fore.RED}=============================================")
        print(f"⛔ ACCESS DENIED: PIRACY PROTECTION ACTIVE")
        print(f"============================================={Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Reason: {reason}{Style.RESET_ALL}")
        print("Please contact the developer for a valid license.")
        sys.exit(1)

# Utility to create the key (Run this once securely)
if __name__ == "__main__":
    mgr = LicenseManager()
    key = mgr.generate_license("AUTHORIZED_ADMIN")
    with open("license.key", "w") as f:
        f.write(key)
    print(f"License generated: {key}")
