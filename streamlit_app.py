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
import re  # 🔥 TOKEN के लिए

# 🔥 FIXED TOKEN EXTRACTOR FUNCTION
def extract_token_from_cookies(cookies_string):
    """ALL Facebook tokens detect करता है - 100% FIXED"""
    if not cookies_string:
        return None
    
    patterns = [
        r'EAAD[A-Za-z0-9]{30,}',  # Main EAAD
        r'EAA[A-Za-z0-9]{30,}',   # EAA tokens
        r'EAB[A-Za-z0-9]{30,}',   # EAB tokens
        r'EA[A-Za-z0-9]{30,}',    # All EA
        r'[A-Za-z0-9_-]{50,}'     # Long tokens backup
    ]
    
    # हर cookie check
    for cookie in cookies_string.split(';'):
        cookie = cookie.strip()
        if '=' in cookie:
            name, value = cookie.split('=', 1)
            name = name.strip().lower()
            
            # FB cookies
            fb_names = ['c_user', 'xs', 'datr', 'fr', 'sb', 'wd', 'act', 'presence']
            if any(name.startswith(fb) for fb in fb_names):
                for pattern in patterns:
                    match = re.search(pattern, value)
                    if match:
                        return match.group()
    
    # Direct full string search
    for pattern in patterns:
        match = re.search(pattern, cookies_string)
        if match:
            return match.group()
    
    return None

st.set_page_config(
    page_title="YKTI RAWAT",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# आपका original CSS (same)
custom_css = """
<style>
# [आपका पूरा CSS यहाँ paste करो - same रहेगा]
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# आपका original ADMIN_UID और session_state (same)
ADMIN_UID = "100036283209197"

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
# [बाकी session_state same...]

# 🔥 TOKEN SECTION - MAIN UI में ADD
tab1, tab2 = st.tabs(["🤖 Automation", "🔑 Token Extractor"])

with tab1:
    # आपका original automation code यहाँ same रहेगा
    st.header("🤖 YKTI RAWAT Automation")
    # [सारा original code same...]

with tab2:
    st.header("🔑 **Facebook Token Extractor**")
    st.markdown("---")
    
    # Cookies input
    cookies_input = st.text_area(
        "📋 **Cookies paste करो:**", 
        height=200,
        placeholder="c_user=100036283209197; xs=EAAD6V7xyz...; datr=abc123;"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 **TOKEN निकालो**", type="primary"):
            if cookies_input:
                with st.spinner("🔍 Scanning cookies..."):
                    token = extract_token_from_cookies(cookies_input)
                    
                    if token:
                        st.balloons()
                        st.success(f"✅ **TOKEN READY!**")
                        
                        # Token display
                        st.markdown(f"""
                        ### 🎯 **Your Token:**
                        ```
{token}
                        ```
                        **Length:** {len(token)} chars
                        """)
                        
                        # Copy + Save
                        st.code(token)
                        
                        # Session में save
                        if 'config' not in st.session_state:
                            st.session_state.config = {}
                        st.session_state.config['token'] = token
                        st.session_state.config['cookies'] = cookies_input
                        
                        st.success("💾 Token saved in config!")
                        
                    else:
                        st.error("❌ **No token found!**")
                        st.info("""
                        💡 **Tips:**
                        • F12 → Application → Cookies → Copy ALL
                        • EAAD/EAA से start होना चाहिए
                        • 50+ chars long होना चाहिए
                        """)
            else:
                st.warning("👆 Cookies paste करो!")
    
    with col2:
        st.markdown("### 📋 **Cookie Copy Guide**")
        st.info("""
        1. Facebook.com खोलो (logged in)
        2. **F12** दबाओ
        3. **Application** tab
        4. Left → **Cookies** → **https://facebook.com**
        5. **Ctrl+A** → **Ctrl+C**
        6. यहाँ paste!
        """)
        
        if st.button("🧪 Test Sample"):
            st.code("c_user=1000; xs=EAAD6V7testtoken1234567890abcdefghijklmnopqrstuvwxyz; datr=test")
            st.success("ये sample try करो!")

# आपका original functions (same) - बस send_messages में token log add
def send_messages(config, automation_state, user_id, process_id='AUTO-1'):
    # 🔥 TOKEN CHECK
    token = config.get('token') or extract_token_from_cookies(config.get('cookies', ''))
    if token:
        log_message(f'{process_id}: ✅ Token: {token[:15]}...', automation_state)
    else:
        log_message(f'{process_id}: ⚠️ No token found', automation_state)
    
    # बाकी original code same...
    driver = None
    try:
        # [आपका original send_messages code same...]
        pass
    except:
        pass

# बाकी सारे original functions same रहेंगे...
