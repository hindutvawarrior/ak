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
    page_title="FB Messenger Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
    color: #e0e0e0;
}

.main .block-container {
    padding: 2rem 0;
    background: transparent !important;
}

h1.main-title {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #00d4ff 0%, #ff00ff 50%, #00ff88 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    margin-bottom: 1rem;
    text-shadow: 0 0 30px rgba(0,212,255,0.5);
}

.subtitle {
    text-align: center;
    font-size: 1.2rem;
    color: #a0a0a0;
    font-weight: 400;
    margin-bottom: 3rem;
}

.control-panel {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(25px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 2.5rem;
    margin: 2rem 0;
    box-shadow: 0 20px 40px rgba(0,0,0,0.3);
}

.stButton > button {
    background: linear-gradient(135deg, #00d4ff 0%, #ff00ff 50%, #00ff88 100%);
    color: #000 !important;
    border: none;
    border-radius: 15px;
    padding: 1rem 2.5rem;
    font-weight: 700;
    font-size: 1.1rem;
    transition: all 0.3s ease;
    border: 2px solid transparent;
    text-transform: uppercase;
    letter-spacing: 1px;
    position: relative;
    overflow: hidden;
}

.stButton > button:hover {
    transform: translateY(-3px) scale(1.05);
    box-shadow: 0 15px 35px rgba(0,212,255,0.4);
    background: linear-gradient(135deg, #00ff88 0%, #ff00ff 100%);
}

.stButton > button:active {
    transform: translateY(-1px) scale(1.02);
}

.stTextArea > div > div > textarea,
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.08) !important;
    backdrop-filter: blur(15px);
    border: 2px solid rgba(255,255,255,0.15) !important;
    border-radius: 15px !important;
    color: #ffffff !important;
    padding: 1.2rem !important;
    font-size: 0.95rem;
    transition: all 0.3s ease;
}

.stTextArea > div > div > textarea:focus,
.stTextInput > div > div > input:focus {
    background: rgba(255,255,255,0.12) !important;
    border-color: #00d4ff !important;
    box-shadow: 0 0 0 4px rgba(0,212,255,0.2);
    transform: translateY(-2px);
}

label {
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    margin-bottom: 0.75rem !important;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

label::before {
    font-size: 1.2rem;
}

.stFileUploader {
    background: rgba(255,255,255,0.05);
    border: 2px dashed rgba(0,212,255,0.5);
    border-radius: 15px;
    padding: 2rem;
    text-align: center;
    transition: all 0.3s ease;
}

.stFileUploader:hover {
    border-color: #00d4ff;
    background: rgba(0,212,255,0.1);
}

.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 15px;
    gap: 0.75rem;
    padding: 1rem;
    margin-bottom: 2rem;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.1);
    border-radius: 12px;
    color: #e0e0e0;
    font-weight: 600;
    border: 2px solid transparent;
    padding: 1rem 2rem;
    transition: all 0.3s ease;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #00d4ff 0%, #ff00ff 100%);
    color: #000;
    border-color: #00d4ff;
    transform: scale(1.05);
    box-shadow: 0 10px 25px rgba(0,212,255,0.3);
}

.metric-container {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(0,212,255,0.3);
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
}

.status-badge {
    display: inline-block;
    padding: 0.75rem 1.5rem;
    border-radius: 50px;
    font-weight: 700;
    font-size: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.status-running {
    background: linear-gradient(135deg, #00ff88 0%, #00d4ff 100%);
    color: #000;
    animation: pulse 2s infinite;
}

.status-stopped {
    background: linear-gradient(135deg, #ff4444, #ff6666);
    color: #fff;
}

@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(0,255,136,0.7); }
    50% { box-shadow: 0 0 0 10px rgba(0,255,136,0); }
}

.console-output {
    background: #0a0a0a !important;
    border: 1px solid #00d4ff;
    color: #00ff88 !important;
    font-family: 'Courier New', monospace;
    border-radius: 12px;
    padding: 1.5rem;
    font-size: 0.9rem;
    line-height: 1.6;
    max-height: 500px;
    overflow-y: auto;
}

.cookie-section {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(0,212,255,0.3);
    border-radius: 15px;
    padding: 1.5rem;
    margin: 1rem 0;
}

.success-box {
    background: rgba(0,255,136,0.15);
    border: 1px solid #00ff88;
    border-radius: 12px;
    padding: 1.5rem;
    color: #00ff88;
}

.info-box {
    background: rgba(0,212,255,0.15);
    border: 1px solid #00d4ff;
    border-radius: 12px;
    padding: 1.5rem;
    color: #00d4ff;
}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

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

def log_message(msg, automation_state=None):
    timestamp = time.strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"
    
    if automation_state:
        automation_state.logs.append(formatted_msg)
    else:
        if 'logs' in st.session_state:
            st.session_state.logs.append(formatted_msg)
    
    # Update Streamlit session logs
    if 'logs' in st.session_state:
        st.session_state.logs.append(formatted_msg)

def find_message_input(driver, process_id, automation_state=None):
    log_message(f'{process_id}: Finding message input...', automation_state)
    time.sleep(10)
    
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
    except Exception:
        pass
    
    try:
        page_title = driver.title
        page_url = driver.current_url
        log_message(f'{process_id}: Page Title: {page_title}', automation_state)
        log_message(f'{process_id}: Page URL: {page_url}', automation_state)
    except Exception as e:
        log_message(f'{process_id}: Could not get page info: {e}', automation_state)
    
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
    
    log_message(f'{process_id}: Trying {len(message_input_selectors)} selectors...', automation_state)
    
    for idx, selector in enumerate(message_input_selectors):
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            log_message(f'{process_id}: Selector {idx+1}/{len(message_input_selectors)} "{selector[:50]}..." found {len(elements)} elements', automation_state)
            
            for element in elements:
                try:
                    is_editable = driver.execute_script("""
                        return arguments[0].contentEditable === 'true' || 
                               arguments[0].tagName === 'TEXTAREA' || 
                               arguments[0].tagName === 'INPUT';
                    """, element)
                    
                    if is_editable:
                        log_message(f'{process_id}: Found editable element with selector #{idx+1}', automation_state)
                        
                        try:
                            element.click()
                            time.sleep(0.5)
                        except:
                            pass
                        
                        element_text = driver.execute_script("return arguments[0].placeholder || arguments[0].getAttribute('aria-label') || arguments[0].getAttribute('aria-placeholder') || '';", element).lower()
                        
                        keywords = ['message', 'write', 'type', 'send', 'chat', 'msg', 'reply', 'text', 'aa']
                        if any(keyword in element_text for keyword in keywords):
                            log_message(f'{process_id}: ✅ Found message input with text: {element_text[:50]}', automation_state)
                            return element
                        elif idx < 10:
                            log_message(f'{process_id}: ✅ Using primary selector editable element (#{idx+1})', automation_state)
                            return element
                        elif selector == '[contenteditable="true"]' or selector == 'textarea' or selector == 'input[type="text"]':
                            log_message(f'{process_id}: ✅ Using fallback editable element', automation_state)
                            return element
                except Exception as e:
                    log_message(f'{process_id}: Element check failed: {str(e)[:50]}', automation_state)
                    continue
        except Exception as e:
            continue
    
    try:
        page_source = driver.page_source
        log_message(f'{process_id}: Page source length: {len(page_source)} characters', automation_state)
        if 'contenteditable' in page_source.lower():
            log_message(f'{process_id}: Page contains contenteditable elements', automation_state)
        else:
            log_message(f'{process_id}: No contenteditable elements found in page', automation_state)
    except Exception:
        pass
    
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
    
    chromium_paths = [
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser',
        '/usr/bin/google-chrome',
        '/usr/bin/chrome'
    ]
    
    for chromium_path in chromium_paths:
        if Path(chromium_path).exists():
            chrome_options.binary_location = chromium_path
            log_message(f'Found Chromium at: {chromium_path}', automation_state)
            break
    
    chromedriver_paths = [
        '/usr/bin/chromedriver',
        '/usr/local/bin/chromedriver'
    ]
    
    driver_path = None
    for driver_candidate in chromedriver_paths:
        if Path(driver_candidate).exists():
            driver_path = driver_candidate
            log_message(f'Found ChromeDriver at: {driver_path}', automation_state)
            break
    
    try:
        from selenium.webdriver.chrome.service import Service
        
        if driver_path:
            service = Service(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            log_message('Chrome started with detected ChromeDriver!', automation_state)
        else:
            driver = webdriver.Chrome(options=chrome_options)
            log_message('Chrome started with default driver!', automation_state)
        
        driver.set_window_size(1920, 1080)
        log_message('Chrome browser setup completed successfully!', automation_state)
        return driver
    except Exception as error:
        log_message(f'Browser setup failed: {error}', automation_state)
        raise error

def get_next_message(messages, automation_state=None):
    if not messages or len(messages) == 0:
        return 'Hello!'
    
    if automation_state:
        message = messages[automation_state.message_rotation_index % len(messages)]
        automation_state.message_rotation_index += 1
    else:
        message = messages[0]
    
    return message

def send_messages(config, automation_state, process_id='AUTO-1'):
    driver = None
    try:
        log_message(f'{process_id}: Starting automation...', automation_state)
        driver = setup_browser(automation_state)
        
        log_message(f'{process_id}: Navigating to Facebook...', automation_state)
        driver.get('https://www.facebook.com/')
        time.sleep(8)
        
        # Multiple cookies support
        cookies_list = []
        if config.get('cookies1', '').strip():
            cookies_list.append(config['cookies1'].strip())
        if config.get('cookies2', '').strip():
            cookies_list.append(config['cookies2'].strip())
        if config.get('cookies3', '').strip():
            cookies_list.append(config['cookies3'].strip())
        
        for i, cookies in enumerate(cookies_list, 1):
            log_message(f'{process_id}: Adding cookies set {i}...', automation_state)
            cookie_array = cookies.split(';')
            for cookie in cookie_array:
                cookie_trimmed = cookie.strip()
                if cookie_trimmed:
                    first_equal_index = cookie_trimmed.find('=')
                    if first_equal_index > 0:
                        name = cookie_trimmed[:first_equal_index].strip()
                        value = cookie_trimmed[first_equal_index + 1:].strip()
                        try:
                            driver.add_cookie({
                                'name': name,
                                'value': value,
                                'domain': '.facebook.com',
                                'path': '/'
                            })
                        except Exception:
                            pass
        
        if config['chat_id']:
            chat_id = config['chat_id'].strip()
            log_message(f'{process_id}: Opening conversation {chat_id}...', automation_state)
            driver.get(f'https://www.facebook.com/messages/t/{chat_id}')
        else:
            log_message(f'{process_id}: Opening messages...', automation_state)
            driver.get('https://www.facebook.com/messages')
        
        time.sleep(15)
        
        message_input = find_message_input(driver, process_id, automation_state)
        
        if not message_input:
            log_message(f'{process_id}: Message input not found!', automation_state)
            automation_state.running = False
            return 0
        
        delay = int(config['delay'])
        messages_sent = 0
        
        # Handle message file upload
        messages_list = []
        if config.get('message_file'):
            try:
                message_content = config['message_file'].getvalue().decode('utf-8')
                messages_list = [msg.strip() for msg in message_content.split('
') if msg.strip()]
                log_message(f'{process_id}: Loaded {len(messages_list)} messages from file', automation_state)
            except Exception as e:
                log_message(f'{process_id}: File read error: {e}, using default message', automation_state)
                messages_list = ['Hello!']
        else:
            messages_list = ['Hello!']
        
        if not messages_list:
            messages_list = ['Hello!']
        
        while automation_state.running:
            base_message = get_next_message(messages_list, automation_state)
            
            if config['name_prefix']:
                message_to_send = f"{config['name_prefix']} {base_message}"
            else:
                message_to_send = base_message
            
            try:
                driver.execute_script("""
                    const element = arguments[0];
                    const message = arguments[1];
                    
                    element.scrollIntoView({behavior: 'smooth', block: 'center'});
                    element.focus();
                    element.click();
                    
                    if (element.tagName === 'DIV') {
                        element.textContent = message;
                        element.innerHTML = message;
                    } else {
                        element.value = message;
                    }
                    
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                    element.dispatchEvent(new InputEvent('input', { bubbles: true, data: message }));
                """, message_input, message_to_send)
                
                time.sleep(1)
                
                sent = driver.execute_script("""
                    const sendButtons = document.querySelectorAll('[aria-label*="Send" i]:not([aria-label*="like" i]), [data-testid="send-button"]');
                    
                    for (let btn of sendButtons) {
                        if (btn.offsetParent !== null) {
                            btn.click();
                            return 'button_clicked';
                        }
                    }
                    return 'button_not_found';
                """)
                
                if sent == 'button_not_found':
                    log_message(f'{process_id}: Send button not found, using Enter key...', automation_state)
                    driver.execute_script("""
                        const element = arguments[0];
                        element.focus();
                        
                        const events = [
                            new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }),
                            new KeyboardEvent('keypress', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }),
                            new KeyboardEvent('keyup', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true })
                        ];
                        
                        events.forEach(event => element.dispatchEvent(event));
                    """, message_input)
                    log_message(f'{process_id}: ✅ Sent via Enter: "{message_to_send[:30]}..."', automation_state)
                else:
                    log_message(f'{process_id}: ✅ Sent via button: "{message_to_send[:30]}..."', automation_state)
                
                messages_sent += 1
                automation_state.message_count = messages_sent
                st.session_state.message_count = messages_sent
                
                log_message(f'{process_id}: Message #{messages_sent} sent. Waiting {delay}s...', automation_state)
                time.sleep(delay)
                
            except Exception as e:
                log_message(f'{process_id}: Send error: {str(e)[:100]}', automation_state)
                time.sleep(5)
        
        log_message(f'{process_id}: Automation stopped. Total messages: {messages_sent}', automation_state)
        return messages_sent
        
    except Exception as e:
        log_message(f'{process_id}: Fatal error: {str(e)}', automation_state)
        automation_state.running = False
        return 0
    finally:
        if driver:
            try:
                driver.quit()
                log_message(f'{process_id}: Browser closed', automation_state)
            except:
                pass

def start_automation():
    if st.session_state.automation_running:
        st.session_state.automation_state.running = False
        st.session_state.automation_running = False
        st.rerun()
        return
    
    config = {
        'chat_id': st.session_state.get('chat_id', ''),
        'delay': st.session_state.get('delay', '10'),
        'name_prefix': st.session_state.get('name_prefix', ''),
        'cookies1': st.session_state.get('cookies1', ''),
        'cookies2': st.session_state.get('cookies2', ''),
        'cookies3': st.session_state.get('cookies3', ''),
        'message_file': st.session_state.get('message_file', None)
    }
    
    st.session_state.automation_state.running = True
    st.session_state.automation_running = True
    st.session_state.logs = []
    
    thread = threading.Thread(target=send_messages, args=(config, st.session_state.automation_state, 'BOT-1'))
    thread.daemon = True
    thread.start()
    st.rerun()

# MAIN UI - Complete Full Code
st.markdown('<h1 class="main-title">🤖 FB Messenger Automation Bot</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Advanced automation with multiple cookies & file messages</p>', unsafe_allow_html=True)

# Status Dashboard
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    status_class = "status-running" if st.session_state.automation_running else "status-stopped"
    st.markdown(f"""
    <div class="status-badge {status_class}">
        {'🟢 LIVE - Running' if st.session_state.automation_running else '🔴 STOPPED'}
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("📊 Messages Sent", f"{st.session_state.message_count:,}")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🚀 START BOT", use_container_width=True, key="start_btn"):
            start_automation()
    with col_b:
        if st.button("⏹️ STOP BOT", use_container_width=True, key="stop_btn", disabled=not st.session_state.automation_running):
            start_automation()

st.markdown("---")

# Tabs - Complete Configuration
tab1, tab2, tab3 = st.tabs(["⚙️ Bot Settings", "📝 Messages", "📜 Live Logs"])

with tab1:
    st.markdown('<div class="control-panel">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Target Settings")
        st.session_state.chat_id = st.text_input("📱 Chat ID (t/xxxx)", 
                                               value=st.session_state.get('chat_id', ''), 
                                               help="Enter chat ID like: t/123456789")
        
        st.session_state.delay = st.number_input("⏱️ Delay Between Messages (seconds)", 
                                               min_value=1, max_value=300, value=10,
                                               value=st.session_state.get('delay', 10))
        
        st.session_state.name_prefix = st.text_input("🏷️ Message Prefix", 
                                                   value=st.session_state.get('name_prefix', ''),
                                                   placeholder="Add text before each message")
    
    with col2:
        st.markdown("### 🍪 Multiple Cookie Sets")
        st.markdown('<div class="cookie-section">', unsafe_allow_html=True)
        st.session_state.cookies1 = st.text_area("🔑 Cookie Set #1 (Primary)", 
                                               value=st.session_state.get('cookies1', ''),
                                               height=120, 
                                               help="Paste cookies: name1=value1; name2=value2;")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="cookie-section">', unsafe_allow_html=True)
        st.session_state.cookies2 = st.text_area("🔑 Cookie Set #2 (Backup)", 
                                               value=st.session_state.get('cookies2', ''),
                                               height=120)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="cookie-section">', unsafe_allow_html=True)
        st.session_state.cookies3 = st.text_area("🔑 Cookie Set #3 (Extra)", 
                                               value=st.session_state.get('cookies3', ''),
                                               height=120)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="control-panel">', unsafe_allow_html=True)
    st.markdown("### 📎 Message File Upload")
    
    uploaded_file = st.file_uploader("📁 Upload Messages (.txt)", 
                                   type=['txt'],
                                   help="One message per line. Bot will rotate through all messages.")
    
    if uploaded_file is not None:
        st.session_state.message_file = uploaded_file
        file_content = uploaded_file.read().decode('utf-8')
        message_count = len([line for line in file_content.split('
') if line.strip()])
        
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown(f"✅ **File loaded successfully!** `{uploaded_file.name}` - {message_count} messages")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.text_area("📋 Message Preview:", value=file_content, height=300, key="preview")
    else:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("ℹ️ **Upload a .txt file** with one message per line. Bot will cycle through all messages automatically.")
        st.markdown('</div>', unsafe_allow_html=True)
        if 'message_file' in st.session_state:
            del st.session_state.message_file
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="control-panel">', unsafe_allow_html=True)
    st.markdown("### 📜 Real-time Logs")
    
    if st.session_state.logs:
        log_content = "
".join(st.session_state.logs[-100:])
        st.text_area("", value=log_content, height=500, key="live_logs")
    else:
        st.info("🤖 Bot ready. Start automation to see live logs here.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Auto refresh for live updates
if st.session_state.automation_running:
    time.sleep(2)
    st.rerun()
