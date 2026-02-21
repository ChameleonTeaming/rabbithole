import re
import time
from collections import deque
from colorama import Fore, Style

class AIArmor:
    def __init__(self):
        # Rolling window for rate limiting (last 60 seconds)
        self.event_window = deque(maxlen=1000)
        self.alert_threshold = 50 # Max 50 events per second is suspicious
        self.suppressed = False

    def sanitize_input(self, text):
        """
        Cleans text of control characters, ANSI codes, and excessive length
        to prevent log poisoning or terminal corruption attacks.
        """
        if not isinstance(text, str):
            return str(text)
            
        # 1. Truncate massive inputs (Buffer Overflow Defense)
        if len(text) > 1024:
            text = text[:1024] + "...[TRUNCATED]"

        # 2. Strip ANSI Escape Codes (Terminal Injection)
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|[\[0-?]*[ -/]*[@-~])')
        text = ansi_escape.sub('', text)

        # 3. Strip non-printable chars (Binary/Fuzzing payloads)
        # Keep basic ASCII + common symbols
        text = re.sub(r'[^\x20-\x7E\n\r\t]', '', text)
        
        return text

    def is_under_attack(self):
        """
        Detects Volumetric Attacks (Fuzzing/Flooding).
        Returns True if event rate exceeds human/normal speed.
        """
        now = time.time()
        # Clean old events
        while self.event_window and now - self.event_window[0] > 1.0:
            self.event_window.popleft()
            
        self.event_window.append(now)
        
        if len(self.event_window) > self.alert_threshold:
            if not self.suppressed:
                print(f"{Fore.RED}[ARMOR] 🛡️ ANOMALY DETECTED: Input Flood! Throttling sensors...{Style.RESET_ALL}")
                self.suppressed = True
            return True
            
        if self.suppressed and len(self.event_window) < (self.alert_threshold / 2):
            print(f"{Fore.GREEN}[ARMOR] Threat subsided. Sensors engaging.{Style.RESET_ALL}")
            self.suppressed = False
            
        return False

    def validate_logic(self, tactic_id):
        """
        Ensures tactic IDs match expected format (Txxxx) to prevent
        logic injection or 'jailbreak' strings passing through as IDs.
        """
        if re.match(r'^T\d{4}(\.\d{3})?$', tactic_id):
            return True
        return False
