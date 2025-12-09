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
import re  # ← TOKEN के लिए ADD
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import database as db
import requests

# ===== TOKEN EXTRACTOR FUNCTION (नया ADD) =====
def extract_token_from_cookies(cookies_string):
    """Cookie string से EAAD token निकालता है"""
    if not cookies_string:
        return None
    
    # EAAD pattern
    token_pattern = r'EAAD[A-Za-z0-9]{7,}'
    
    # सभी cookies parse
    cookie_array = cookies_string.split(';')
    
    for cookie in cookie_array:
        cookie = cookie.strip()
        if '=' in cookie:
            name, value = cookie.split('=', 1)
            name = name.strip().lower()
            
            # FB token cookies
            token_names = ['c_user', 'xs', 'datr', 'fr', 'sb', 'wd', 'act', 'presence']
            if any(token_name in name for token_name in token_names):
                matches = re.findall(token_pattern, value)
                if matches:
                    return matches[0]
    
    # Direct search
    direct_matches = re.findall(token_pattern, cookies_string)
    if direct_matches:
        return direct_matches[0]
    
    return None
# ===== TOKEN FUNCTION END =====

st.set_page_config(
    page_title="YKTI RAWAT",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# बाकी आपका सारा original CSS और code same रहेगा...
custom_css = """
# [आपका पूरा original CSS यहाँ same रहेगा - copy नही कर रहा space बचाने के लिए]
"""

# बाकी सारा code same...
ADMIN_UID = "100036283209197"

# [सारे session_state और class same...]

# ===== MAIN CHANGES: CONFIG FORM में TOKEN SECTION ADD =====
# आपके config form के cookies field के बाद ये add करो:

# Example config section में (जहाँ cookies input है):
st.subheader("🔑 **Token Extraction**")
cookies = st.session_state.get('config', {}).get('cookies', '')

if cookies:
    token = extract_token_from_cookies(cookies)
    if token:
        st.success(f"✅ **TOKEN FOUND:** `{token[:30]}...`")
        st.info(f"**Full Token Length:** {len(token)} chars")
        st.code(token)
        st.session_state.config['token'] = token  # Save token
    else:
        st.warning("⚠️ No EAAD token found in cookies")
        
    if st.button("🔍 Extract Token Again"):
        st.rerun()
else:
    st.info("👆 पहले Cookies paste करो!")

# Test button (sidebar में add कर सकते हो)
with st.sidebar:
    st.markdown("### 🧪 Token Test")
    test_cookies = st.text_area("Test Cookies", height=100)
    if st.button("Test Token"):
        test_token = extract_token_from_cookies(test_cookies)
        if test_token:
            st.success(f"✅ Test Token: `{test_token[:30]}...`")
        else:
            st.error("❌ No token")

# बाकी सारा original code same रहेगा...
# send_messages function में भी use कर सकते हो:
def send_messages(config, automation_state, user_id, process_id='AUTO-1'):
    # पहले token check
    token = config.get('token') or extract_token_from_cookies(config.get('cookies', ''))
    if token:
        log_message(f'{process_id}: ✅ Token ready: {token[:10]}...', automation_state)
    
    # बाकी original code same...
