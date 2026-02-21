import math
import re
import os

class AIEngine:
    @staticmethod
    def analyze_finding(finding):
        """
        Simulates advanced AI analysis using heuristics, entropy, and context awareness.
        """
        vuln_type = finding.get('type', 'Unknown')
        content = finding.get('content', '')
        file_path = finding.get('file', '')
        url = finding.get('url', '')
        
        # Default Analysis Structure
        analysis = {
            "risk_score": 0.0,
            "confidence": "LOW",
            "remediation": "",
            "ai_insight": ""
        }
        
        # Context Factors
        is_test_file = AIEngine._is_test_file(file_path)
        
        # --- HEURISTIC ANALYSIS ---
        
        if vuln_type == "hardcoded_secret":
            # Extract the potential secret value
            match = re.search(r'["\'](.*?)["\']', content)
            secret_value = match.group(1) if match else ""
            
            entropy = AIEngine._calculate_entropy(secret_value)
            is_placeholder = "example" in content.lower() or "test" in content.lower() or "1234" in secret_value
            
            if is_test_file:
                analysis['risk_score'] = 2.0
                analysis['confidence'] = "HIGH"
                analysis['ai_insight'] = "Credential found, but file context indicates this is a test/mock file. Likely a dummy secret."
                analysis['remediation'] = "Ensure this secret is not valid in production. Best practice: use environment variables even in tests."
            elif is_placeholder or entropy < 3.0:
                analysis['risk_score'] = 4.0
                analysis['confidence'] = "MEDIUM"
                analysis['ai_insight'] = f"detected a potential secret, but low entropy ({entropy:.2f}) suggests it might be a placeholder or default password."
                analysis['remediation'] = "Verify if this is a real secret. If it's a placeholder, remove it to reduce noise."
            else:
                analysis['risk_score'] = 9.8
                analysis['confidence'] = "HIGH"
                analysis['ai_insight'] = f"High-entropy string ({entropy:.2f}) detected in a non-test file. This has the statistical characteristics of a real API key or private key."
                analysis['remediation'] = "CRITICAL: Revoke this key immediately and rotate credentials. Use a secrets manager."

        elif vuln_type == "dangerous_function":
            # Heuristic: Is it executing a literal string (safe) or a variable (unsafe)?
            # Very basic check: look for quotes inside the parens
            if re.search(r'\(["\'].*["\']\)', content):
                analysis['risk_score'] = 3.0
                analysis['confidence'] = "MEDIUM"
                analysis['ai_insight'] = "Dangerous function detected, but it appears to be executing a static string. Risk is lower, but still bad practice."
                analysis['remediation'] = "Refactor to avoid using 'eval' or 'exec' entirely, even for static strings."
            else:
                analysis['risk_score'] = 9.0
                analysis['confidence'] = "HIGH"
                analysis['ai_insight'] = "Dynamic execution of code detected involving variables. If these variables are tainted by user input, this is RCE."
                analysis['remediation'] = "Replace with safer alternatives. Validate and sanitize all inputs strictly if this function is absolutely necessary."

        elif vuln_type == "sql_injection":
            if is_test_file:
                analysis['risk_score'] = 5.0
                analysis['ai_insight'] = "SQL concatenation found in a test file. Low immediate risk, but promotes bad coding habits."
            else:
                analysis['risk_score'] = 9.9
                analysis['confidence'] = "HIGH"
                analysis['ai_insight'] = "Classic SQL Injection pattern (string concatenation) detected. This is the #1 vector for data breaches."
                analysis['remediation'] = "Use parameterized queries (e.g., `cursor.execute('SELECT * FROM users WHERE id=?', (user_id,))`). NEVER concatenate strings for SQL."
            
        elif "XSS" in vuln_type:
            analysis['risk_score'] = 7.5
            analysis['confidence'] = "MEDIUM"
            analysis['remediation'] = "Context-aware output encoding is required. Use frameworks that auto-escape (like React/Vue) or libraries like 'bleach'."
            analysis['ai_insight'] = "Reflected user input detected. If this URL is clicked by an admin, an attacker could hijack their session."
            
        elif "Security Headers" in vuln_type:
            analysis['risk_score'] = 3.5
            analysis['confidence'] = "HIGH"
            analysis['remediation'] = "Update web server configuration (Nginx/Apache) or application middleware to inject these headers."
            analysis['ai_insight'] = "Missing defense-in-depth headers. This makes the application vulnerable to Clickjacking and MIME-sniffing attacks."

        elif vuln_type == "flask_debug":
            analysis['risk_score'] = 9.0
            analysis['confidence'] = "HIGH"
            analysis['ai_insight'] = "Flask app running in debug mode. This exposes the interactive Werkzeug debugger, allowing arbitrary code execution (RCE) if accessible."
            analysis['remediation'] = "Ensure 'debug=False' in production. Use environment variables to toggle this setting."

        elif vuln_type == "django_allowed_hosts":
            analysis['risk_score'] = 6.0
            analysis['confidence'] = "HIGH"
            analysis['ai_insight'] = "Django ALLOWED_HOSTS is set to wildcard '*'. This enables Host Header attacks, potentially leading to cache poisoning or password reset poisoning."
            analysis['remediation'] = "Set ALLOWED_HOSTS to a specific list of valid domain names for this deployment."

        elif vuln_type == "insecure_random":
            analysis['risk_score'] = 4.5
            analysis['confidence'] = "MEDIUM"
            analysis['ai_insight'] = "Standard 'random' module detected. It is not cryptographically secure and should not be used for generating tokens, passwords, or keys."
            analysis['remediation'] = "Use the 'secrets' module (Python 3.6+) or 'os.urandom()' for security-sensitive randomness."
            
        else:
            analysis['risk_score'] = 5.0
            analysis['ai_insight'] = "Generic vulnerability pattern matched. Manual review recommended."
            analysis['remediation'] = "Investigate the code context."

        return analysis

    @staticmethod
    def _is_test_file(path):
        """Checks if the file path suggests it is a test or documentation file."""
        if not path: return False
        path_lower = path.lower()
        indicators = ['/test/', '/tests/', 'test_', '_test', 'spec.', 'mock', 'example', 'docs/']
        return any(ind in path_lower for ind in indicators)

    @staticmethod
    def _calculate_entropy(text):
        """Calculates Shannon entropy to determine randomness of a string."""
        if not text:
            return 0
        entropy = 0
        for x in range(256):
            p_x = float(text.count(chr(x))) / len(text)
            if p_x > 0:
                entropy += - p_x * math.log(p_x, 2)
        return entropy