import os
import time
import psutil
import atexit
import threading
from colorama import Fore, Style

class DefenseSystem:
    def __init__(self):
        self.artifacts = set()
        self.compromised = False
        self.lock = threading.Lock()
        
        # Register cleanup on exit
        atexit.register(self.emergency_cleanup)

    def register_artifact(self, file_path):
        """
        Track a file created by Red Team for later deletion.
        """
        with self.lock:
            self.artifacts.add(file_path)

    def detect_debugger(self):
        """
        Checks if the current process is being traced (e.g., by strace, gdb).
        Linux specific: Checks TracerPid in /proc/self/status.
        """
        try:
            with open("/proc/self/status", "r") as f:
                for line in f:
                    if line.startswith("TracerPid"):
                        pid = int(line.split(":")[1].strip())
                        if pid > 0:
                            self.compromised = True
                            return True, pid
        except:
            pass
        return False, 0

    def emergency_cleanup(self):
        """
        The Janitor: Wipes all registered artifacts.
        """
        if not self.artifacts:
            return

        print(f"\n{Fore.YELLOW}[DEFENSE] Initiating Emergency Cleanup...{Style.RESET_ALL}")
        with self.lock:
            for artifact in list(self.artifacts):
                if os.path.exists(artifact):
                    try:
                        os.remove(artifact)
                        print(f"   -> Wiped: {artifact}")
                    except Exception as e:
                        print(f"   -> Failed to wipe {artifact}: {e}")
            self.artifacts.clear()

    def check_integrity(self):
        """
        Run a health check.
        """
        is_traced, pid = self.detect_debugger()
        if is_traced:
            return "COMPROMISED", f"Process is being traced by PID {pid}"
        return "SECURE", "System integrity verified."
