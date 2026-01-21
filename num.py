import os
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.errors import UserNotParticipant
from flask import Flask
from threading import Thread

# --- FAKE WEB SERVER FOR RENDER (KEEP ALIVE) ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "⚡ ANYSNAP BOT IS RUNNING ON RENDER ⚡"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# --- CONFIGURATION ---
API_ID = 37314366
API_HASH = "bd4c934697e7e91942ac911a5a287b46"

# 🆕 UPDATED SESSION STRING
SESSION_STRING = "BQI5Xz4AfVucFjjAZHS29EV-ZnLy5sZK3dpFVccZI8kTZcGrscEEJNvPdWlEfUEOF9Nsr4dGWZlbzi5f6Axk4Jb9CD9sPqIq09m2RG56CiOZ3ke8umbehZB4dbwcUSV98EKfgr717Yyv1fEWGtk1Oqvk3vHZR2ZyVnhjfu73KrMEKvuokXUFBOXf8RLfxofyN0Ym-FyP8VZLLavcj-ubKwZLbZRw0TzBAoWAd5E8cHKfykPWdxwQZcfGNGAPjkpeSqFXbjZrqn_RVTRggC8iZamVz__4IRrhoLQGwuW-Laidb7GnZTnciiu1dNfGA64VbTVr6N-X6a5-_Mrhd5DZ0-9n_tQcrAAAAAGc59H6AA"

TARGET_BOT = "Random_insight69_bot"
NEW_FOOTER = "⚡ Designed & Powered by @MAGMAxRICH"

# --- 🔐 SECURITY SETTINGS ---
# Allowed Group ID
ALLOWED_GROUPS = [-1003387459132] 

# Force Sub Channels
FSUB_CONFIG = [
    {"username": "Anysnapupdate", "link": "https://t.me/Anysnapupdate"},
    {"username": "Anysnapsupport", "link": "https://t.me/Anysnapsupport"}
]

app = Client("anysnap_secure_bot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# --- HELPER: CHECK IF USER JOINED ---
async def check_user_joined(client, user_id):
    missing = False
    for ch in FSUB_CONFIG:
        try:
            member = await client.get_chat_member(ch["username"], user_id)
            if member.status in [enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.BANNED]:
                missing = True
                break
        except UserNotParticipant:
            missing = True
            break
        except Exception:
            pass 
    return not missing 

# --- DASHBOARD ---
@app.on_message(filters.command(["start", "help", "menu"], prefixes="/") & (filters.private | filters.chat(ALLOWED_GROUPS)))
async def show_dashboard(client, message):
    
    if not await check_user_joined(client, message.from_user.id):
        return await message.reply_text(
            "🚫 **Access Denied!**\n\n"
            "Bot use karne ke liye pehle niche diye gaye channels join karein:\n\n"
            "📢 **[Click to Join Updates](https://t.me/Anysnapupdate)**\n"
            "👥 **[Click to Join Support](https://t.me/Anysnapsupport)**\n\n"
            "__Join karne ke baad dubara /start dabayein.__",
            disable_web_page_preview=True
        )

    text = (
        "📖 **ANYSNAP BOT DASHBOARD**\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📢 **Updates:** [Join Here](https://t.me/Anysnapupdate)\n"
        "👥 **Support:** [Join Here](https://t.me/Anysnapsupport)\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "🔍 **Lookup Services:**\n"
        "📱 `/num [number]`\n🚗 `/vehicle [plate]`\n🆔 `/aadhar [uid]`\n"
        "👨‍👩‍👧‍👦 `/familyinfo [uid]`\n🔗 `/vnum [plate]`\n💸 `/fam [id]`\n📨 `/sms [number]`\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "⚡ **Designed & Powered by @MAGMAxRICH**"
    )
    await message.reply_text(text, disable_web_page_preview=True)

# --- MAIN LOGIC ---
@app.on_message(filters.command(["num", "vehicle", "aadhar", "familyinfo", "vnum", "fam", "sms"], prefixes="/") & (filters.private | filters.chat(ALLOWED_GROUPS)))
async def process_request(client, message):
    
    if not await check_user_joined(client, message.from_user.id):
        return await message.reply_text(
            "🚫 **Access Denied!**\n\n"
            "Result dekhne ke liye pehle join karein:\n\n"
            "➡️ **[Join Update Channel](https://t.me/Anysnapupdate)**\n"
            "➡️ **[Join Support Group](https://t.me/Anysnapsupport)**\n\n"
            f"__Join karne ke baad wapas `/{message.command[0]}` bhejein.__",
            disable_web_page_preview=True
        )

    if len(message.command) < 2:
        return await message.reply_text(f"❌ **Data Missing!**\nUsage: `/{message.command[0]} <value>`")

    status_msg = await message.reply_text(f"🔍 **Searching via ANYSNAP...**")
    
    try:
        sent_req = await client.send_message(TARGET_BOT, message.text)
        
        target_response = None
        
        # --- ZIDDI WAIT LOOP ---
        for attempt in range(15):
            await asyncio.sleep(2.5) 
            async for log in client.get_chat_history(TARGET_BOT, limit=1):
                if log.id == sent_req.id: continue
                
                text_content = (log.text or log.caption or "").lower()
                ignore_words = ["wait", "processing", "searching", "scanning", "generating", "loading", "checking"]
                
                if any(word in text_content for word in ignore_words):
                    await status_msg.edit(f"⏳ **Fetching Data... (Attempt {attempt+1})**")
                    continue 
                
                target_response = log
                break 
            
            if target_response: break
        
        if not target_response:
            await status_msg.edit("❌ **Timeout:** Target bot ne final result nahi diya.")
            return

        # --- Data Handling ---
        raw_text = ""
        if target_response.document:
            await status_msg.edit("📂 **Downloading File...**")
            file_path = await client.download_media(target_response)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                raw_text = f.read()
            os.remove(file_path)
        elif target_response.photo:
            raw_text = target_response.caption or ""
        elif target_response.text:
            raw_text = target_response.text

        if not raw_text or len(raw_text.strip()) < 5:
            await status_msg.edit("❌ **No Data Found**")
            return

        # --- Branding ---
        lines = raw_text.splitlines()
        clean_lines = []
        for line in lines:
            if "@DuXxZx_info" not in line and "Designed & Powered" not in line and "Scanning Vehicle" not in line:
                clean_lines.append(line)
        
        main_body = "\n".join(clean_lines).strip()
        final_output = f"{main_body}\n\n{NEW_FOOTER}"

        if len(final_output) > 4000:
            await message.reply_text(final_output[:4000])
            await message.reply_text(final_output[4000:])
        else:
            await message.reply_text(final_output)
            
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit(f"❌ **Error:** {str(e)}")

print("🚀 Starting Web Server & Bot...")
keep_alive()  # <--- Starts the Fake Web Server
app.run()