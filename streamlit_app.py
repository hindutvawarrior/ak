import streamlit as st
import streamlit.components.v1 as components
import time
import threading
import uuid
import hashlib
import os
import subprocess
import json
import urllib.parse
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import database as db
import requests

st.set_page_config(
    page_title="YKTI RAWAT",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------ CUSTOM CSS (NEW BOX DESIGN + CLEANER HEADER) ------------------
custom_css = """
        <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap');
    * { font-family: 'Poppins', sans-serif; }

    body { background: linear-gradient(135deg, #0f172a 0%, #071029 100%); }

    .main .block-container {
        background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(250,250,250,0.95));
        border-radius: 18px;
        padding: 26px 28px;
        border: 1px solid rgba(255,255,255,0.06);
        box-shadow: 0 10px 30px rgba(2,6,23,0.6);
    }

    .app-header {
        display: flex; align-items: center; gap: 20px; padding: 18px;
        border-radius: 14px; margin-bottom: 18px; background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.04);
    }

    .app-header h1 { color: #f8fafc; margin:0; font-size: 28px; letter-spacing: 1px; }
    .app-header p { margin:0; color: #a6b0c3 }

    /* BOX CARD */
    .card {
        background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(248,249,250,0.95));
        border-radius: 14px; padding: 18px; border: 1px solid rgba(3,7,18,0.05);
        box-shadow: 0 6px 18px rgba(3,7,18,0.06);
    }

    label { color: #0f172a !important; font-weight: 700 !important; }

    .stButton>button { background: linear-gradient(90deg,#00c6ff,#0072ff); color: #fff; border-radius:10px; padding:10px 18px; font-weight:700 }

    .file-dropzone { border: 2px dashed rgba(7,10,29,0.08); border-radius: 10px; padding: 12px; }

    .sidebar .sidebar-content { background: rgba(255,255,255,0.02); }

    .footer { text-align:center; color:#94a3b8; margin-top:18px; }

    .small-muted { color: #6b7280; font-size: 0.9rem }

</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# ------------------ SESSION STATE (no username/password login) ------------------
if 'user_id' not in st.session_state or not st.session_state.user_id:
    # default to a single local user id (you can change this if your `db` expects another id)
    st.session_state.user_id = 1
if 'username' not in st.session_state:
    st.session_state.username = 'Local'
if 'automation_running' not in st.session_state:
    st.session_state.automation_running = False
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'message_count' not in st.session_state:
    st.session_state.message_count = 0

class AutomationState:
    def __init__(self):
        self.running = False
        self.message_count = 0
        self.logs = []
        self.message_rotation_index = 0

if 'automation_state' not in st.session_state:
    st.session_state.automation_state = AutomationState()

if 'auto_start_checked' not in st.session_state:
    st.session_state.auto_start_checked = False

# ------------------ Utilities (unchanged logic mostly) ------------------

def log_message(msg, automation_state=None):
    timestamp = time.strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"
    if automation_state:
        automation_state.logs.append(formatted_msg)
    else:
        st.session_state.logs.append(formatted_msg)

# (Keep other helper functions identical; trimmed here to focus on the UI changes)
# For brevity in this file we import the remaining functions from the original streamlit_app
# rather than duplicating huge blocks. If your environment needs a single-file, paste those
# functions below (find_message_input, setup_browser, send_messages, etc.).

# ------------------ UI: simplified - no login/signup (user requested)

st.markdown(f"""
<div class="app-header">
    <div>
        <h1>🦂 YKTI RAWAT — CONVERSATION AUTOMATION</h1>
        <p class="small-muted">Offline E2EE conversation tool · Multiple cookies · TXT upload messages</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar user info (login removed as requested)
st.sidebar.markdown('<div class="card">', unsafe_allow_html=True)
st.sidebar.markdown(f"**USERNAME:** {st.session_state.username}")
st.sidebar.markdown(f"**USER ID:** {st.session_state.user_id}")
st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Load user configuration if any
user_config = db.get_user_config(st.session_state.user_id) if hasattr(db, 'get_user_config') else None

# If no config in DB, create a local default config object to avoid breaking the UI
if not user_config:
    user_config = {
        'chat_id': '',
        'name_prefix': '',
        'delay': 5,
        'cookies': '',
        'messages': 'Hello!'
    }

# Tabs: Configuration + Automation (same structure)
tab1, tab2 = st.tabs(["⚙️ CONFIGURATION", "🚀 AUTOMATION"])

with tab1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        chat_id = st.text_input("CHAT/CONVERSATION E2EE ID", value=user_config.get('chat_id', ''), placeholder="e.g., 1362400298935018")
        name_prefix = st.text_input("NAME PREFIX", value=user_config.get('name_prefix', ''), placeholder="e.g., [YKTI RAWAT]")
        delay = st.number_input("DELAY (SECONDS)", min_value=1, max_value=300, value=int(user_config.get('delay', 5)))

    with col2:
        st.markdown("**COOKIES (multiple support)**")
        st.markdown("- You can paste multiple cookies separated by a blank line (each cookie string will be used in turn).")
        cookies_text = st.text_area("PASTE COOKIES (one cookie per block) ", value=user_config.get('cookies', ''), height=140)

        st.markdown("**OR UPLOAD A COOKIES TXT**")
        cookies_file = st.file_uploader("Upload cookies .txt (each cookie block separated by an empty line)", type=['txt'])
        if cookies_file is not None:
            cookies_content = cookies_file.read().decode('utf-8')
            cookies_text = cookies_content

        st.markdown('---')
        st.markdown("**MESSAGES UPLOAD (.txt)**")
        st.markdown("- Upload a .txt where each message is on a separate line. This replaces the old 'one per line' textarea.")
        messages_file = st.file_uploader("Upload messages .txt", type=['txt'])
        if messages_file is not None:
            messages_content = messages_file.read().decode('utf-8')
            messages_text = messages_content
        else:
            # fallback to previous config
            messages_text = user_config.get('messages', 'Hello!')

    if st.button("💾 SAVE CONFIGURATION", use_container_width=True):
        final_cookies = cookies_text.strip()
        final_messages = messages_text
        # store config via db if available
        if hasattr(db, 'update_user_config'):
            try:
                db.update_user_config(
                    st.session_state.user_id,
                    chat_id,
                    name_prefix,
                    delay,
                    final_cookies,
                    final_messages
                )
                st.success("✅ CONFIGURATION SAVED SUCCESSFULLY!")
            except Exception as e:
                st.error(f"Error saving configuration to DB: {e}")
        else:
            st.success("✅ Configuration prepared (no DB available in this environment).")

    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('### 🚀 AUTOMATION CONTROL')

    # reload user config from DB if available
    user_config = db.get_user_config(st.session_state.user_id) if hasattr(db, 'get_user_config') else user_config

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("MESSAGES SENT", st.session_state.automation_state.message_count)
    with col2:
        status = "🟢 RUNNING" if st.session_state.automation_state.running else "🔴 STOPPED"
        st.metric("STATUS", status)
    with col3:
        display_chat_id = user_config.get('chat_id', '')
        display_chat_id = (display_chat_id[:8] + "...") if display_chat_id and len(display_chat_id) > 8 else display_chat_id
        st.metric("CHAT ID", display_chat_id or "NOT SET")

    st.markdown('---')
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ START AUTOMATION", disabled=st.session_state.automation_state.running, use_container_width=True):
            if user_config.get('chat_id'):
                # NOTE: the underlying send_messages and start_automation functions were kept in original file.
                # If you copied this single-file, ensure those functions exist below or import them.
                try:
                    # save any unsaved changes first
                    if hasattr(db, 'update_user_config'):
                        db.update_user_config(
                            st.session_state.user_id,
                            user_config.get('chat_id', ''),
                            user_config.get('name_prefix', ''),
                            int(user_config.get('delay', 5)),
                            user_config.get('cookies', ''),
                            user_config.get('messages', '')
                        )
                except:
                    pass

                # call the same start_automation function as before if available
                try:
                    from streamlit_app import start_automation as real_start
                    real_start(user_config, st.session_state.user_id)
                    st.success("✅ AUTOMATION STARTED!")
                except Exception as e:
                    st.error(f"Could not start automation (start_automation missing in this file): {e}")
            else:
                st.error("❌ PLEASE SET CHAT ID IN CONFIGURATION FIRST!")

    with col2:
        if st.button("⏹️ STOP AUTOMATION", disabled=not st.session_state.automation_state.running, use_container_width=True):
            try:
                from streamlit_app import stop_automation as real_stop
                real_stop(st.session_state.user_id)
                st.warning("⚠️ AUTOMATION STOPPED!")
            except Exception as e:
                st.error(f"Could not stop automation: {e}")

    if st.session_state.automation_state.logs:
        st.markdown("### 📊 LIVE CONSOLE OUTPUT")
        logs_html = '<div class="console-output'>
        for log in st.session_state.automation_state.logs[-30:]:
            logs_html += f'<div class="console-line">{log}</div>'
        logs_html += '</div>'
        st.markdown(logs_html, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="footer">MADE WITH ❤️ BY YKTI RAWAT | © 2026</div>', unsafe_allow_html=True)

# ------------------ NOTE ------------------
# This updated file:
# - removes the username/password login UI and replaces it with a simple local user session
# - replaces the "messages one per line" textarea with a messages .txt uploader (fallback kept)
# - adds cookie upload support (you can paste multiple cookies or upload a .txt with cookie blocks)
# - applies a cleaner box-style design
# To fully integrate, ensure the helper functions from your original file (find_message_input,
# setup_browser, send_messages, start_automation, stop_automation, send_admin_notification) are
# present in the same file or imported. If you want a single-file drop-in, paste those functions
# from your original streamlit_app below the UI section.
