import streamlit as st
import time
from dataclasses import dataclass, field

# ----------------------- Session State Classes -----------------------
@dataclass
class AutomationState:
    running: bool = False
    logs: list = field(default_factory=list)

@dataclass
class UserSession:
    logged_in: bool = False
    user_id: str = ""
    automation_state: AutomationState = field(default_factory=AutomationState)
    config: dict = field(default_factory=dict)

# ----------------------- Initialize Session State -----------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = ""
if "automation_state" not in st.session_state:
    st.session_state.automation_state = AutomationState()
if "config" not in st.session_state:
    st.session_state.config = {"chat_id": ""}

# ----------------------- Login Page -----------------------
def login_page():
    st.title("🔑 लॉगिन पेज")
    username = st.text_input("यूजरनेम")
    password = st.text_input("पासवर्ड", type="password")
    if st.button("लॉगिन करें"):
        if username == "admin" and password == "1234":  # Simple example
            st.session_state.logged_in = True
            st.session_state.user_id = username
            st.success("✅ लॉगिन सफल!")
            st.experimental_rerun()
        else:
            st.error("❌ गलत यूजरनेम या पासवर्ड!")

# ----------------------- Automation Functions -----------------------
def start_automation(user_config, user_id):
    st.session_state.automation_state.running = True
    st.session_state.automation_state.logs.append(f"[{time.strftime('%H:%M:%S')}] ऑटोमेशन शुरू हो गया!")
    # Example loop to simulate logs
    for i in range(5):
        if not st.session_state.automation_state.running:
            st.session_state.automation_state.logs.append(f"[{time.strftime('%H:%M:%S')}] ऑटोमेशन रोका गया।")
            break
        st.session_state.automation_state.logs.append(f"[{time.strftime('%H:%M:%S')}] मैसेज भेजा गया #{i+1}...")
        time.sleep(1)
    st.session_state.automation_state.running = False
    st.session_state.automation_state.logs.append(f"[{time.strftime('%H:%M:%S')}] ऑटोमेशन समाप्त।")

def stop_automation(user_id):
    st.session_state.automation_state.running = False
    st.session_state.automation_state.logs.append(f"[{time.strftime('%H:%M:%S')}] ऑटोमेशन को मैन्युअली रोका गया।")

# ----------------------- Main App -----------------------
def main_app():
    st.title("🤖 ऑटोमेशन डैशबोर्ड")
    
    # User config
    st.subheader("⚙️ कॉन्फ़िगरेशन")
    chat_id = st.text_input("चैट आईडी", value=st.session_state.config.get("chat_id", ""))
    if st.button("💾 सेव करें"):
        st.session_state.config['chat_id'] = chat_id
        st.success("✅ कॉन्फ़िगरेशन सेव हो गया!")
    
    # Automation controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ ऑटोमेशन शुरू करें", disabled=st.session_state.automation_state.running):
            if st.session_state.config.get('chat_id'):
                start_automation(st.session_state.config, st.session_state.user_id)
                st.success("✅ ऑटोमेशन शुरू हो गया!")
                st.experimental_rerun()
            else:
                st.error("❌ पहले कॉन्फ़िगरेशन में चैट आईडी सेट करें!")
    
    with col2:
        if st.button("⏹️ ऑटोमेशन रोकें", disabled=not st.session_state.automation_state.running):
            stop_automation(st.session_state.user_id)
            st.warning("⚠️ ऑटोमेशन रोका गया!")
            st.experimental_rerun()
    
    # Logs
    if st.session_state.automation_state.logs:
        st.markdown("### 📊 लाइव लॉग्स")
        logs_html = '<div class="console-output">'
        for log in st.session_state.automation_state.logs[-30:]:
            logs_html += f'<div class="console-line">{log}</div>'
        logs_html += '</div>'
        st.markdown(logs_html, unsafe_allow_html=True)
        
        if st.button("🔄 लॉग्स रीफ्रेश करें"):
            st.experimental_rerun()
    
    # Footer
    st.markdown('<div class="footer">MADE WITH ❤️ BY YKTI RAWAT | © 2026</div>', unsafe_allow_html=True)

# ----------------------- Run -----------------------
if not st.session_state.logged_in:
    login_page()
else:
    main_app()
