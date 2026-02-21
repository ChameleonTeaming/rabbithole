import streamlit as st
import os
import time
import subprocess
import sys
from aibughunter.sast import StaticAnalyzer
from aibughunter.ai_engine import AIEngine
from aibughunter.autofixer import AutoFixer

# --- HELPER FOR CLI LAUNCH ---
def run_gui():
    """Entry point for 'ai-bug-hunter-gui' command."""
    # Find the path to this script
    script_path = os.path.abspath(__file__)
    # Launch Streamlit pointing to this file
    # We use sys.executable to ensure we use the same python env
    cmd = [sys.executable, "-m", "streamlit", "run", script_path]
    print(f"Launching GUI: {' '.join(cmd)}")
    subprocess.call(cmd)

# --- STREAMLIT APP ---
if __name__ == "__main__" or "streamlit" in sys.modules:
    st.set_page_config(page_title="AI Bug Bounty Hunter", layout="wide")

    st.title("🛡️ AI Bug Bounty Hunter - Command Center")

    # Sidebar
    st.sidebar.header("Configuration")
    scan_dir = st.sidebar.text_input("Target Directory", value="tests")
    run_scan = st.sidebar.button("Run Security Scan")

    if 'findings' not in st.session_state:
        st.session_state['findings'] = []

    # --- SCAN LOGIC ---
    if run_scan:
        with st.spinner(f"Scanning {scan_dir}..."):
            analyzer = StaticAnalyzer(scan_dir)
            raw_findings = analyzer.scan()
            
            enriched_findings = []
            for f in raw_findings:
                ai_analysis = AIEngine.analyze_finding(f)
                f.update(ai_analysis)
                enriched_findings.append(f)
                
            st.session_state['findings'] = enriched_findings
            st.success(f"Scan complete! Found {len(enriched_findings)} potential vulnerabilities.")

    # --- RESULTS DISPLAY ---
    if st.session_state['findings']:
        st.subheader("🔍 Vulnerability Report")
        
        # Summary Metrics
        col1, col2, col3 = st.columns(3)
        high_risk = sum(1 for f in st.session_state['findings'] if f['risk_score'] >= 7.0)
        med_risk = sum(1 for f in st.session_state['findings'] if 4.0 <= f['risk_score'] < 7.0)
        low_risk = sum(1 for f in st.session_state['findings'] if f['risk_score'] < 4.0)
        
        col1.metric("Critical / High Risk", high_risk, delta_color="inverse")
        col2.metric("Medium Risk", med_risk, delta_color="off")
        col3.metric("Low Risk", low_risk, delta_color="normal")

        # Detailed Findings Table
        selected_finding_idx = st.selectbox(
            "Select a Vulnerability to Inspect & Fix",
            range(len(st.session_state['findings'])),
            format_func=lambda i: f"{st.session_state['findings'][i]['type']} (Risk: {st.session_state['findings'][i]['risk_score']})"
        )
        
        finding = st.session_state['findings'][selected_finding_idx]
        
        # --- INSPECTION & FIX ---
        st.markdown("---")
        c1, c2 = st.columns([1, 1])
        
        with c1:
            st.subheader("⚠️ Vulnerability Details")
            st.write(f"**Type:** {finding['type']}")
            st.write(f"**File:** `{finding['file']}` : Line {finding['line']}")
            st.write(f"**Severity:** {finding['severity']}")
            st.info(f"**AI Insight:** {finding['ai_insight']}")
            st.warning(f"**Remediation:** {finding['remediation']}")

        with c2:
            st.subheader("🛠️ Auto-Remediation Preview")
            
            fixer = AutoFixer()
            file_path = finding['file']
            
            if os.path.exists(file_path):
                original_code, fixed_code = fixer.preview_fix(file_path, finding)
                
                # Simple Diff Display
                if original_code == fixed_code:
                    st.success("No code changes required or already fixed.")
                else:
                    st.code(fixed_code, language='python')
                    st.caption("Above shows the proposed safer code.")
                    
                    if st.button("Apply Fix & Verify"):
                        try:
                            with open(file_path, 'w') as f:
                                f.write(fixed_code)
                            st.success("Fix Applied Successfully!")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to write file: {e}")
            else:
                st.error("File not found.")

    # --- MANUAL VERIFICATION TEST ---
    st.markdown("---")
    st.subheader("🧪 Verification Sandbox")
    if st.button("Check Syntax of Target"):
        # Safe syntax check using ast module (no disk writes)
        import ast
        try:
            # We assume target is the one we just fixed if possible, or user input
            # For simplicity, let's use the file from the selected finding
            target_file = None
            if st.session_state['findings']:
                target_file = st.session_state['findings'][selected_finding_idx]['file']
            
            if target_file and os.path.exists(target_file):
                with open(target_file, "r") as f:
                    source = f.read()
                ast.parse(source)
                st.success(f"{target_file}: Code compiles successfully! Syntax is valid.")
            else:
                 st.warning("Select a finding to verify its file.")
        except SyntaxError as e:
            st.error(f"Syntax Error:\n{e}")
        except Exception as e:
            st.error(f"Check failed: {e}")