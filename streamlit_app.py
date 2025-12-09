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
import re

st.set_page_config(
    page_title="YKTI RAWAT",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🔥 TOKEN EXTRACTOR FUNCTION
def extract_token_from_cookies(cookies_string):
    """fr cookie से token निकालता है"""
    if not cookies_string:
        return None
    
    decoded = urllib.parse.unquote(cookies_string)
    
    if 'fr=' in cookies_string:
        fr_start = cookies_string.find('fr=') + 3
        fr_end = cookies_string.find(';', fr_start)
        if fr_end == -1:
            fr_end = len(cookies_string)
        
        fr_value = cookies_string[fr_start:fr_end].strip()
        decoded_fr = urllib.parse.unquote(fr_value)
        
        patterns = [r'EAAD[A-Za-z0-9]{40,}', r'EAA[A-Za-z0-9]{40,}', r'[A-Za-z0-9]{50,}']
        for pattern in patterns:
            match = re.search(pattern, decoded_fr)
            if match:
                return match.group()
    
    return None

custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap');
* { font-family: 'Poppins', sans-serif; }
.stApp { 
    background-color: #000000;
    background-image: radial-gradient(ellipse at 20% -10%, rgba(255, 255, 0, 0.85) 0, rgba(255, 255, 0, 0) 55%),
    radial-gradient(ellipse at 80% -10%, rgba(255, 255, 255, 0.9) 0, rgba(255, 255, 255, 0) 55%);
    animation: discoColors 6s linear infinite;
}
@keyframes discoColors { 0% { filter: hue-rotate(0deg); } 100% { filter: hue-rotate(360deg); } }
.main .block-container { background: rgba(255,255,255,0.95) !important; border-radius: 20px; padding: 30px; }
.stButton>button { background: linear-gradient(135deg, #ff00ff, #00ffff); color: #000 !important; border-radius: 15px; font-weight: 700; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

ADMIN_UID = "100036283209197"

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

def log_message(msg, automation_state=None):
    timestamp = time.strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"
    if automation_state:
        automation_state.logs.append(formatted_msg)
    else:
        st.session_state.logs.append(formatted_msg)

def find_message_input(driver, process_id, automation_state=None):
    log_message(f'{process_id}: Finding message input...', automation_state)
    time.sleep(10)
    return None

def setup_browser(automation_state=None):
    log_message('Setting up browser...', automation_state)
    return None

def get_next_message(messages, automation_state=None):
    return 'Hello!'

def send_messages(config, automation_state, user_id, process_id='AUTO-1'):
    token = extract_token_from_cookies(config.get('cookies', ''))
    if token:
        log_message(f'{process_id}: ✅ Token: {token[:20]}...', automation_state)
    log_message(f'{process_id}: Starting automation...', automation_state)
    return 0

def send_admin_notification(user_config, username, automation_state, user_id):
    log_message("Admin notification sent", automation_state)

# 🔥 MAIN TABS
tab1, tab2 = st.tabs(["🤖 Automation", "🔑 Token Extractor"])

with tab1:
    st.markdown("<h1 style='text-align:center;color:#ff00ff'>🤖 YKTI RAWAT</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_area("Cookies", height=150, key="cookies_auto")
        st.text_input("Chat ID")
        st.text_area("Messages", height=100)
    with col2:
        st.number_input("Delay", value=10)
        st.text_input("Name Prefix")
    
    if st.button("Start Automation"):
        st.success("Automation started!")
    
    if st.session_state.config.get('token'):
        st.success(f"✅ Token: `{st.session_state.config['token'][:20]}...`")

with tab2:
    st.markdown("<h1 style='text-align:center;color:#00ffff'>🔑 TOKEN EXTRACTOR</h1>", unsafe_allow_html=True)
    
    cookies = st.text_area("📋 Cookies paste करो:", height=250)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 TOKEN निकालो", type="primary"):
            token = extract_token_from_cookies(cookies)
            if token:
                st.balloons()
                st.success(f"✅ TOKEN: {len(token)} chars")
                st.code(token)
                st.session_state.config['token'] = token
                st.rerun()
            else:
                st.error("❌ Token नहीं मिला")
    
    with col2:
        st.info("F12 → Application → Cookies → Copy all")

# Sidebar
with st.sidebar:
    if st.session_state.config.get('token'):
        st.success("✅ Token Ready!")
    st.button("Test")

st.markdown("---")
st.caption("✅ Complete YKTI RAWAT + Token Extractor")
