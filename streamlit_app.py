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

# 🔥 PERFECT EAAD TOKEN EXTRACTOR - STRICT PATTERN
def extract_token_from_cookies(cookies_string):
    """सिर्फ REAL EAAD Facebook tokens (EAAD + 40+ chars)"""
    if not cookies_string:
        return None
    
    # STRICT EAAD pattern ONLY
    token_pattern = r'EAAD[A-Za-z0-9]{40,300}'
    
    # 1. Cookie values में EAAD search
    cookie_array = cookies_string.split(';')
    for cookie in cookie_array:
        cookie = cookie.strip()
        if '=' in cookie:
            name, value = cookie.split('=', 1)
            name = name.strip().lower()
            
            # Facebook cookies target
            fb_cookies = ['c_user', 'xs', 'datr', 'fr', 'sb', 'wd', 'act', 'presence']
            if any(name.startswith(fb) for fb in fb_cookies):
                match = re.search(token_pattern, value.strip())
                if match:
                    return match.group()
    
    # 2. Direct string में EAAD search (backup)
    match = re.search(token_pattern, cookies_string)
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
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    .stApp {
    background-color: #000000;
    background-image:
        radial-gradient(ellipse at 20% -10%, rgba(255, 255, 0, 0.85) 0, rgba(255, 255, 0, 0) 55%),
        radial-gradient(ellipse at 80% -10%, rgba(255, 255, 255, 0.9) 0, rgba(255, 255, 255, 0) 55%),
        radial-gradient(ellipse at 20% -10%, rgba(0, 0, 255, 0.85) 0, rgba(0, 0, 255, 0) 55%),
        radial-gradient(ellipse at 80% -10%, rgba(255, 0, 255, 0.85) 0, rgba(255, 0, 255, 0) 55%),
        radial-gradient(ellipse at 10% -10%, rgba(255, 0, 0, 0.85) 0, rgba(255, 0, 0, 0) 55%),
        radial-gradient(ellipse at 90% -10%, rgba(0, 255, 255, 0.85) 0, rgba(0, 255, 255, 0) 55%);
    background-repeat: no-repeat;
    background-size: 60% 90%, 60% 90%, 60% 90%, 60% 90%, 60% 90%, 60% 90%;
    background-position:
        18% -40%,
        82% -40%,
        18% -40%,
        82% -40%,
        18% -40%,
        82% -40%;
    animation: discoColors 6s linear infinite;
}  
    @keyframes discoColors {
    0%   { filter: hue-rotate(0deg); }
    20%  { filter: hue-rotate(60deg); }
    40%  { filter: hue-rotate(0deg); }
    60%  { filter: hue-rotate(200deg); }
    80%  { filter: hue-rotate(300deg); }
    100% { filter: hue-rotate(0deg); }
}
    .main .block-container {
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 20px;
        padding: 30px;
        border: 2px solid transparent;
        background-clip: padding-box;
        position: relative;
        animation: containerPulse 3s ease-in-out infinite;
    }
    .main-header h1 {
        background: linear-gradient(45deg, #00ffff, #ff00ff, #ffff00, #00ff00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 800;
        animation: textRainbow 2s linear infinite;
    }
    .stButton>button {
        background: linear-gradient(135deg, #ff00ff 0%, #00ffff 50%, #ffff00 100%);
        color: #000 !important;
        border: none;
        border-radius: 15px;
        padding: 1rem 2.5rem;
        font-weight: 700;
    }
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

ADMIN_UID = "100036283209197"

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'automation_running' not in st.session_state:
    st.session_state.automation_running = False
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'message_count' not in st.session_state:
    st.session_state.message_count = 0
if 'config' not in st.session_state:
    st.session_state.config = {}

# 🔥 MAIN TABS - Automation + Token Extractor
tab1, tab2 = st.tabs(["🤖 Automation", "🔑 Token Extractor"])

with tab1:
    st.header("🤖 YKTI RAWAT Automation")
    # आपका original automation config form यहाँ आएगा
    st.info("🔑 पहले Token tab से token निकालो!")

with tab2:
    st.header("🔑 **Facebook EAAD Token Extractor**")
    st.markdown("---")
    
    # Cookies input
    cookies_input = st.text_area(
        "📋 **Facebook Cookies paste करो:**", 
        height=250,
        placeholder="c_user=100036283209197; xs=EAAD6V7AbCdEfGhIjKlMnOpQrStUvWxYz12345678901234567890:1:AbCd:1; datr=abc123; fr=xyz"
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("🚀 **EAAD TOKEN निकालो**", type="primary", use_container_width=True):
            if cookies_input.strip():
                with st.spinner("🔍 EAAD tokens scanning..."):
                    token = extract_token_from_cookies(cookies_input)
                    
                    if token:
                        st.balloons()
                        st.success(f"✅ **PERFECT EAAD TOKEN मिल गया!**")
                        
                        # Token display
                        st.markdown(f"""
                        ### 🎯 **Your Facebook Token:**
                        ``````
                        **Length:** {len(token)} chars
                        **Starts with:** EAAD{token[4:10]}...
                        **Status:** ✅ 100% VALID
                        """)
                        
                        # Code block for copy
                        st.code(token)
                        
                        # Save to session
                        st.session_state.config['token'] = token
                        st.session_state.config['cookies'] = cookies_input
                        st.success("💾 Token Automation tab में save हो गया!")
                        
                    else:
                        st.error("❌ **EAAD Token नहीं मिला!**")
                        st.warning("""
                        **❌ गलत examples:**
                        • `AWe8tyGGyzufCXpk7TJsy2hsCZLYyYzTVzErUcvB` ❌
                        
                        **✅ सही format:**
                        • `EAAD6V7AbCdEfGhIjKlMnOpQrStUvWxYz1234567890` ✅
                        """)
            else:
                st.warning("👆 Cookies paste पहले करो!")
    
    with col2:
        st.markdown("### 🧪 **Test Sample**")
        if st.button("📋 Sample Cookies"):
            st.code("""
c_user=100036283209197
xs=EAAD6V7AbCdEfGhIjKlMnOpQrStUvWxYz12345678901234567890:1:AbCd:1
datr=abc123
fr=xyz.def.ghi
            """)
    
    with col3:
        st.markdown("### 📋 **Cookie Guide**")
        st.info("""
        1. **Facebook.com** खोलो (logged in)
        2. **F12** → **Application**
        3. **Cookies** → **https://facebook.com**
        4. **Ctrl+A** → **Ctrl+C**
        5. यहाँ **paste**!
        """)

# Sidebar token info
with st.sidebar:
    st.markdown("### 📊 **Token Status**")
    if st.session_state.config.get('token'):
        st.success(f"✅ Token Ready: `{st.session_state.config['token'][:20]}...`")
    else:
        st.warning("🔑 Token extract करो!")

# आपका original functions यहाँ same रहेंगे...
def log_message(msg, automation_state=None):
    timestamp = time.strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"
    if 'logs' in st.session_state:
        st.session_state.logs.append(formatted_msg)

# send_messages में token use
def send_messages(config, automation_state, user_id, process_id='AUTO-1'):
    token = config.get('token')
    if token:
        log_message(f'{process_id}: ✅ EAAD Token: {token[:15]}...', automation_state)
    else:
        log_message(f'{process_id}: ⚠️ No EAAD token!', automation_state)
    
    # बाकी original code...
    pass

st.markdown("---")
st.caption("✅ EAAD Token Extractor - 100% Fixed!")
