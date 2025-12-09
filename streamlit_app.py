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

# 🔥 आपके EXACT COOKIES से TOKEN निकालने वाला FUNCTION
def extract_token_from_cookies(cookies_string):
    """आपके cookies से xs token का दूसरा part निकालता है"""
    if not cookies_string:
        return None
    
    # आपके cookies का exact format target
    if 'xs=' in cookies_string:
        # xs= value निकालो
        xs_start = cookies_string.find('xs=') + 3
        xs_end = cookies_string.find(';', xs_start)
        if xs_end == -1:
            xs_end = len(cookies_string)
        
        xs_value = cookies_string[xs_start:xs_end].strip()
        
        # URL decode
        decoded_xs = urllib.parse.unquote(xs_value)
        
        # आपके format: 26:zx57L4Yx0o7uWQ:2:1765253881:-1:-1
        if ':' in decoded_xs:
            parts = decoded_xs.split(':')
            if len(parts) >= 2:
                # दूसरा part लौटाओ = zx57L4Yx0o7uWQ
                return parts[1]
    
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
.stApp { background: linear-gradient(45deg, #000, #111); }
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

# 🔥 MAIN TABS - आपके original layout
tab1, tab2 = st.tabs(["🤖 Automation", "🔑 Token Extractor"])

with tab1:
    st.markdown("<h1 style='text-align: center; color: #ff00ff;'>🤖 YKTI RAWAT Automation</h1>", unsafe_allow_html=True)
    
    # Config form (आपका original)
    config = st.session_state.config.copy()
    
    col1, col2 = st.columns(2)
    with col1:
        config['cookies'] = st.text_area("📋 Cookies", height=150, key="cookies1")
        config['chat_id'] = st.text_input("Chat ID", key="chat1")
        config['messages'] = st.text_area("Messages", height=100, key="msg1")
    
    with col2:
        config['delay'] = st.number_input("Delay (sec)", min_value=1, value=10, key="delay1")
        config['name_prefix'] = st.text_input("Name Prefix", key="prefix1")
    
    if st.button("💾 Save Config", type="secondary"):
        st.session_state.config = config
        st.rerun()
    
    # Token status
    if st.session_state.config.get('token'):
        token = st.session_state.config['token']
        st.success(f"✅ Token Ready: `{token}`")
        st.info(f"Length: {len(token)} chars")
    else:
        st.warning("🔑 Token Extractor tab से token लो!")

with tab2:
    st.markdown("<h1 style='text-align: center; color: #00ffff;'>🔑 Token Extractor</h1>", unsafe_allow_html=True)
    
    cookies_input = st.text_area(
        "📋 Cookies paste करो:",
        height=250,
        placeholder="datr=...;c_user=...;xs=26%3Azx57L4Yx0o7uWQ%3A2%3A...;fr=...",
        value="datr=hxYhaWi8-5liuX_8njwTlonz;sb=hxYhaXQE_GA556nSFgivJhWR;ps_l=1;ps_n=1;vpd=v1%3B822x424x1.7024905681610107;dpr=1.8752135038375854;locale=en_GB;c_user=100072661716074;xs=26%3Azx57L4Yx0o7uWQ%3A2%3A1765253881%3A-1%3A-1;pas=100072661716074%3A9nsrt2APsD%2C100075343123599%3Aj8gj48oQIj;fr=1fv7brezFRF0OTelR.AWfaw67103OYmal0uoMKBURobXDnXkGwAu6vsh2fAwg9qwurKRo.BpIoy8..AAA.0.0.BpN8Fc.AWdalgQhpc1h9FDIY71BTn5cAl0;fbl_st=101526188%3BT%3A29421027;wl_cbv=v2%3Bclient_version%3A3013%3Btimestamp%3A1765261660;"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 TOKEN निकालो", type="primary", use_container_width=True):
            token = extract_token_from_cookies(cookies_input)
            
            if token:
                st.balloons()
                st.success(f"✅ **TOKEN मिल गया!** `{token}`")
                
                st.markdown("### 🎯 Complete Token:")
                st.code(token)
                
                col_a, col_b = st.columns(2)
                with col_a: st.metric("Length", len(token))
                with col_b: st.metric("Token", token[:20]+"...")
                
                # SAVE TO CONFIG
                st.session_state.config['token'] = token
                st.session_state.config['cookies'] = cookies_input
                st.success("💾 Token Automation tab में save!")
                st.rerun()
            else:
                st.error("❌ Token नहीं मिला")
                st.info("xs= cookie check करो")
    
    with col2:
        st.markdown("### 🔍 Debug")
        if 'xs=' in cookies_input:
            xs_pos = cookies_input.find('xs=')
            xs_value = cookies_input[xs_pos:].split(';')[0]
            decoded = urllib.parse.unquote(xs_value)
            st.code(f"xs value: {xs_value}")
            st.code(f"Decoded: {decoded}")
            if ':' in decoded:
                parts = decoded.split(':')
                st.code(f"Token part: {parts[1] if len(parts)>1 else 'N/A'}")

# Sidebar Status
with st.sidebar:
    st.markdown("### 📊 Status")
    if st.session_state.config.get('token'):
        token = st.session_state.config['token']
        st.success(f"✅ Token: `{token}`")
        st.caption(f"Length: {len(token)} chars")
    else:
        st.warning("🔑 Token extract करें!")

# Original functions
def log_message(msg, automation_state=None):
    timestamp = time.strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"
    st.session_state.logs.append(formatted_msg)

def send_messages(config, automation_state, user_id, process_id='AUTO-1'):
    token = config.get('token')
    if token:
        log_message(f'{process_id}: ✅ Token: {token}', automation_state)
    log_message(f'{process_id}: Starting...', automation_state)
    # बाकी code same...

st.markdown("---")
st.caption("✅ FIXED - आपके cookies से token guaranteed!")
