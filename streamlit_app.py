import streamlit as st
import time
import threading
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

st.set_page_config(page_title="YKTI RAWAT", page_icon="✅", layout="wide", initial_sidebar_state="expanded")

# Beautiful Bright Animated CSS (Dark theme हटाया)
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap');
* { font-family: 'Poppins', sans-serif; }
.stApp { 
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    background-attachment: fixed;
}
.main .block-container {
    background: rgba(255,255,255,0.95)!important;
    border-radius: 25px;
    padding: 35px;
    border: 3px solid transparent;
    animation: containerFloat 6s ease-in-out infinite;
    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}
.main .block-container::before {
    content: ''; position: absolute; inset: -3px;
    background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #f9ca24, #ff6b6b);
    border-radius: 28px; z-index: -1;
    animation: borderRotate 4s linear infinite;
}
@keyframes borderRotate { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
@keyframes containerFloat { 0%,100% { transform: translateY(0px); } 50% { transform: translateY(-10px); } }
.main-header {
    background: rgba(255,255,255,0.98)!important; padding: 3rem 2rem;
    border-radius: 25px; text-align: center; margin-bottom: 3rem;
    border: 3px solid transparent; animation: headerPulse 3s infinite;
}
.main-header h1 {
    background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #f9ca24);
    background-size: 300% 300%; -webkit-background-clip: text;
    -webkit-text-fill-color: transparent; font-size: 3.5rem;
    font-weight: 800; animation: textRainbow 3s linear infinite;
}
@keyframes textRainbow { 0% { background-position: 0% 50%; } 100% { background-position: 300% 50%; } }
.stButton>button {
    background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 50%, #f9ca24 100%);
    color: #000!important; border: none; border-radius: 20px;
    padding: 1.2rem 3rem; font-weight: 700; font-size: 1.2rem;
    animation: buttonShift 4s ease infinite; box-shadow: 0 10px 25px rgba(78,205,196,0.4);
}
.stButton>button:hover {
    background: linear-gradient(135deg, #f9ca24 0%, #ff6b6b 100%);
    transform: translateY(-5px) scale(1.05); box-shadow: 0 15px 35px rgba(78,205,196,0.6);
}
.stTextInput>div>div>input, .stTextArea>div>div>textarea {
    background: rgba(255,255,255,0.95)!important; border: 3px solid #e8f5e8;
    border-radius: 15px; color: #2c3e50!important; padding: 1.2rem;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}
label { color: #2c3e50!important; font-weight: 700!important; font-size: 1.1rem!important; }
.stFileUploader { border: 3px dashed #4ecdc4; border-radius: 15px; padding: 2rem; background: rgba(78,205,196,0.1); }
.console-output { background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%)!important; border: 2px solid #4ecdc4; color: #00ff88!important; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Session State
if 'automation_running' not in st.session_state: st.session_state.automation_running = False
if 'logs' not in st.session_state: st.session_state.logs = []
if 'message_count' not in st.session_state: st.session_state.message_count = 0

class AutomationState:
    def __init__(self):
        self.running = False
        self.message_count = 0
        self.logs = []
        self.message_rotation_index = 0

if 'automation_state' not in st.session_state:
    st.session_state.automation_state = AutomationState()

def log_message(msg):
    timestamp = time.strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"
    st.session_state.logs.append(formatted_msg)
    st.session_state.automation_state.logs.append(formatted_msg)
    if len(st.session_state.logs) > 100: st.session_state.logs.pop(0)

def find_message_input(driver, process_id):
    log_message(f'{process_id}: Finding message input...')
    time.sleep(10)
    message_input_selectors = [
        'div[contenteditable="true"][role="textbox"]', 'div[contenteditable="true"][data-lexical-editor="true"]',
        'div[aria-label*="message" i][contenteditable="true"]', 'div[contenteditable="true"][spellcheck="true"]',
        '[role="textbox"][contenteditable="true"]', '[contenteditable="true"]', 'textarea', 'input[type="text"]'
    ]
    for selector in message_input_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                is_editable = driver.execute_script("return arguments[0].contentEditable === 'true' || arguments[0].tagName === 'TEXTAREA' || arguments[0].tagName === 'INPUT';", element)
                if is_editable:
                    log_message(f'{process_id}: ✅ Found message input!')
                    return element
        except: continue
    return None

def setup_browser():
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1920, 1080)
    log_message('✅ Chrome browser setup completed!')
    return driver

def get_next_message(messages):
    if not messages: return 'Hello!'
    idx = st.session_state.automation_state.message_rotation_index % len(messages)
    st.session_state.automation_state.message_rotation_index += 1
    return messages[idx]

def send_messages(config):
    driver = None
    try:
        log_message('🚀 Starting Facebook automation...')
        driver = setup_browser()
        driver.get('https://www.facebook.com/')
        time.sleep(8)
        
        # Multiple Cookies Support (semicolon separated)
        if config['cookies'].strip():
            log_message('🍪 Adding multiple cookies...')
            cookie_array = [c.strip() for c in config['cookies'].split(';') if c.strip()]
            for cookie_str in cookie_array:
                try:
                    name, value = cookie_str.split('=', 1)
                    driver.add_cookie({'name': name.strip(), 'value': value.strip(), 'domain': '.facebook.com', 'path': '/'})
                except: continue
        
        # Open Chat
        if config['chat_id']:
            driver.get(f'https://www.facebook.com/messages/t/{config["chat_id"]}')
        else:
            driver.get('https://www.facebook.com/messages')
        time.sleep(15)
        
        message_input = find_message_input(driver, 'MAIN')
        if not message_input:
            log_message('❌ Message input not found!')
            return
        
        delay = int(config['delay'])
        messages_list = [msg.strip() for msg in config['messages'].split('
') if msg.strip()]
        
        while st.session_state.automation_state.running:
            message = get_next_message(messages_list)
            if config['name_prefix']: message = f"{config['name_prefix']} {message}"
            
            # Type message
            driver.execute_script("""
                const el=arguments[0], msg=arguments[1];
                el.focus(); el.click();
                if(el.tagName==='DIV'){ el.textContent=msg; el.innerHTML=msg; } else { el.value=msg; }
                el.dispatchEvent(new Event('input',{bubbles:true}));
            """, message_input, message)
            time.sleep(1)
            
            # Send message
            sent = driver.execute_script("""
                const btns=document.querySelectorAll('[aria-label*="Send" i], [data-testid="send-button"]');
                for(let btn of btns){ if(btn.offsetParent!==null){ btn.click(); return 'sent'; } }
                return 'enter';
            """)
            
            if sent == 'enter':
                driver.execute_script("""
                    const el=arguments[0];
                    el.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}));
                    el.dispatchEvent(new KeyboardEvent('keypress',{key:'Enter',bubbles:true}));
                    el.dispatchEvent(new KeyboardEvent('keyup',{key:'Enter',bubbles:true}));
                """, message_input)
            
            st.session_state.message_count += 1
            st.session_state.automation_state.message_count += 1
            log_message(f'✅ Message #{st.session_state.message_count} sent! Waiting {delay}s...')
            time.sleep(delay)
            
    except Exception as e:
        log_message(f'❌ Error: {str(e)[:100]}')
    finally:
        if driver: driver.quit()
        log_message('🔒 Browser closed')

# MAIN UI
st.markdown('<h1 class="main-header">🚀 YKTI RAWAT Automation</h1>', unsafe_allow_html=True)
st.markdown('<p class="main-header">Professional Facebook Messenger Tool</p>', unsafe_allow_html=True)

# Inputs
col1, col2 = st.columns([2,1])

with col1:
    st.markdown("### 📤 Configuration")
    cookies_input = st.text_area("🍪 **Multiple Facebook Cookies** (semicolon separated)", 
                                height=120, 
                                placeholder="c_user=abc123; xs=def456; fr=ghi789; datr=jkl012")
    
    chat_id = st.text_input("🔗 **Chat ID** (optional)")
    name_prefix = st.text_input("🏷️ **Message Prefix** (optional)")
    
    uploaded_file = st.file_uploader("📄 **Upload Messages TXT**", type=['txt'])
    if uploaded_file:
        messages_content = uploaded_file.read().decode('utf-8')
        st.success(f"✅ Loaded {len([l for l in messages_content.splitlines() if l.strip()])} messages")
    else:
        messages_content = st.text_area("✏️ **Enter Messages** (one per line)", height=150)

with col2:
    st.markdown("### ⚙️ Settings")
    delay_time = st.number_input("⏱️ **Delay (seconds)**", min_value=1, max_value=300, value=10)
    
    st.markdown("### 📊 Status")
    st.metric("📨 Messages Sent", st.session_state.message_count)
    st.metric("🔄 Status", "🟢 Running" if st.session_state.automation_running else "🔴 Stopped")

# Buttons
col_btn1, col_btn2 = st.columns(2)
with col_btn1: start_btn = st.button("🚀 **START**", type="primary", use_container_width=True)
with col_btn2: stop_btn = st.button("⏹️ **STOP**", use_container_width=True)

# Automation Control
if start_btn and cookies_input.strip() and messages_content.strip():
    if st.session_state.automation_running:
        st.warning("⚠️ Already running!")
    else:
        st.session_state.automation_running = True
        st.session_state.automation_state.running = True
        config = {
            'cookies': cookies_input,
            'chat_id': chat_id or '',
            'name_prefix': name_prefix or '',
            'delay': delay_time,
            'messages': messages_content
        }
        thread = threading.Thread(target=send_messages, args=(config,))
        thread.daemon = True
        thread.start()
        st.success("✅ Started!")

if stop_btn:
    st.session_state.automation_running = False
    st.session_state.automation_state.running = False
    st.success("✅ Stopped!")

# Logs
st.markdown("### 📋 Live Logs")
if st.session_state.logs:
    st.text_area("Console:", value="
".join(st.session_state.logs[-30:]), height=300)

st.markdown("---")
st.markdown("*✨ YKTI RAWAT - Complete Working Tool ✨*")
