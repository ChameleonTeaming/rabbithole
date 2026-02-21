from colorama import Fore, Style

class StrategicAnalyst:
    def __init__(self):
        # Knowledge Base: Mapping Tactic IDs to Strategic Intent (The "Why")
        self.knowledge_base = {
            "T1087": "Adversaries perform Account Discovery to understand the privilege context they are operating in. Knowing 'whoami' helps decide if privilege escalation is needed.",
            "T1124": "System Time Discovery is used to synchronize logs or schedule tasks effectively, often a precursor to time-based attacks.",
            "T1053": "Scheduled Task Discovery (Persistence) reveals existing automated jobs. Attackers check this to hide their own persistence mechanisms among legitimate tasks.",
            "T1027": "Obfuscated Files or Information helps adversaries evade static signature detection (like antivirus) by encoding payloads (e.g., Base64).",
            "T1003": "Credential Dumping aims to steal account hashes (like /etc/shadow). If successful, this allows lateral movement across the network.",
            "T1059": "Command and Scripting Interpreter (C2) establishes a communication channel back to the attacker, allowing remote control.",
            "T1552": "Unsecured Credentials (SSH Keys) allow adversaries to log into other systems without needing passwords, bypassing many auth controls.",
            "T1595": "Active Scanning identifies open ports and vulnerable services to target for initial access or lateral movement.",
            "T1110": "Brute Force attacks attempt to guess passwords. While noisy, they are effective against weak credentials.",
            "T1566": "Phishing exploits human trust to gain initial access via malicious links or attachments."
        }

    def analyze_performance(self, red_logs, blue_logs):
        """
        Correlates Red actions with Blue detections to generate insights.
        """
        insights = []
        
        # Map detections to attacks (simple timestamp/type correlation)
        # In a real system, we'd match exact timestamps, but for sim we check if threat was flagged.
        
        for attack in red_logs:
            tactic_id = attack['Event'].split(":")[1].split(" ")[1].strip() # Extract T1087 etc
            command = attack.get('Details', '')
            
            # The "Why"
            intent = self.knowledge_base.get(tactic_id, "Unknown Tactic Strategy.")
            
            # Did Blue detect it?
            detected = False
            for d in blue_logs:
                # Heuristic matching
                if tactic_id in d['Event'] or command in d['Details']: 
                    detected = True
                    break
            
            # The "Learning" (Adaptive Feedback)
            if detected:
                status = "🔴 CAUGHT"
                lesson = "Adaptive Response: The Blue Team signatures successfully flagged this behavior. **Next Steps:** Increase Jitter delay, change obfuscation method (e.g., use XOR instead of Base64), or switch to 'Living off the Land' binaries (LOLBAS)."
            else:
                status = "🟢 SUCCESS (Undetected)"
                lesson = "Reinforcement: Current stealth parameters are effective against current sensors. **Next Steps:** Proceed to next stage of kill chain. Maintain current noise level."

            insights.append({
                "Tactic": tactic_id,
                "Status": status,
                "Intent": intent,
                "Lesson": lesson
            })
            
        return insights
