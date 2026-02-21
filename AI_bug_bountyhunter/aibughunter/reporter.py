import json
import os
from datetime import datetime
from aibughunter.utils import Logger

class Reporter:
    def __init__(self, findings):
        self.findings = findings
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.report_dir = "reports"
        
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)

    def generate_json(self):
        filename = f"{self.report_dir}/scan_report_{self.timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(self.findings, f, indent=4)
        Logger.success(f"JSON Report saved to: {filename}")

    def generate_markdown(self):
        filename = f"{self.report_dir}/scan_report_{self.timestamp}.md"
        with open(filename, 'w') as f:
            f.write(f"# AI Bug Bounty Hunter Report\n")
            f.write(f"**Date:** {self.timestamp}\n\n")
            f.write(f"## Executive Summary\n")
            f.write(f"Total Findings: {len(self.findings)}\n\n")
            
            for i, finding in enumerate(self.findings):
                f.write(f"### {i+1}. {finding.get('type', 'Unknown Vulnerability')}\n")
                f.write(f"- **Severity:** {finding.get('severity', 'Unknown')}\n")
                f.write(f"- **Confidence:** {finding.get('confidence', 'N/A')}\n")
                f.write(f"- **Location:** {finding.get('file', finding.get('url', 'N/A'))}\n")
                f.write(f"- **Line:** {finding.get('line', 'N/A')}\n")
                f.write(f"- **AI Insight:** {finding.get('ai_insight', 'N/A')}\n")
                f.write(f"- **Remediation:** {finding.get('remediation', 'N/A')}\n")
                f.write(f"\n---\n")
                
        Logger.success(f"Markdown Report saved to: {filename}")
