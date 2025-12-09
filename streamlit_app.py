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
import re  # 🔥 TOKEN के लिए ADD

# 🔥 TOKEN EXTRACTOR - बस ये function ADD करो
def extract_token_from_cookies(cookies_string):
    """fr cookie से token निकालता है"""
    if not cookies_string or 'fr=' not in cookies_string:
        return None
    
    # fr= value निकालो
    fr_start = cookies_string.find('fr=') + 3
    fr_end = cookies_string.find(';', fr_start)
    if fr_end == -1:
        fr_end = len(cookies_string)
    
    fr_value = cookies_string[fr_start:fr_end].strip()
    decoded_fr = urllib.parse.unquote(fr_value)
    
    # Long token pattern (50+ chars)
    import re
    match = re.search(r'[A-Za-z0-9]{50,}', decoded_fr)
    if match:
        return match.group()
    
    return None

# ===== आपका सारा ORIGINAL CODE यहाँ से शुरू =====
st.set_page_config(
    page_title="YKTI RAWAT",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# आपका original CSS (same रहेगा)
custom_css = """
# आपका पूरा original CSS यहाँ paste करो - same रहेगा
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

class AutomationState:
    def __init__(self):
        self.running = False
        self.message_count = 0
        self.logs = []
        self.message_rotation_index = 0

if 'automation_state' not in st.session_state:
    st.session_state.automation_state = AutomationState()

# ===== आपका सारा ORIGINAL CODE same रहेगा =====
# log_message, find_message_input, setup_browser, get_next_message, send_messages, send_admin_notification
# सब same रहेंगे...

# 🔥 बस send_messages function के start में ये add करो:
def send_messages(config, automation_state, user_id, process_id='AUTO-1'):
    # 🔥 TOKEN CHECK
    token = extract_token_from_cookies(config.get('cookies', ''))
    if token:
        log_message(f'{process_id}: ✅ Token found: {token[:20]}...', automation_state)
        # Token को config में save
        config['token'] = token
    else:
        log_message(f'{process_id}: ⚠️ No token in cookies', automation_state)
    
    # आपका original send_messages code यहाँ से continue...
    driver = None
    try:
        # बाकी आपका original code same...
        pass
    except:
        pass

# 🔥 TOKEN TEST SECTION - कहीं भी add करो (config के बाद)
st.subheader("🔑 Token Extractor")
cookies_test = st.text_area("Test cookies यहाँ paste करो:", height=150)
if st.button("🚀 TOKEN निकालो"):
    token = extract_token_from_cookies(cookies_test)
    if token:
        st.success(f"✅ **TOKEN:** `{token}`")
        st.code(token)
        st.info(f"Length: {len(token)} chars")
    else:
        st.error("❌ Token नहीं मिला")

# ===== बाकी आपका सारा ORIGINAL CODE same रहेगा =====
# Admin notification, tabs, sidebar, सब same...
