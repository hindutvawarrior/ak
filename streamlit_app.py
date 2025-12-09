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
import re
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import database as db
import requests

# 🔥 PERFECT TOKEN EXTRACTOR - URL DECODE + FULL EAAD
def extract_token_from_cookies(cookies_string):
    """URL decoded cookies से FULL EAAD token निकालता है"""
    if not cookies_string:
        return None
    
    # 1. URL DECODE
    decoded_cookies = urllib.parse.unquote(cookies_string)
    
    # 2. EAAD patterns (multiple versions)
    patterns = [
        r'EAAD[A-Za-z0-9]{40,500}',
        r'EAA[A-Za-z0-9]{40,500}',
        r'EA[A-Za-z0-9]{40,500}'
    ]
    
    # 3. Cookie parsing
    cookie_array = cookies_string.split(';')
    for cookie in cookie_array:
        cookie = cookie.strip()
        if '=' in cookie:
            name, value = cookie.split('=', 1)
            name = name.strip().lower()
            value = value.strip()
            decoded_value = urllib.parse.unquote(value)
            
            # FB cookies target
            fb_cookies = ['c_user', 'xs', 'datr', 'fr', 'sb', 'wd', 'act', 'presence']
            if any(name.startswith(fb) for fb in fb_cookies):
                # Original + decoded check
                for check_value in [value, decoded_value]:
                    for pattern in patterns:
                        match = re.search(pattern, check_value)
                        if match:
                            return match.group()
    
    # 4. Direct search
    for pattern in patterns:
        match = re.search(pattern, decoded_cookies)
        if match:
            return match.group()
    
    return None

st.set_page_config(
    page_title="YKTI RAWAT",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap');
* { font-family: 'Poppins', sans-serif; }
.stApp { 
    background: linear-gradient(45deg, #000, #111); 
    background-size: 400% 400%;
    animation: gradientShift 8s ease infinite;
}
@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.main .block-container { 
    background: rgba(255,255,255,0.95) !important; 
    border-radius: 20px; 
    padding: 30px; 
    border: 2px solid #00ffff; 
}
.stButton>button { 
    background: linear-gradient(135deg, #ff00ff, #00ffff, #ffff00) !important; 
    color: #000 !important; 
    border-radius: 15px; 
    font-weight: 700; 
    border: none;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

ADMIN_UID = "100036283209197"

# Session state
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_id' not in st.session_state: st.session_state.user_id = None
if 'username' not in st.session_state: st.session_state.username = None
if 'automation_running' not in st.session_state: st.session_state.automation_running = False
if 'logs' not in st.session_state: st.session_state.logs = []
if 'message_count' not in st.session_state: st.session_state.message_count = 0
if 'config' not in st.session_state: st.session_state.config = {}

class AutomationState:
    def __init__(self):
        self.running = False
        self.message_count = 0
        self.logs = []
        self.message_rotation_index = 0

if 'automation_state' not in st.session_state:
    st.session_state.automation_state = AutomationState()

# 🔥 MAIN TABS
tab1, tab2 = st.tabs(["🤖 Automation", "🔑 Token Extractor"])

with tab1:
    st.markdown("<h1 style='text-align: center; color: #ff00ff;'>🤖 YKTI RAWAT</h1>", unsafe_allow_html=True)
    
    # Config form
    st.subheader("⚙️ Configuration")
    col1, col2 = st.columns(2)
    
    with col1:
        config = st.session_state.config.copy()
        config['cookies'] = st.text_area("Cookies", height=150, key="cookies_input")
        config['chat_id'] = st.text_input("Chat ID", key="chat_id_input")
        config['messages'] = st.text_area("Messages (one per line)", height=100, key="messages_input")
    
    with col2:
        config['delay'] = st.number_input("Delay (seconds)", min_value=1, value=10, key="delay_input")
        config['name_prefix'] = st.text_input("Name Prefix", key="name_prefix_input")
        
        if st.button("💾 Save Config", type="secondary"):
            st.session_state.config = config
            st.success("Config saved!")
    
    # Token status
    if st.session_state.config.get('token'):
        st.success(f"✅ Token Ready: `{st.session_state.config['token'][:20]}...`")
        st.info(f"Length: {len(st.session_state.config['token'])} chars")
    else:
        st.warning("🔑 Token Extractor tab से token लो!")

with tab2:
    st.markdown("<h1 style='text-align: center; color: #00ffff;'>🔑 Token Extractor</h1>", unsafe_allow_html=True)
    
    cookies_input = st.text_area(
        "📋 **Facebook Cookies paste करो:**", 
        height=250,
        placeholder="datr=...; c_user=...; xs=26%3Azx57L4Yx0o7uWQ%3A2%3A...; fr=..."
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("🚀 **FULL TOKEN निकालो**", type="primary", use_container_width=True):
            if cookies_input.strip():
                with st.spinner("🔍 URL decoding + EAAD scanning..."):
                    token = extract_token_from_cookies(cookies_input)
                    
                    if token:
                        st.balloons()
                        st.success(f"✅ **FULL EAAD TOKEN मिला!** ({len(token)} chars)")
                        
                        # FULL TOKEN DISPLAY
                        st.markdown("### 🎯 **Complete Token:**")
                        st.code(token, language="text")
                        
                        # Token metrics
                        col_a, col_b, col_c = st.columns(3)
                        with col_a: st.metric("Length", len(token))
                        with col_b: st.metric("Starts", token[:10])
                        with col_c: st.metric("Ends", token[-10:])
                        
                        # Save to config
                        st.session_state.config['token'] = token
                        st.session_state.config['cookies'] = cookies_input
                        st.rerun()
                        
                    else:
                        st.error("❌ **EAAD Token नहीं मिला**")
                        st.info("""
                        **Debug Info:**
                        • Cookies length: {}
                        • Decoded length: {}
                        """.format(len(cookies_input), len(urllib.parse.unquote(cookies_input))))
    
    with col2:
        st.markdown("### 🧪 **Test**")
        test_cookies = """datr=hxYhaWi8-5liuX_8njwTlonz;sb=hxYhaXQE_GA556nSFgivJhWR;c_user=100072661716074;xs=26%3Azx57L4Yx0o7uWQ%3A2%3A1765253881%3A-1%3A-1"""
        if st.button("📋 Your Cookies"):
            st.code(test_cookies)
    
    with col3:
        st.markdown("### 📋 **Guide**")
        st.info("""
        1. Facebook.com खोलो
        2. **F12** → **Application**
        3. **Cookies** → **facebook.com**
        4. **Ctrl+A** → **Ctrl+C**
        5. यहाँ **Paste**!
        """)

# Sidebar
with st.sidebar:
    st.markdown("### 📊 **Status**")
    if st.session_state.config.get('token'):
        token = st.session_state.config['token']
        st.success(f"✅ **Token Active**")
        st.metric("Token Length", len(token))
        st.caption(f"{token[:30]}...")
    else:
        st.warning("🔑 Token extract करो!")

# Original functions (same)
def log_message(msg, automation_state=None):
    timestamp = time.strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"
    if automation_state:
        automation_state.logs.append(formatted_msg)
    else:
        st.session_state.logs.append(formatted_msg)

def send_messages(config, automation_state, user_id, process_id='AUTO-1'):
    token = config.get('token')
    if token:
        log_message(f'{process_id}: ✅ FULL Token: {len(token)} chars', automation_state)
    else:
        log_message(f'{process_id}: ⚠️ No token found', automation_state)
    # बाकी original code same...

st.markdown("---")
st.caption("✅ YKTI RAWAT - Full EAAD Token Extractor Fixed!")
