import os
import asyncio
import json
import logging
from threading import Thread
from flask import Flask
from pyrogram import Client, filters, enums, idle
from pyrogram.errors import UserNotParticipant, PeerIdInvalid, ChannelInvalid

# --- LOGGING SETUP ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FAKE WEBSITE FOR RENDER ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "⚡ ANYSNAP Bot is Running Successfully!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# --- CONFIGURATION ---
API_ID = 37314366
API_HASH = "bd4c934697e7e91942ac911a5a287b46"

# SESSION STRING
SESSION_STRING = "BQI5Xz4AgSc0H1AqRtF36ztzS0mIwEg3TszfSM4jL-64WvIy5RUvfhviMlQXU7cz3x7jsK7jcnR-_tJ86zSrUXzfuQHXWHjv7vUOEfBZwW1nb-R3ELMKYYoTqlXCiX0q6tf1Aj5PD_ZxCcx3hmi-fkzbxWrSxTI8Z6z5dYDhq85kRE4SgOFtXN9T_85Enn39Wx74BuUIVq2kXlDB_sdPUn89lgmmjLluLjK-pcms2iqAh3n1C5PEdGO7I_qGF5M7ioJxnpidMi0w60a8Bord_TxCcQffU7R_tQ2eALIOM1vtajUQyN7YVDzX_f21jA6BzZkhe-lYEudfhnTieoZ0pbrFYUFbnwAAAAFJSgVkAA"

TARGET_BOT = "Random_insight69_bot"
NEW_FOOTER = "⚡ Designed & Powered by @MAGMAxRICH"

# --- 🔐 SECURITY SETTINGS ---
ALLOWED_GROUPS = [-1003387459132] 

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
        except (PeerIdInvalid, ChannelInvalid, KeyError):
            pass
        except Exception:
            pass 
    return not missing 

# --- DASHBOARD ---
@app.on_message(filters.command(["start", "help", "menu"], prefixes="/") & (filters.private | filters.chat(ALLOWED_GROUPS)))
async def show_dashboard(client, message):
    try:
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
    except Exception as e:
        logger.error(f"Error in dashboard: {e}")

# --- MAIN LOGIC ---
@app.on_message(filters.command(["num", "vehicle", "aadhar", "familyinfo", "vnum", "fam", "sms"], prefixes="/") & (filters.private | filters.chat(ALLOWED_GROUPS)))
async def process_request(client, message):
    
    try:
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
        except PeerIdInvalid:
             await status_msg.edit("❌ **Error:** Target Bot ID invalid. Userbot must start @Random_insight69_bot first.")
             return
        except Exception as e:
            await status_msg.edit(f"❌ **Request Error:** {e}")
            return

        target_response = None
        
        # --- WAIT LOOP ---
        for attempt in range(15):
            await asyncio.sleep(2.5) 
            try:
                async for log in client.get_chat_history(TARGET_BOT, limit=1):
                    if log.id == sent_req.id: continue
                    
                    text_content = (log.text or log.caption or "").lower()
                    ignore_words = ["wait", "processing", "searching", "scanning", "generating", "loading", "checking"]
                    
                    if any(word in text_content for word in ignore_words):
                        if f"Attempt {attempt+1}" not in status_msg.text:
                            await status_msg.edit(f"⏳ **Fetching Data... (Attempt {attempt+1})**")
                        continue 
                    
                    target_response = log
                    break 
            except Exception as e:
                logger.error(f"Error fetching history: {e}")
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

        # --- ADVANCED JSON PARSING (Fix for Multiple Results) ---
        lines = raw_text.splitlines()
        
        all_records = []      # List to hold all results
        current_record = {}   # Dictionary for the current result being processed
        
        for line in lines:
            clean_line = line.strip()
            
            # Skip junk lines
            if not clean_line or any(x in clean_line for x in ["@DuXxZx_info", "Designed & Powered", "Scanning Vehicle"]):
                continue

            # Check if this line is a Key: Value pair
            if ":" in clean_line:
                try:
                    parts = clean_line.split(":", 1)
                    key = parts[0].strip().replace("*", "").replace("`", "")
                    value = parts[1].strip().replace("*", "").replace("`", "")
                    
                    # LOGIC CHANGE: 
                    # Agar key pehle se current_record me hai (jaise Name dobara aaya),
                    # iska matlab naya record shuru ho gaya hai.
                    if key in current_record:
                        all_records.append(current_record) # Save old record
                        current_record = {} # Start new record
                    
                    current_record[key] = value
                except:
                    # Formatting error, maybe ignore or add to separate list
                    pass
            elif "Record" in clean_line or "---" in clean_line:
                 # Explicit separator detection (Backup logic)
                 if current_record:
                     all_records.append(current_record)
                     current_record = {}

        # Add the last remaining record
        if current_record:
            all_records.append(current_record)

        # Result Generation
        if not all_records:
            # Fallback agar parsing fail hui to raw text dikha dega JSON me
            json_output = json.dumps({"Raw Data": lines}, indent=4, ensure_ascii=False)
        else:
            # Agar sirf ek result hai to list nahi, direct dict dikhaye (User preference)
            # Ya user chahta hai hamesha list rahe? Safer is List.
            json_output = json.dumps(all_records, indent=4, ensure_ascii=False)

        # Formatting: JSON Code Block + Normal Text Footer
        final_message_text = f"```json\n{json_output}\n```\n\n{NEW_FOOTER}"

        await status_msg.delete()

        # --- SENDING RESULT ---
        sent_result_msg = None
        if len(final_message_text) > 4000:
            sent_result_msg = await message.reply_text(final_message_text[:4000])
            await message.reply_text(final_message_text[4000:])
        else:
            sent_result_msg = await message.reply_text(final_message_text)
            
        # --- AUTO DELETE (30s) ---
        if sent_result_msg:
            await asyncio.sleep(30)
            try:
                await sent_result_msg.delete()
            except Exception:
                pass

    except Exception as e:
        try:
            await status_msg.edit(f"❌ **Error:** {str(e)}")
        except:
            pass

# --- START SERVER & BOT ---
async def start_bot():
    print("🚀 Starting Web Server...")
    keep_alive() 
    print("🚀 Starting Pyrogram Client...")
    await app.start()
    print("✅ Bot is Online!")
    await idle()
    await app.stop()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())