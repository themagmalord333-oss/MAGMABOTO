import telebot
import json
import os
import subprocess
import threading
import time
from telebot import types
from flask import Flask

# --- CONFIGURATION ---
TOKEN = '8321333186:AAEWHHj7OpeS8lARdm1vNjcWOd2ilrc2vWE' 
REQUEST_ID = 6927405562  # Admin Account ID
OWNER_ID = 8081343902    # Aapki Owner ID

# --- MAIN CHANNEL MONITOR ---
# Bot must be ADMIN here
MAIN_FORCE_CHANNEL = "@Anysnapupdate" 
MAIN_FORCE_GROUP = "@Anysnapsupport"
CHANNEL_LINK = "https://t.me/Anysnapupdate"
GROUP_LINK = "https://t.me/Anysnapsupport"
# ----------------------------

# ==========================================
# 🔥 FLASK WEB SERVER
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot is Running 24/7!"

def run_web():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# ==========================================
# 🤖 BOT SETUP
# ==========================================
print("🚀 Main Hosting Bot Starting...")
bot = telebot.TeleBot(TOKEN)
running_bots = {}

if not os.path.exists('clones'): os.makedirs('clones')

# ==========================================
# 1. DATA MANAGEMENT (SMART REFERRAL SYSTEM)
# ==========================================
USER_DATA_FILE = "users.json"

def load_users():
    if not os.path.exists(USER_DATA_FILE): return {}
    try:
        with open(USER_DATA_FILE, 'r') as f: return json.load(f)
    except: return {}

def save_users(data):
    with open(USER_DATA_FILE, 'w') as f: json.dump(data, f)

def get_user_ref_count(user_id):
    data = load_users()
    return data.get(str(user_id), {}).get('referrals', 0)

# Step 1: Sirf Pending me daalo (Point mat do abhi)
def set_pending_referral(new_user_id, referrer_id):
    data = load_users()
    new_user_id = str(new_user_id)
    referrer_id = str(referrer_id)

    if new_user_id == referrer_id: return # Khud ko refer nahi kar sakte

    if new_user_id not in data:
        data[new_user_id] = {'referrals': 0, 'invited_by': None, 'pending_ref': None}
    
    # Agar pehle se invited nahi hai, to pending me daal do
    if data[new_user_id].get('invited_by') is None:
        data[new_user_id]['pending_ref'] = referrer_id
        save_users(data)

# Step 2: Jab Join kar le, tab Point do
def confirm_referral(user_id):
    data = load_users()
    user_id = str(user_id)
    
    if user_id in data and data[user_id].get('pending_ref'):
        referrer_id = data[user_id]['pending_ref']
        
        # Verify Referrer exists
        if referrer_id not in data:
            data[referrer_id] = {'referrals': 0, 'invited_by': None}

        # Point Add Karo
        data[referrer_id]['referrals'] += 1
        
        # Invite Confirm Karo
        data[user_id]['invited_by'] = referrer_id
        data[user_id]['pending_ref'] = None # Pending clear
        
        save_users(data)
        return referrer_id # ID return karo taaki notification bhej sakein
    return None

def deduct_referrals(user_id, amount):
    data = load_users()
    user_id = str(user_id)
    if user_id in data and data[user_id]['referrals'] >= amount:
        data[user_id]['referrals'] -= amount
        save_users(data)
        return True
    return False

# ==========================================
# 2. FORCE JOIN CHECKER
# ==========================================
def is_user_joined_main(user_id):
    try:
        # Check Channel
        stat_c = bot.get_chat_member(MAIN_FORCE_CHANNEL, user_id).status
        if stat_c not in ['creator', 'administrator', 'member']: return False
        
        # Check Group
        stat_g = bot.get_chat_member(MAIN_FORCE_GROUP, user_id).status
        if stat_g not in ['creator', 'administrator', 'member']: return False
        
        return True
    except:
        # Agar Bot admin nahi hai to Safety ke liye True
        return True

def get_main_join_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK))
    markup.add(types.InlineKeyboardButton("👥 Join Group", url=GROUP_LINK))
    markup.add(types.InlineKeyboardButton("✅ Checked / Verify", callback_data="check_main_join"))
    return markup

# ==========================================
# 3. SECURITY MONITOR
# ==========================================
def monitor_clone_owners():
    while True:
        time.sleep(30)
        try:
            if not os.path.exists('clones'): continue
            for uid in os.listdir('clones'):
                if not uid.isdigit(): continue
                try:
                    stat = bot.get_chat_member(MAIN_FORCE_CHANNEL, uid).status
                    if stat not in ['creator', 'administrator', 'member']:
                        stop_user_bots(uid)
                except: pass
        except: pass

def stop_user_bots(user_id):
    user_dir = f"clones/{user_id}"
    if not os.path.exists(user_dir): return
    for f in os.listdir(user_dir):
        if f.endswith('_info.json'):
            try:
                path = f"{user_dir}/{f}"
                with open(path, 'r') as file: data = json.load(file)
                if data.get('status') == 'active':
                    if data['name'] in running_bots:
                        running_bots[data['name']].terminate()
                        del running_bots[data['name']]
                    data['status'] = 'suspended'
                    with open(path, 'w') as file: json.dump(data, file)
                    bot.send_message(user_id, f"⚠️ **Bot Suspended!**\nYou left our channel.")
            except: pass

# ==========================================
# 4. CLONE BOT TEMPLATE
# ==========================================
def get_clone_code(token, bot_username, custom_credit, force_subs_list):
    return f'''
import telebot
import time
from telebot import types

TOKEN = "{token}"
REQUEST_ID = {REQUEST_ID}
MY_USERNAME = "{bot_username}"
CUSTOM_CREDIT = "{custom_credit}"
FORCE_SUBS = {force_subs_list}

bot = telebot.TeleBot(TOKEN)
request_storage = {{}}

LOADING_GIF = "https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif"
COMMANDS_LIST = ['num', 'vehicle', 'aadhar', 'familyinfo', 'vnum', 'fam', 'sms', 'clone']

def get_missing_channels(user_id):
    if not FORCE_SUBS: return []
    missing = []
    for sub in FORCE_SUBS:
        try:
            stat = bot.get_chat_member(sub['id'], user_id).status
            if stat not in ['creator', 'administrator', 'member']:
                missing.append(sub)
        except: pass
    return missing

def get_join_markup(missing_channels):
    markup = types.InlineKeyboardMarkup()
    for sub in missing_channels:
        markup.add(types.InlineKeyboardButton(f"📢 Join {{sub['id']}}", url=sub['url']))
    markup.add(types.InlineKeyboardButton("✅ Checked", callback_data="check_join"))
    return markup

@bot.message_handler(commands=['start', 'help'])
def start(m):
    missing = get_missing_channels(m.from_user.id)
    if missing:
        bot.send_message(m.chat.id, "⚠️ **Join Channels First!**", reply_markup=get_join_markup(missing))
        return
    text = (f"🚀 **@{{MY_USERNAME}} is Online!**\\n\\n🔥 **Commands:**\\n📱 `/num` 🚗 `/vehicle` 🆔 `/aadhar`")
    bot.reply_to(m, text, parse_mode="Markdown")

@bot.message_handler(commands=COMMANDS_LIST)
def handle_query(m):
    missing = get_missing_channels(m.from_user.id)
    if missing:
        bot.send_message(m.chat.id, "⚠️ **Join Channels First!**", reply_markup=get_join_markup(missing))
        return
    try:
        if len(m.text.split()) < 2:
            bot.reply_to(m, "❌ Usage: `{{m.text.split()[0]}} <value>`")
            return
        anim = bot.send_animation(m.chat.id, LOADING_GIF, caption="⚡ **Fetching Data...**")
        try:
            sent = bot.send_message(REQUEST_ID, m.text)
            request_storage[sent.message_id] = {{'chat_id': m.chat.id, 'anim_id': anim.message_id}}
        except:
            bot.delete_message(m.chat.id, anim.message_id)
            bot.reply_to(m, "❌ System Offline.")
    except: pass

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join(call):
    missing = get_missing_channels(call.from_user.id)
    if not missing:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "✅ **Verified!**")
    else:
        bot.answer_callback_query(call.id, "❌ Not Joined!", show_alert=True)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=get_join_markup(missing))

def send_data_to_user(target_chat, anim_msg_id, message_object):
    try:
        try: bot.delete_message(target_chat, anim_msg_id)
        except: pass
        if message_object.text:
            if "Searching" in message_object.text: return 
            final_text = message_object.text.replace("@MAGMAxRICH", CUSTOM_CREDIT)
            bot.send_message(target_chat, final_text)
        else: bot.copy_message(target_chat, message_object.chat.id, message_object.message_id)
    except: pass

@bot.message_handler(content_types=['text', 'photo', 'document'], func=lambda m: m.from_user.id == REQUEST_ID and m.reply_to_message)
def handle_reply(m):
    try:
        orig_id = m.reply_to_message.message_id
        if orig_id in request_storage:
            user_data = request_storage[orig_id]
            send_data_to_user(user_data['chat_id'], user_data['anim_id'], m)
    except: pass

@bot.edited_message_handler(content_types=['text', 'photo', 'document'], func=lambda m: m.from_user.id == REQUEST_ID and m.reply_to_message)
def handle_edit(m):
    try:
        orig_id = m.reply_to_message.message_id
        if orig_id in request_storage:
            user_data = request_storage[orig_id]
            send_data_to_user(user_data['chat_id'], user_data['anim_id'], m)
    except: pass

while True:
    try: bot.infinity_polling(timeout=15)
    except: time.sleep(5)
'''

# ==========================================
# 5. HANDLERS (START & CLONE)
# ==========================================

@bot.message_handler(commands=['start'])
def welcome(m):
    user_id = m.from_user.id
    
    # 1. Store Referral as PENDING (Do not give credit yet)
    args = m.text.split()
    if len(args) > 1:
        referrer_id = args[1]
        if referrer_id.isdigit():
            set_pending_referral(user_id, referrer_id)

    # 2. Check Force Join BEFORE showing Menu
    if not is_user_joined_main(user_id):
        bot.send_message(m.chat.id, "⚠️ **You must Join our Channels to use this Bot!**\n\n👇 Click below to Join & Verify.", reply_markup=get_main_join_markup())
        return

    # 3. If Joined, Confirm Referral (Give credit now)
    ref_id = confirm_referral(user_id)
    if ref_id:
        try: bot.send_message(ref_id, f"🎉 **New Referral Verified!**\nUser: {m.from_user.first_name}\n\nBalance: {get_user_ref_count(ref_id)} Points")
        except: pass

    # 4. Show Welcome Menu
    show_main_menu(m)

def show_main_menu(m):
    ref_link = f"https://t.me/{bot.get_me().username}?start={m.from_user.id}"
    refs = get_user_ref_count(m.from_user.id)
    
    text = (f"👋 **Welcome to Bot Hosting!**\n\n"
            f"🤖 You can clone your own bot here.\n"
            f"💰 **Cost:** 2 Referrals = 1 Clone Bot\n\n"
            f"📊 **Your Refs:** {refs}\n"
            f"🔗 **Your Link:** `{ref_link}`\n\n"
            f"👇 Click /clone to start.")
    bot.reply_to(m, text, parse_mode="Markdown")

# --- CALLBACK: MAIN JOIN CHECK ---
@bot.callback_query_handler(func=lambda call: call.data == "check_main_join")
def check_main_join(call):
    if is_user_joined_main(call.from_user.id):
        # 1. Delete "Join" Msg
        bot.delete_message(call.message.chat.id, call.message.message_id)
        
        # 2. Confirm Referral (Give credit now)
        ref_id = confirm_referral(call.from_user.id)
        if ref_id:
            try: bot.send_message(ref_id, f"🎉 **New Referral Verified!**\nUser: {call.from_user.first_name}\n\nBalance: {get_user_ref_count(ref_id)} Points")
            except: pass
            
        # 3. Show Menu
        bot.send_message(call.message.chat.id, "✅ **Verified!**")
        show_main_menu(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ Not Joined Yet!", show_alert=True)

@bot.message_handler(commands=['clone'])
def ask_token(m):
    user_id = m.from_user.id
    
    # Force Join Check (Double Safety)
    if not is_user_joined_main(user_id):
        bot.send_message(m.chat.id, "⚠️ **Join Channels First!**", reply_markup=get_main_join_markup())
        return
    
    # Referral Check
    if user_id != OWNER_ID:
        refs = get_user_ref_count(user_id)
        if refs < 2:
            ref_link = f"https://t.me/{bot.get_me().username}?start={user_id}"
            bot.reply_to(m, f"❌ **Insufficient Referrals!**\n\nCost: 2 Refs = 1 Clone\nYou have: {refs} Refs\n\n🔗 **Link:**\n`{ref_link}`", parse_mode="Markdown")
            return
    
    msg = bot.reply_to(m, "🔑 **Send your Bot Token** from @BotFather:")
    bot.register_next_step_handler(msg, process_token)

def process_token(m):
    try:
        token = m.text.strip()
        try:
            temp_bot = telebot.TeleBot(token)
            bot_info = temp_bot.get_me()
            bot_username = bot_info.username
        except:
            bot.reply_to(m, "❌ **Invalid Token!** Try again via /clone")
            return
        msg = bot.reply_to(m, f"✅ Verified: @{bot_username}\n\n✍️ **Enter Footer Credit:**")
        bot.register_next_step_handler(msg, process_credit, token, bot_username)
    except: bot.reply_to(m, "❌ Error.")

def process_credit(m, token, bot_username):
    custom_credit = m.text.strip()
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("✅ Add Channels", "⏩ Skip")
    msg = bot.reply_to(m, "📢 **Add Force Subscribe?**", reply_markup=markup)
    bot.register_next_step_handler(msg, process_force_decision, token, bot_username, custom_credit, [])

def process_force_decision(m, token, bot_username, custom_credit, subs_list):
    if m.text == "⏩ Skip":
        create_bot_final(m, token, bot_username, custom_credit, [])
    else:
        msg = bot.reply_to(m, "1️⃣ **Send Channel Username:**\n(e.g., `@MyChannel`)", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, step_ask_username, token, bot_username, custom_credit, subs_list)

def step_ask_username(m, token, bot_username, custom_credit, subs_list):
    text = m.text.strip()
    if text.lower() == "done":
        create_bot_final(m, token, bot_username, custom_credit, subs_list)
        return
    if not text.startswith("@"):
        bot.reply_to(m, "⚠️ Must start with `@`. Try again or type `Done`.")
        bot.register_next_step_handler(m, step_ask_username, token, bot_username, custom_credit, subs_list)
        return
    
    current_username = text
    msg = bot.reply_to(m, f"🔗 **Send Link for {current_username}:**")
    bot.register_next_step_handler(msg, step_ask_link, token, bot_username, custom_credit, subs_list, current_username)

def step_ask_link(m, token, bot_username, custom_credit, subs_list, current_username):
    link = m.text.strip()
    subs_list.append({'id': current_username, 'url': link})
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("Done")
    msg = bot.reply_to(m, f"✅ Added! ({len(subs_list)})\n\n👇 **Next Username** OR click **Done**.", reply_markup=markup)
    bot.register_next_step_handler(msg, step_ask_username, token, bot_username, custom_credit, subs_list)

def create_bot_final(m, token, bot_username, custom_credit, subs_list):
    try:
        user_id = m.from_user.id
        if user_id != OWNER_ID:
            if not deduct_referrals(user_id, 2):
                bot.reply_to(m, "❌ **Error:** Referrals changed!")
                return
        
        user_dir = f"clones/{user_id}"
        if not os.path.exists(user_dir): os.makedirs(user_dir)
        filename = f"{user_dir}/{bot_username}_bot.py"
        
        with open(filename, 'w') as f:
            f.write(get_clone_code(token, bot_username, custom_credit, str(subs_list)))
        
        info = {'user_id': str(user_id), 'name': bot_username, 'token': token, 'status': 'pending', 'file': filename}
        with open(f"{user_dir}/{bot_username}_info.json", 'w') as f: json.dump(info, f)
            
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Approve", callback_data=f"app|{user_id}|{bot_username}"), types.InlineKeyboardButton("❌ Reject", callback_data=f"rej|{user_id}|{bot_username}"))
        
        user_markup = types.InlineKeyboardMarkup()
        user_markup.add(types.InlineKeyboardButton("⚡ Contact Owner for Fast Approval", url="https://t.me/MAGMAxRICH"))
        
        bot.reply_to(m, f"⏳ **Request Submitted!**\nBot: @{bot_username}\n\n**2 Referrals Deducted!** ✅", reply_markup=user_markup)
        bot.send_message(OWNER_ID, f"🔔 NEW CLONE\nUser: {user_id}\nBot: @{bot_username}\nChannels: {len(subs_list)}", reply_markup=markup)
    except Exception as e:
        bot.reply_to(m, f"❌ Error: {e}")

# ==========================================
# 6. RUNNER
# ==========================================

@bot.callback_query_handler(func=lambda call: call.data.startswith(('app|', 'rej|')))
def handle_callback(call):
    if call.from_user.id != OWNER_ID: return
    try:
        action, uid, uname = call.data.split('|')
        info_path = f"clones/{uid}/{uname}_info.json"
        
        if action == 'app':
            with open(info_path, 'r') as f: data = json.load(f)
            data['status'] = 'active'
            with open(info_path, 'w') as f: json.dump(data, f)
            start_bot_process(data['file'], uname)
            bot.edit_message_text(f"✅ Approved: @{uname}", call.message.chat.id, call.message.message_id)
            bot.send_message(uid, f"🎉 **Approved!**\nYour bot @{uname} is now Active!")
        elif action == 'rej':
            os.remove(info_path)
            bot.edit_message_text(f"❌ Rejected: @{uname}", call.message.chat.id, call.message.message_id)
            bot.send_message(uid, f"❌ Rejected.")
    except: pass

def start_bot_process(file_path, name):
    try:
        if name in running_bots:
            try: running_bots[name].terminate()
            except: pass
        proc = subprocess.Popen(['python3', file_path])
        running_bots[name] = proc
    except: pass

def autostart():
    if not os.path.exists('clones'): return
    for uid in os.listdir('clones'):
        upath = f"clones/{uid}"
        if os.path.isdir(upath):
            for f in os.listdir(upath):
                if f.endswith('_info.json'):
                    try:
                        with open(f"{upath}/{f}", 'r') as file: d = json.load(file)
                        if d.get('status') == 'active':
                            start_bot_process(d['file'], d['name'])
                    except: pass

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    threading.Thread(target=monitor_clone_owners, daemon=True).start()
    autostart()
    print("🤖 Main Hosting Bot Running...")
    bot.infinity_polling()
