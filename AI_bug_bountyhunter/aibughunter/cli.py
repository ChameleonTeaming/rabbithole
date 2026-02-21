import argparse
import sys
from aibughunter.sast import StaticAnalyzer
from aibughunter.ast_engine import AdvancedAnalyzer
from aibughunter.dast import DynamicScanner
from aibughunter.ai_engine import AIEngine
from aibughunter.reporter import Reporter
from aibughunter.autofixer import AutoFixer
from aibughunter.utils import Logger

def main():
    parser = argparse.ArgumentParser(description="AI Bug Bounty Hunter - Hybrid Security Scanner")
    parser.add_argument("--scan-type", choices=["sast", "dast", "full"], required=True, help="Type of scan to perform")
    parser.add_argument("--target", required=True, help="Target directory (SAST) or URL (DAST)")
    parser.add_argument("--fix", action="store_true", help="Automatically fix detected vulnerabilities")
    
    args = parser.parse_args()
    
    findings = []
    
    Logger.header("AI Bug Bounty Hunter Initialized")

    # SAST Scan
    if args.scan_type in ["sast", "full"]:
        try:
            # 1. Regex Scan (Fast, supports multi-language)
            analyzer = StaticAnalyzer(args.target)
            sast_findings = analyzer.scan()
            findings.extend(sast_findings)
            
            # 2. Advanced AST Scan (Deep, Python only)
            ast_analyzer = AdvancedAnalyzer(args.target)
            ast_findings = ast_analyzer.scan()
            findings.extend(ast_findings)
            
        except Exception as e:
            Logger.error(f"SAST Scan failed: {str(e)}")

    # DAST Scan
    if args.scan_type in ["dast", "full"]:
        if not args.target.startswith("http"):
             if args.scan_type == "dast":
                 Logger.error("DAST target must be a URL starting with http/https")
                 sys.exit(1)
             else:
                 Logger.warning("Skipping DAST scan (target is not a URL)")
        else:
            try:
                scanner = DynamicScanner(args.target)
                dast_findings = scanner.scan()
                findings.extend(dast_findings)
            except Exception as e:
                Logger.error(f"DAST Scan failed: {str(e)}")

    # AI Analysis & Enrichment
    Logger.header("Analyzing Findings with AI Engine")
    enriched_findings = []
    for finding in findings:
        ai_analysis = AIEngine.analyze_finding(finding)
        finding.update(ai_analysis)
        enriched_findings.append(finding)
        
        Logger.info(f"Analyzed: {finding['type']} - Risk Score: {finding['risk_score']}/10")

    # Reporting
    if enriched_findings:
        reporter = Reporter(enriched_findings)
        reporter.generate_json()
        reporter.generate_markdown()
        
        # Auto-Remediation
        if args.fix:
            fixer = AutoFixer(enriched_findings)
            fixer.apply_fixes()
            
    else:
        Logger.warning("No vulnerabilities found.")

if __name__ == "__main__":
    main()
