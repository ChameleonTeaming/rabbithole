import ipaddress
import logging
import time
import os

class SafetyInterlock:
    def __init__(self, allowed_subnets=["127.0.0.1/32", "::1/128"]):
        self.allowed_networks = [ipaddress.ip_network(n) for n in allowed_subnets]
        self._setup_audit_logging()

    def _setup_audit_logging(self):
        logging.basicConfig(
            filename='audit_compliance.log',
            level=logging.INFO,
            format='%(asctime)s | USER_ACTION | %(message)s'
        )

    def is_target_allowed(self, ip_str):
        """
        Validates if a target IP is within the authorized scope.
        Blocks public IPs and non-whitelisted private IPs.
        """
        try:
            target = ipaddress.ip_address(ip_str)
            for net in self.allowed_networks:
                if target in net:
                    return True
            return False
        except ValueError:
            return False

    def authorize_attack(self, tool_name, target, user_consent=True):
        """
        The Gatekeeper. Returns True if attack is legal and in-scope.
        """
        if not user_consent:
            logging.warning(f"BLOCKED: {tool_name} against {target} - No Consent")
            return False, "User consent required."

        if not self.is_target_allowed(target):
            msg = f"SCOPE VIOLATION: {target} is not in the whitelist."
            logging.critical(f"BLOCKED: {tool_name} against {target} - {msg}")
            return False, msg

        logging.info(f"AUTHORIZED: {tool_name} against {target}")
        return True, "Authorized"
