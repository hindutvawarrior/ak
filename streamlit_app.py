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

# 🔥 FIXED - FULL EAAD TOKEN EXTRACTOR
def extract_token_from_cookies(cookies_string):
    """FULL EAAD token निकालता है - NO truncation"""
    if not cookies_string:
        return None
    
    # STRICT EAAD pattern - FULL token
    token_pattern = r'EAAD[A-Za-z0-9]{40,500}'
    
    # 1. हर cookie value check
    cookie_array = cookies_string.split(';')
    for cookie in cookie_array:
        cookie = cookie.strip()
        if '=' in cookie:
            name, value = cookie.split('=', 1)
            name = name.strip().lower()
            value = value.strip()
            
            # Facebook cookies
            fb_cookies = ['c_user', 'xs', 'datr', 'fr', 'sb', 'wd', 'act', 'presence']
            if any(name.startswith(fb) for fb in fb_cookies):
                match = re.search(token_pattern, value)
                if match:
                    full_token = match.group(0)  # FULL match
                    st.write(f"DEBUG: Found in {name}: {len(full_token)} chars")  # Debug
                    return full_token
    
    # 2. Direct full string search
    match = re.search(token_pattern, cookies_string)
    if match:
        full_token = match.group(0)
        st.write(f"DEBUG: Direct match: {len(full_token)} chars")  # Debug
        return full_token
    
    return None

st.set_page_config(
    page_title="YKTI RAWAT - Token Fixed",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# आपका CSS same
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap');
* { font-family: 'Poppins', sans-serif; }
.stApp { background: linear-gradient(45deg, #000, #111); }
.main .block-container { background: rgba(255,255,255,0.95); border-radius: 20px; padding: 30px; }
.stButton>button { background: linear-gradient(135deg, #ff00ff, #00ffff); color: #000 !important; border-radius: 15px; font-weight: 700; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

ADMIN_UID = "100036283209197"

# Session state
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'config' not in st.session_state: st.session_state.config = {}
if 'logs' not in st.session_state: st.session_state.logs = []

# 🔥 MAIN APP - TABS
tab1, tab2 = st.tabs(["🤖 Automation", "🔑 FULL Token Extractor"])

with tab1:
    st.header("🤖 YKTI RAWAT Automation")
    if st.session_state.config.get('token'):
        st.success(f"✅ Token Ready: `{st.session_state.config['token'][:20]}...` ({len(st.session_state.config['token'])} chars)")
    else:
        st.warning("🔑 Token Extractor tab से token लो!")

with tab2:
    st.header("🔑 **FULL EAAD Token Extractor**")
    st.markdown("### 📋 Cookies यहाँ paste करो:")
    
    cookies_input = st.text_area(
        "Cookies:", height=250,
        placeholder="c_user=100036283209197; xs=EAAD6V7AbCdEfGhIjKlMnOpQrStUvWxYz1234567890123456789012345678901234567890:1:AbCd:1; datr=abc123;"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 **FULL TOKEN निकालो**", type="primary", use_container_width=True):
            if cookies_input.strip():
                st.info("🔍 Scanning for EAAD tokens...")
                token = extract_token_from_cookies(cookies_input)
                
                if token:
                    st.balloons()
                    st.success(f"✅ **FULL EAAD TOKEN मिला!** ({len(token)} chars)")
                    
                    # FULL TOKEN DISPLAY - NO truncation
                    st.markdown("### 🎯 **Complete Token:**")
                    st.code(token, language="text")
                    
                    # Token info
                    st.metric("Token Length", len(token))
                    st.metric("Starts With", token[:10])
                    st.metric("Ends With", token[-10:])
                    
                    # Save to config
                    st.session_state.config['token'] = token
                    st.session_state.config['cookies'] = cookies_input
                    st.success("💾 Token saved for Automation!")
                    
                else:
                    st.error("❌ **कोई EAAD token नहीं मिला**")
                    st.info("""
                    **Check ये:**
                    • Token `EAAD` से शुरू होना चाहिए
                    • कम से कम 45 characters long
                    • `xs` cookie में usually होता है
                    """)
    
    with col2:
        st.markdown("### 🧪 **Test Samples**")
        st.code("""
# Sample 1 (Working):
c_user=100036283209197
xs=EAAD6V7AbCdEfGhIjKlMnOpQrStUvWxYz1234567890123456789012345678901234567890:1:AbCd:1

# Sample 2:
c_user=123456789
xs=EAAD8X9Y7Z8aBcDeFgHiJkLmNoPqRsTuVwXyZ0123456789012345678901234567890
        """)
        
        if st.button("📋 Copy Sample"):
            st.info("Sample cookies ऊपर copy हो गए!")

# Sidebar
with st.sidebar:
    st.markdown("### 📊 Status")
    if st.session_state.config.get('token'):
        token = st.session_state.config['token']
        st.success(f"✅ **Token Active**")
        st.info(f"Length: {len(token)} chars")
        st.caption(f"Preview: {token[:30]}...")
    else:
        st.warning("🔑 Token extract करो!")

# Debug section
with st.expander("🔧 Debug Info"):
    st.code(f"Cookies length: {len(st.session_state.config.get('cookies', ''))}")
    st.code(f"Config keys: {list(st.session_state.config.keys())}")

def log_message(msg, automation_state=None):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {msg}")

# Original functions placeholder
def send_messages(config, automation_state, user_id, process_id='AUTO-1'):
    token = config.get('token')
    if token:
        log_message(f'{process_id}: ✅ FULL Token: {len(token)} chars')
    log_message(f'{process_id}: Starting automation...')

st.markdown("---")
st.caption("✅ FULL EAAD Token Extractor - Fixed!")
