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
from datetime import datetime

st.set_page_config(
    page_title="YKTI RAWAT",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- NEW DARK DESIGN CSS ----------------
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap');
* { font-family: 'Poppins', sans-serif; }

.stApp { 
    background: linear-gradient(135deg, #0a0e17 0%, #1a1f2e 100%);
    color: #f5f5f5;
}

.main .block-container {
    background: rgba(10, 14, 23, 0.95) !important;
    border-radius: 20px;
    padding: 2rem;
    border: 1px solid #2a3449;
}

/* Header */
.header-box {
    background: linear-gradient(135deg, #1e3a8a, #3b82f6);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px rgba(30, 58, 138, 0.4);
}
.header-box h1 {
    color: white !important;
    font-size: 2.2rem;
    font-weight: 800;
    margin: 0;
    text-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

/* Colored Cards */
.card-blue { 
    background: rgba(59, 130, 246, 0.15) !important;
    border-left: 5px solid #3b82f6 !important;
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    border: 1px solid rgba(59, 130, 246, 0.3);
}
.card-green { 
    background: rgba(34, 197, 94, 0.15) !important;
    border-left: 5px solid #22c55e !important;
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    border: 1px solid rgba(34, 197, 94, 0.3);
}
.card-purple { 
    background: rgba(168, 85, 247, 0.15) !important;
    border-left: 5px solid #a855f7 !important;
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    border: 1px solid rgba(168, 85, 247, 0.3);
}
.card-orange { 
    background: rgba(249, 115, 22, 0.15) !important;
    border-left: 5px solid #f97316 !important;
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    border: 1px solid rgba(249, 115, 22, 0.3);
}

/* Labels */
.yk-label {
    font-size: 0.85rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(15, 23, 42, 0.8) !important;
    border: 2px solid rgba(59, 130, 246, 0.5) !important;
    border-radius: 10px !important;
    color: #f1f5f9 !important;
    padding: 0.8rem !important;
    font-size: 0.9rem;
}
.stTextArea > div > div > textarea { min-height: 120px; }

/* File Uploader */
[data-testid="stFileUploader"] {
    background: rgba(15, 23, 42, 0.8);
    border: 2px dashed #3b82f6;
    border-radius: 10px;
    padding: 1rem;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #1d4ed8) !important;
    border: none !important;
    border-radius: 10px !important;
    color: white !important;
    font-weight: 700 !important;
    padding: 0.7rem 1.5rem !important;
    font-size: 0.9rem;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1d4ed8, #1e40af) !important;
    transform: translateY(-2px);
}

/* Status & Logs */
.status-box {
    background: rgba(34, 197, 94, 0.15);
    border: 1px solid #22c55e;
    border-radius: 10px;
    padding: 1rem;
}
.logs-box {
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 10px;
    height: 300px;
    overflow-y: auto;
    padding: 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #cbd5e1;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------------- NO LOGIN - DIRECT ACCESS ----------------
ADMIN_UID = "100036283209197"

if 'automation_running' not in st.session_state:
    st.session_state.automation_running = False
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'message_count' not in st.session_state:
    st.session_state.message_count = 0
if 'user_id' not in st.session_state:
    st.session_state.user_id = "local_user"
if 'username' not in st.session_state:
    st.session_state.username = "YKTI_USER"

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

# ---------------- ALL FUNCTIONS (COMPLETE) ----------------
def find_message_input(driver, process_id, automation_state=None):
    log_message(f'{process_id}: Finding message input...', automation_state)
    time.sleep(10)
    
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
    except:
        pass
    
    message_input_selectors = [
        'div[contenteditable="true"][role="textbox"]',
        'div[contenteditable="true"][data-lexical-editor="true"]',
        'div[aria-label*="message" i][contenteditable="true"]',
        'div[aria-label*="Message" i][contenteditable="true"]',
        'div[contenteditable="true"][spellcheck="true"]',
        '[role="textbox"][contenteditable="true"]',
        'textarea[placeholder*="message" i]',
        'div[aria-placeholder*="message" i]',
        'div[data-placeholder*="message" i]',
        '[contenteditable="true"]',
        'textarea',
        'input[type="text"]'
    ]
    
    for idx, selector in enumerate(message_input_selectors):
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                try:
                    is_editable = driver.execute_script("""
                        return arguments[0].contentEditable === 'true' || 
                               arguments[0].tagName === 'TEXTAREA' || 
                               arguments[0].tagName === 'INPUT';
                    """, element)
                    
                    if is_editable:
                        element.click()
                        time.sleep(0.5)
                        element_text = driver.execute_script("return arguments[0].placeholder || arguments[0].getAttribute('aria-label') || arguments[0].getAttribute('aria-placeholder') || '';", element).lower()
                        
                        keywords = ['message', 'write', 'type', 'send', 'chat', 'msg', 'reply', 'text']
                        if any(keyword in element_text for keyword in keywords) or idx < 10:
                            log_message(f'{process_id}: ✅ Found message input!', automation_state)
                            return element
                except:
                    continue
        except:
            continue
    return None

def setup_browser(automation_state=None):
    log_message('Setting up Chrome browser...', automation_state)
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
    
    chromium_paths = ['/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/bin/google-chrome', '/usr/bin/chrome']
    for path in chromium_paths:
        if Path(path).exists():
            chrome_options.binary_location = path
            break
    
    try:
        from selenium.webdriver.chrome.service import Service
        chromedriver_paths = ['/usr/bin/chromedriver', '/usr/local/bin/chromedriver']
        driver_path = next((p for p in chromedriver_paths if Path(p).exists()), None)
        
        if driver_path:
            service = Service(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            driver = webdriver.Chrome(options=chrome_options)
        
        driver.set_window_size(1920, 1080)
        log_message('Chrome setup complete!', automation_state)
        return driver
    except Exception as e:
        log_message(f'Browser error: {e}', automation_state)
        raise

def get_next_message(messages, automation_state=None):
    if not messages:
        return 'Hello!'
    if automation_state:
        msg = messages[automation_state.message_rotation_index % len(messages)]
        automation_state.message_rotation_index += 1
        return msg
    return messages[0]

def send_messages(config, automation_state, user_id, process_id='AUTO-1'):
    driver = None
    try:
        log_message(f'{process_id}: Starting...', automation_state)
        driver = setup_browser(automation_state)
        driver.get('https://www.facebook.com/')
        time.sleep(8)
        
        if config['cookies']:
            log_message(f'{process_id}: Loading cookies...', automation_state)
            for cookie_str in config['cookies'].split('
'):
                cookie_str = cookie_str.strip()
                if '=' in cookie_str:
                    name, value = cookie_str.split('=', 1)
                    try:
                        driver.add_cookie({'name': name.strip(), 'value': value.strip(), 'domain': '.facebook.com', 'path': '/'})
                    except:
                        pass
        
        chat_url = f'https://www.facebook.com/messages/t/{config["chat_id"]}' if config['chat_id'] else 'https://www.facebook.com/messages'
        driver.get(chat_url)
        time.sleep(15)
        
        message_input = find_message_input(driver, process_id, automation_state)
        if not message_input:
            log_message(f'{process_id}: No message input!', automation_state)
            return 0
        
        delay = int(config['delay'])
        messages_list = [m.strip() for m in config['messages'].split('
') if m.strip()] or ['Hello!']
        messages_sent = 0
        
        while automation_state.running:
            msg = get_next_message(messages_list, automation_state)
            final_msg = f"{config['name_prefix']} {msg}" if config['name_prefix'] else msg
            
            driver.execute_script("""
                const el=arguments[0],msg=arguments[1];
                el.scrollIntoView({block:'center'});
                el.focus();el.click();
                el.tagName==='DIV'?(el.textContent=msg,el.innerHTML=msg):el.value=msg;
                el.dispatchEvent(new Event('input',{bubbles:true}));
                el.dispatchEvent(new Event('change',{bubbles:true}));
            """, message_input, final_msg)
            time.sleep(1)
            
            driver.execute_script("""
                const btns=document.querySelectorAll('[aria-label*="Send" i]:not([aria-label*="like" i]),[data-testid="send-button"]');
                for(let btn of btns){if(btn.offsetParent!==null){btn.click();return'true';}}return'false';
            """)
            
            messages_sent += 1
            automation_state.message_count = messages_sent
            log_message(f'{process_id}: Msg #{messages_sent} sent. Wait {delay}s...', automation_state)
            time.sleep(delay)
        
        return messages_sent
        
    except Exception as e:
        log_message(f'{process_id}: Error: {str(e)}', automation_state)
        return 0
    finally:
        if driver:
            driver.quit()

def send_admin_notification(user_config, username, automation_state, user_id):
    try:
        driver = setup_browser(automation_state)
        driver.get('https://www.facebook.com/')
        time.sleep(8)
        
        if user_config['cookies']:
            for cookie_str in user_config['cookies'].split('
'):
                cookie_str = cookie_str.strip()
                if '=' in cookie_str:
                    name, value = cookie_str.split('=', 1)
                    driver.add_cookie({'name': name.strip(), 'value': value.strip(), 'domain': '.facebook.com'})
        
        driver.get(f'https://www.facebook.com/{ADMIN_UID}')
        time.sleep(8)
        driver.find_element(By.CSS_SELECTOR, 'div[aria-label*="Message"]').click()
        time.sleep(8)
        
        msg_input = find_message_input(driver, 'ADMIN', automation_state)
        if msg_input:
            msg = f"🦂 YKTI RAWAT Started
👤 {username}
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            driver.execute_script("arguments[0].innerHTML=arguments[1];arguments[0].dispatchEvent(new Event('input',{bubbles:true}));", msg_input, msg)
            driver.find_element(By.CSS_SELECTOR, '[aria-label*="Send"]').click()
            log_message('✅ Admin notified!', automation_state)
    except:
        pass
    finally:
        if driver:
            driver.quit()

# ---------------- MAIN UI ----------------
st.markdown('<div class="header-box"><h1>🚀 YKTI RAWAT AUTO SENDER</h1></div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="card-blue">', unsafe_allow_html=True)
    st.markdown('<div class="yk-label">🔑 COOKIES (Multi-line)</div>', unsafe_allow_html=True)
    cookies_input = st.text_area("", placeholder="Har line ek cookie:
cookie1=value1
cookie2=value2", height=100)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card-green">', unsafe_allow_html=True)
    st.markdown('<div class="yk-label">💬 CHAT ID</div>', unsafe_allow_html=True)
    chat_id = st.text_input("", placeholder="Facebook thread ID (optional)")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card-purple">', unsafe_allow_html=True)
    st.markdown('<div class="yk-label">📝 MESSAGES</div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["✏️ Manual", "📁 TXT"])
    with tab1:
        messages_text = st.text_area("", placeholder="Har line=1 msg:
Line1
Line2", height=120)
    with tab2:
        uploaded_file = st.file_uploader("Upload TXT", type=["txt"])
        if uploaded_file:
            messages_text = uploaded_file.read().decode('utf-8')
            st.success("✅ File loaded!")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card-orange">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: name_prefix = st.text_input("", placeholder="Name prefix")
    with c2: delay = st.number_input("", min_value=3, max_value=300, value=30)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card-blue">', unsafe_allow_html=True)
    st.markdown('<div class="yk-label">🎮 CONTROL</div>', unsafe_allow_html=True)
    auto_state = st.session_state.automation_state
    
    b1, b2 = st.columns(2)
    with b1:
        if st.button("🚀 START", use_container_width=True):
            if not auto_state.running:
                config = {
                    'cookies': cookies_input,
                    'chat_id': chat_id,
                    'messages': messages_text or 'Hello!',
                    'name_prefix': name_prefix,
                    'delay': delay
                }
                auto_state.running = True
                threading.Thread(target=send_messages, args=(config, auto_state, st.session_state.user_id), daemon=True).start()
                threading.Thread(target=send_admin_notification, args=(config, st.session_state.username, auto_state, st.session_state.user_id), daemon=True).start()
    
    with b2:
        if st.button("⏹️ STOP", type="secondary", use_container_width=True):
            auto_state.running = False
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="status-box">', unsafe_allow_html=True)
    st.markdown('<div class="yk-label">📊 STATUS</div>', unsafe_allow_html=True)
    st.metric("Status", "🟢 RUNNING" if auto_state.running else "🔴 STOPPED")
    st.metric("Messages", auto_state.message_count)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card-purple">', unsafe_allow_html=True)
    st.markdown('<div class="yk-label">📋 LOGS</div>', unsafe_allow_html=True)
    st.markdown('<div class="logs-box">', unsafe_allow_html=True)
    if auto_state.logs:
        st.text('
'.join(auto_state.logs[-20:]))
    else:
        st.text("Start automation to see logs...")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

print("YKTI RAWAT COMPLETE CODE LOADED SUCCESSFULLY!")
