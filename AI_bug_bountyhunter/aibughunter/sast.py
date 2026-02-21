import os
import re
from aibughunter.utils import Logger

class StaticAnalyzer:
    def __init__(self, target_dir):
        self.target_dir = target_dir
        self.findings = []
        
        # Regex patterns for common vulnerabilities
        self.patterns = {
            'hardcoded_secret': r'(?i)([a-z0-9_]*(api_key|secret|password|token)[a-z0-9_]*)\s*=\s*["\'][a-zA-Z0-9_\-!@#$%^&*]{8,}["\']',
            'dangerous_function': r'(?i)\b(eval\(|exec\(|os\.system\(|subprocess\.call\()',
            'sql_injection': r'(?i)(SELECT|INSERT|UPDATE|DELETE).*WHERE.*["\']\s*\+\s*[a-zA-Z_]',
            'xss_vulnerability': r'(?i)(innerHTML|document\.write\(|echo\s*\$_(GET|POST|REQUEST))',
            'flask_debug': r'(?i)app\.run\(.*debug\s*=\s*True',
            'django_allowed_hosts': r'(?i)ALLOWED_HOSTS\s*=\s*\[.*[\'"]\*[\'"].*\]',
            'insecure_random': r'(?i)random\.(randint|choice|random)\('
        }

    def scan(self):
        Logger.header(f"Starting SAST Scan on: {self.target_dir}")
        
        if os.path.isfile(self.target_dir):
            if self.target_dir.endswith((".py", ".js", ".php", ".html", ".java", ".go")):
                self._analyze_file(self.target_dir)
        else:
            for root, _, files in os.walk(self.target_dir):
                if "venv" in root or ".git" in root or "__pycache__" in root:
                    continue
                    
                for file in files:
                    if file.endswith((".py", ".js", ".php", ".html", ".java", ".go")):
                        self._analyze_file(os.path.join(root, file))
        
        return self.findings

    def _analyze_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            for i, line in enumerate(lines):
                for vul_type, pattern in self.patterns.items():
                    if re.search(pattern, line):
                        self.findings.append({
                            "type": vul_type,
                            "file": file_path,
                            "line": i + 1,
                            "content": line.strip(),
                            "severity": "HIGH" if vul_type in ["hardcoded_secret", "sql_injection"] else "MEDIUM"
                        })
                        
        except Exception as e:
            Logger.error(f"Could not read file {file_path}: {str(e)}")
