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
import requests

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
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    background-attachment: fixed;
}

.main .block-container {
    background: rgba(255, 255, 255, 0.95) !important;
    border-radius: 25px;
    padding: 35px;
    border: 3px solid transparent;
    background-clip: padding-box;
    position: relative;
    animation: containerFloat 6s ease-in-out infinite;
    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}

.main .block-container::before {
    content: '';
    position: absolute;
    inset: -3px;
    background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #f9ca24, #ff6b6b);
    border-radius: 28px;
    z-index: -1;
    animation: borderRotate 4s linear infinite;
}

@keyframes borderRotate {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@keyframes containerFloat {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}

.main-header {
    background: rgba(255, 255, 255, 0.98) !important;
    padding: 3rem 2rem;
    border-radius: 25px;
    text-align: center;
    margin-bottom: 3rem;
    border: 3px solid transparent;
    background-clip: padding-box;
    position: relative;
    overflow: hidden;
    box-shadow: 0 15px 35px rgba(0,0,0,0.1);
}

.main-header::before {
    content: '';
    position: absolute;
    inset: -3px;
    background: linear-gradient(45deg, #4ecdc4, #44a08d, #f9ca24, #4ecdc4);
    border-radius: 28px;
    z-index: -1;
    animation: headerBorder 3s linear infinite;
}

@keyframes headerBorder {
    0% { transform: rotate(0deg) scale(1); }
    50% { transform: rotate(180deg) scale(1.02); }
    100% { transform: rotate(360deg) scale(1); }
}

.main-header h1 {
    background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #f9ca24);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 3.5rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: 2px;
    animation: textRainbow 3s linear infinite;
}

@keyframes textRainbow {
    0% { background-position: 0% 50%; }
    100% { background-position: 300% 50%; }
}

.main-header p {
    color: #2c3e50;
    font-size: 1.4rem;
    font-weight: 600;
    margin-top: 1rem;
    animation: pulseGlow 2s ease-in-out infinite alternate;
}

@keyframes pulseGlow {
    from { filter: brightness(1); text-shadow: 0 0 10px rgba(78,205,196,0.5); }
    to { filter: brightness(1.1); text-shadow: 0 0 20px rgba(78,205,196,0.8); }
}

.stButton>button {
    background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 50%, #f9ca24 100%);
    background-size: 200% 200%;
    color: #000 !important;
    border: none;
    border-radius: 20px;
    padding: 1.2rem 3rem;
    font-weight: 700;
    font-size: 1.2rem;
    position: relative;
    overflow: hidden;
    text-transform: uppercase;
    letter-spacing: 1px;
    animation: buttonShift 4s ease infinite;
    transition: all 0.4s ease;
    box-shadow: 0 10px 25px rgba(78,205,196,0.4);
}

@keyframes buttonShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.stButton>button:hover {
    animation: none;
    background: linear-gradient(135deg, #f9ca24 0%, #ff6b6b 100%);
    transform: translateY(-5px) scale(1.05);
    box-shadow: 0 15px 35px rgba(78,205,196,0.6);
}

.stTextInput>div>div>input, 
.stTextArea>div>div>textarea, 
.stNumberInput>div>div>input {
    background: rgba(255, 255, 255, 0.95) !important;
    border: 3px solid #e8f5e8;
    border-radius: 15px;
    color: #2c3e50 !important;
    padding: 1.2rem;
    font-weight: 500;
    position: relative;
    transition: all 0.4s ease;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.stTextInput>div>div>input:focus, 
.stTextArea>div>div>textarea:focus {
    border-image: linear-gradient(45deg, #4ecdc4, #f9ca24, #ff6b6b) 1;
    background: rgba(255, 255, 255, 1) !important;
    transform: scale(1.02);
    box-shadow: 0 10px 25px rgba(78,205,196,0.3);
}

label {
    color: #2c3e50 !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    margin-bottom: 10px !important;
    animation: labelFloat 3s ease-in-out infinite;
}

@keyframes labelFloat {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-3px); }
}

.stFileUploader {
    border: 3px dashed #4ecdc4;
    border-radius: 15px;
    padding: 2rem;
    background: rgba(78,205,196,0.1);
    transition: all 0.3s ease;
}

.stFileUploader:hover {
    border-color: #f9ca24;
    background: rgba(249,202,36,0.15);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #f8f9ff 100%) !important;
    border-right: 4px solid #4ecdc4;
}

.metric-container {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 20px;
    padding: 2rem;
    border: 3px solid transparent;
    animation: metricPulse 2s ease-in-out infinite;
}

@keyframes metricPulse {
    0%, 100% { box-shadow: 0 0 20px rgba(78,205,196,0.3); }
    50% { box-shadow: 0 0 30px rgba(78,205,196,0.6); }
}

.console-output {
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
    border: 2px solid #4ecdc4;
    color: #00ff88 !important;
    border-radius: 15px;
    padding: 1.5rem;
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
if 'automation_state' not in st.session_state:
    class AutomationState:
        def __init__(self):
            self.running = False
            self.message_count = 0
            self.logs = []
            self.message_rotation_index = 0
    st.session_state.automation_state = AutomationState()

def log_message(msg, automation_state=None):
    timestamp = time.strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"
    
    if automation_state:
        automation_state.logs.append(formatted_msg)
    else:
        st.session_state.logs.append(formatted_msg)
    
    if len(st.session_state.logs) > 100:
        st.session_state.logs.pop(0)

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
        
        if config['cookies'] and config['cookies'].strip():
            log_message(f'{process_id}: Adding multiple cookies...', automation_state)
            cookie_array = [cookie.strip() for cookie in config['cookies'].split(';') if cookie.strip()]
            for cookie_str in cookie_array:
                try:
                    first_equal_index = cookie_str.find('=')
                    if first_equal_index > 0:
                        name = cookie_str[:first_equal_index].strip()
                        value = cookie_str[first_equal_index + 1:].strip()
                        driver.add_cookie({
                            'name': name,
                            'value': value,
                            'domain': '.facebook.com',
                            'path': '/'
                        })
                        log_message(f'{process_id}: Added cookie: {name}', automation_state)
                except Exception as e:
                    log_message(f'{process_id}: Cookie add failed: {str(e)[:50]}', automation_state)
                    continue
        
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
        messages_list = [msg.strip() for msg in config['messages'].split('
') if msg.strip()]
        
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
                else:
                    log_message(f'{process_id}: Message sent successfully!', automation_state)
                
                messages_sent += 1
                automation_state.message_count = messages_sent
                
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

# MAIN UI
st.markdown('<h1 class="main-header">🚀 YKTI RAWAT Automation</h1>', unsafe_allow_html=True)
st.markdown('<p class="main-header">Advanced Facebook Messenger Automation Tool</p>', unsafe_allow_html=True)

# COL1: Inputs
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📤 Configuration")
    
    cookies_input = st.text_area(
        "🍪 **Multiple Facebook Cookies** (separate multiple accounts with `;`)",
        height=120,
        placeholder="c_user=abc123; xs=def456; fr=ghi789; datr=jkl012; sb=mno345; wd=xyz678"
    )
    
    chat_id = st.text_input("🔗 **Chat/Thread ID** (optional, leave empty for inbox)")
    name_prefix = st.text_input("🏷️ **Message Prefix** (optional)")
    
    uploaded_file = st.file_uploader("📄 **Upload Messages TXT File**", type=['txt'])
    
    if uploaded_file is not None:
        messages_content = uploaded_file.read().decode('utf-8')
        st.success(f"✅ Loaded {len([line.strip() for line in messages_content.splitlines() if line.strip()])} messages from file!")
    else:
        messages_content = st.text_area("✏️ **Or Enter Messages** (one per line)", height=150)

with col2:
    st.markdown("### ⚙️ Settings")
    delay_time = st.number_input("⏱️ **Delay (seconds)**", min_value=1, max_value=300, value=10)
    
    st.markdown("### 📊 Status")
    st.metric("📨 Messages Sent", st.session_state.message_count)
    st.metric("🔄 Status", "🟢 Running" if st.session_state.automation_running else "🔴 Stopped")

# Buttons
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])

with col_btn1:
    start_btn = st.button("🚀 **START AUTOMATION**", type="primary", use_container_width=True)

with col_btn2:
    stop_btn = st.button("⏹️ **STOP AUTOMATION**", use_container_width=True)

# Automation Logic
if start_btn and cookies_input.strip() and (uploaded_file is not None or messages_content.strip()):
    if st.session_state.automation_running:
        st.warning("⚠️ Automation already running!")
    else:
        st.session_state.automation_running = True
        st.session_state.automation_state.running = True
        
        messages_final = messages_content if uploaded_file is None else messages_content
        
        config = {
            'cookies': cookies_input,
            'chat_id': chat_id,
            'name_prefix': name_prefix,
            'delay': delay_time,
            'messages': messages_final
        }
        
        # Start in background thread
        thread = threading.Thread(target=send_messages, args=(config, st.session_state.automation_state, 'MAIN'))
        thread.daemon = True
        thread.start()
        
        st.success("✅ Automation started successfully!")

if stop_btn:
    st.session_state.automation_running = False
    st.session_state.automation_state.running = False
    st.success("✅ Automation stopped!")

# Logs Display
st.markdown("### 📋 Real-time Logs")
log_placeholder = st.empty()

if st.session_state.logs:
    with log_placeholder.container():
        st.text_area(
            "Live Console Output:",
            value="
".join(st.session_state.logs[-50:]),
            height=300,
            key="live_logs"
        )

st.markdown("---")
st.markdown("*✨ YKTI RAWAT - Professional Facebook Automation Tool ✨*")
