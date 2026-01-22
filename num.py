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
    # Render assigns a port via the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    # '0.0.0.0' is crucial for Render to detect the port
    web_app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# --- CONFIGURATION ---
API_ID = 37314366
API_HASH = "bd4c934697e7e91942ac911a5a287b46"

# 🆕 UPDATED SESSION STRING (Jo aapne diya)
SESSION_STRING = "BQI5Xz4AGxfBeV-3jaxgwyugowiDkIjvDhk8x3QhrEFBaJOdieKytrqqYVK_mpdNG2EiODrwjkyZBdEzICVyLsnlfYBfjJQ19dJJF4KnlWjHXWFrWUUnTNSQb7_HTCclpShBy5WF2vMpRcEKZxFkwgBBt30_LyA-Fb5hR0y-wM33oDvY6CB5-Ored-uQbU-srNHTwaxTOIcXp77aNANv5U6dHTmvvF8YtAX4U5JtakBZowSEUxgXk3axQlF4g44SSdKU4Sp_nCitcvzfxkrMCARl0r2_8iuJXUSS3jsx-V_AyjDWG7E8WTppwkf9BerFM-eV2iEq3AHK22sESU5W0QXYmHbUFgAAAAGc59H6AA"

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
        # Check Force Sub
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
        
        # --- SEND REQUEST ---
        try:
            sent_req = await client.send_message(TARGET_BOT, message.text)
        except PeerIdInvalid:
             await status_msg.edit("❌ **Error:** Target Bot ID invalid. Make sure the Userbot account has started @Random_insight69_bot.")
             return
        except Exception as e:
            await status_msg.edit(f"❌ **Request Error:** {e}")
            return

        target_response = None
        
        # --- ZIDDI WAIT LOOP ---
        for attempt in range(15):
            await asyncio.sleep(2.5) 
            try:
                async for log in client.get_chat_history(TARGET_BOT, limit=1):
                    if log.id == sent_req.id: continue
                    
                    text_content = (log.text or log.caption or "").lower()
                    ignore_words = ["wait", "processing", "searching", "scanning", "generating", "loading", "checking"]
                    
                    if any(word in text_content for word in ignore_words):
                        # Edit only if text is different to avoid API flood
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

        # --- JSON Conversion & Branding ---
        lines = raw_text.splitlines()
        data_dict = {}
        info_lines = []

        for line in lines:
            clean_line = line.strip()
            # Branding Removal
            if "@DuXxZx_info" in clean_line or "Designed & Powered" in clean_line or "Scanning Vehicle" in clean_line or not clean_line:
                continue
            
            # Key-Value Logic
            if ":" in clean_line:
                try:
                    parts = clean_line.split(":", 1)
                    key = parts[0].strip().replace("*", "").replace("`", "")
                    value = parts[1].strip().replace("*", "").replace("`", "")
                    data_dict[key] = value
                except:
                    info_lines.append(clean_line)
            else:
                info_lines.append(clean_line)

        if info_lines:
            data_dict["Additional Info"] = info_lines
        
        data_dict["Credits"] = NEW_FOOTER

        # JSON Output
        json_output = json.dumps(data_dict, indent=4, ensure_ascii=False)
        final_message_text = f"```json\n{json_output}\n```"

        await status_msg.delete()

        # --- SENDING RESULT ---
        sent_result_msg = None
        if len(final_message_text) > 4000:
            sent_result_msg = await message.reply_text(final_message_text[:4000])
            await message.reply_text(final_message_text[4000:])
        else:
            sent_result_msg = await message.reply_text(final_message_text)
            
        # --- AUTO DELETE LOGIC (30 Seconds) ---
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

# --- START SERVER & BOT SAFELY ---
async def start_bot():
    print("🚀 Starting Web Server...")
    keep_alive() # Start Flask first (Fake Website)
    print("🚀 Starting Pyrogram Client...")
    await app.start()
    print("✅ Bot is Online!")
    await idle()
    await app.stop()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
