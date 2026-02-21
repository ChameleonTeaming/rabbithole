import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from aibughunter.utils import Logger
import random

class DynamicScanner:
    def __init__(self, target_url):
        self.target_url = target_url
        self.findings = []
        self.session = requests.Session()
        self.user_agent = "AI-Bug-Bounty-Hunter/1.0"
        
        self.payloads = {
            "sql_injection": ["' OR '1'='1", "admin' --", "' UNION SELECT 1, user(), 3--", "1' ORDER BY 1--"],
            "xss": ["<script>alert(1)</script>", "<img src=x onerror=alert(1)>", "javascript:alert(1)"],
            "path_traversal": ["../../../../etc/passwd", "../boot.ini"]
        }

    def scan(self):
        Logger.header(f"Starting DAST Scan on: {self.target_url}")
        
        try:
            response = self.session.get(self.target_url, timeout=5, headers={"User-Agent": self.user_agent})
            if response.status_code != 200:
                Logger.warning(f"Target URL returned status code: {response.status_code}")
            
            # 1. Scan for XSS in forms
            self._scan_forms(response.text)
            
            # 2. Fuzz URL parameters
            self._fuzz_params(self.target_url)

            # 3. Check for interesting headers
            self._check_headers(response.headers)
            
        except requests.RequestException as e:
            Logger.error(f"Connection failed: {str(e)}")
            
        return self.findings

    def _scan_forms(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        forms = soup.find_all('form')
        
        Logger.info(f"Found {len(forms)} forms to test.")
        
        for form in forms:
            action = form.get('action')
            method = form.get('method', 'get').lower()
            inputs = form.find_all('input')
            
            target_url = urljoin(self.target_url, action)
            data = {}
            
            for input_tag in inputs:
                name = input_tag.get('name')
                input_type = input_tag.get('type')
                if name:
                    if input_type == 'text':
                        data[name] = self.payloads['xss'][0] # Try basic XSS
                    else:
                        data[name] = "test"

            if method == 'post':
                try:
                    res = self.session.post(target_url, data=data, timeout=3)
                    if self.payloads['xss'][0] in res.text:
                        self.findings.append({
                            "type": "Reflected XSS",
                            "url": target_url,
                            "payload": self.payloads['xss'][0],
                            "severity": "HIGH"
                        })
                except:
                    pass
            else:
                # Handle GET forms similarly
                pass

    def _fuzz_params(self, url):
        parsed = urlparse(url)
        if not parsed.query:
            return

        params = parsed.query.split('&')
        base_url = url.split('?')[0]
        
        for param in params:
            if '=' not in param: continue
            key = param.split('=')[0]
            
            # Test SQLi
            for payload in self.payloads['sql_injection']:
                fuzzed_url = f"{base_url}?{key}={payload}"
                try:
                    res = self.session.get(fuzzed_url, timeout=3)
                    # Simple heuristic: Look for database errors
                    if "syntax error" in res.text.lower() or "mysql" in res.text.lower():
                         self.findings.append({
                            "type": "SQL Injection",
                            "url": fuzzed_url,
                            "payload": payload,
                            "severity": "CRITICAL"
                        })
                except:
                    pass

    def _check_headers(self, headers):
        missing_headers = []
        security_headers = [
            "Content-Security-Policy",
            "X-Frame-Options", 
            "X-Content-Type-Options",
            "Strict-Transport-Security"
        ]
        
        for h in security_headers:
            if h not in headers:
                missing_headers.append(h)
        
        if missing_headers:
            self.findings.append({
                "type": "Missing Security Headers",
                "details": ", ".join(missing_headers),
                "severity": "LOW"
            })
