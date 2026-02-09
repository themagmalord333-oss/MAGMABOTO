import os
import asyncio
import json
import logging
import re
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
SESSION_STRING = "BQI5Xz4ATohe7TzEthBJV163cxqpZqg_Za3jR19G_o9TwJ3_uYacTCM6VUGOTvcLGEeM2RtMUuacEfZ7GteCqpAbvkznZ-VPVbYm93KIpWl0m25xpAmMJgfP6v-B4UJeswwS9F8vTyRB2FfGkXfk9oGcxo_RQy1MdABUnn6QUsf91rKvmmwXgTiqqc8zCgm-8amZdmt0eVJh90IN9KX_nuNxiZAYR5fmp057aDBYarvKeNDctusJWBXF50Xr6BIkZDe3PBkLe33BQLwYEeeGesxrxkdom5eBuC3NESlDu0AExdF1Sy270Q0DS9qdGzLYmJVqscGg-GwjLjACCCFOaskdcJH1zAAAAAGc59H6AA"

TARGET_BOT = "Random_insight69_bot"
NEW_FOOTER = "⚡ Designed & Powered by @MAGMAxRICH"

# --- 🔐 SECURITY SETTINGS ---
# Jis group me bot command accept karega
ALLOWED_GROUPS = [-1003387459132] 

# FSUB (Force Subscribe) List
# Note: Private Channel ID (-100...) use kiya hai. Bot ko waha ADMIN bana dena.
FSUB_CONFIG = [
    {"chat_id": -1003387459132, "link": "https://t.me/+wZ9rDQC5fkYxOWJh"},
    {"chat_id": "Anysnapsupport", "link": "https://t.me/Anysnapsupport"}
]

app = Client("anysnap_secure_bot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# --- HELPER: CHECK IF USER JOINED ---
async def check_user_joined(client, user_id):
    missing = False
    for ch in FSUB_CONFIG:
        try:
            # chat_id can be int (for private) or str (for username)
            member = await client.get_chat_member(ch["chat_id"], user_id)
            if member.status in [enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.BANNED]:
                missing = True
                break
        except UserNotParticipant:
            missing = True
            break
        except (PeerIdInvalid, ChannelInvalid, KeyError):
            # Agar bot admin nahi hai ya ID galat hai to ignore karke pass kar dete hain (Risk handling)
            pass
        except Exception:
            pass 
    return not missing 

# --- DASHBOARD ---
@app.on_message(filters.command(["start", "help", "menu"], prefixes="/") & (filters.private | filters.chat(ALLOWED_GROUPS)))
async def show_dashboard(client, message):
    try:
        # Fsub Logic in Dashboard
        if not await check_user_joined(client, message.from_user.id):
            # Buttons generate karna based on config
            buttons_text = ""
            for ch in FSUB_CONFIG:
                buttons_text += f"➡️ **[Join Channel]({ch['link']})**\n"
            
            return await message.reply_text(
                "🚫 **Access Denied!**\n\n"
                "Bot use karne ke liye pehle niche diye gaye channels join karein:\n\n"
                f"{buttons_text}\n"
                "__Join karne ke baad dubara /start dabayein.__",
                disable_web_page_preview=True
            )

        text = (
            "📖 **ANYSNAP BOT DASHBOARD**\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "📢 **Updates:** [Join Here](https://t.me/+wZ9rDQC5fkYxOWJh)\n"
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
        # 1. Permission Check
        if not await check_user_joined(client, message.from_user.id):
            buttons_text = ""
            for ch in FSUB_CONFIG:
                buttons_text += f"➡️ **[Join Channel]({ch['link']})**\n"

            return await message.reply_text(
                "🚫 **Access Denied!**\n\n"
                "Result dekhne ke liye pehle join karein:\n\n"
                f"{buttons_text}\n"
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

        # --- SMART WAIT LOOP ---
        for attempt in range(30): 
            await asyncio.sleep(2) 
            try:
                async for log in client.get_chat_history(TARGET_BOT, limit=1):
                    if log.id == sent_req.id: continue

                    text_content = (log.text or log.caption or "").lower()
                    
                    # 1. IGNORE LIST
                    ignore_words = [
                        "wait", "processing", "searching", "scanning", 
                        "generating", "loading", "checking", 
                        "looking up", "uploading", "sending file", 
                        "attaching", "sending"
                    ]

                    if any(word in text_content for word in ignore_words) and not log.document:
                        if f"Attempt {attempt+1}" not in status_msg.text:
                            await status_msg.edit(f"⏳ **Fetching Data... (Attempt {attempt+1})**")
                        continue 
                    
                    # 2. SUCCESS CHECK
                    if log.document or "{" in text_content or "success" in text_content:
                        target_response = log
                        break
                    
                    # 3. Fallback
                    target_response = log
                    break
                    
            except Exception as e:
                logger.error(f"Error fetching history: {e}")
            
            if target_response: break

        if not target_response:
            # UPDATED: Timeout ki jagah No Data Found
            await status_msg.edit("❌ **No Data Found**")
            return

        # --- DATA EXTRACTION & CLEANING ---
        raw_text = ""
        
        # Scenario A: Result is a FILE
        if target_response.document:
            await status_msg.edit("📂 **Downloading Result File...**")
            try:
                file_path = await client.download_media(target_response)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    raw_text = f.read()
                os.remove(file_path)
            except Exception as e:
                await status_msg.edit(f"❌ **File Error:** {e}")
                return
                
        # Scenario B: Result is TEXT or CAPTION
        elif target_response.text:
            raw_text = target_response.text
        elif target_response.caption:
            raw_text = target_response.caption

        if not raw_text or len(raw_text.strip()) < 2:
            await status_msg.edit("❌ **No Data Found**")
            return

        # --- REMOVE UNWANTED TEXT ---
        raw_text = raw_text.replace("⚡ Designed & Powered by @DuXxZx_info", "")
        raw_text = raw_text.replace("@DuXxZx_info", "")
        
        # --- SMART JSON PARSING ---
        final_output = raw_text 
        
        try:
            clean_text = raw_text.replace("```json", "").replace("```", "").strip()
            json_match = re.search(r'\{.*\}', clean_text, re.DOTALL)
            
            if json_match:
                parsed_data = json.loads(json_match.group(0))
                
                results = []
                if "data" in parsed_data:
                    data_part = parsed_data["data"]
                    if isinstance(data_part, list) and len(data_part) > 0:
                        if "results" in data_part[0]:
                            results = data_part[0]["results"]
                        else:
                            results = data_part
                    elif isinstance(data_part, dict):
                        if "results" in data_part:
                            results = data_part["results"]
                        else:
                            results = [data_part]
                elif "results" in parsed_data:
                    results = parsed_data["results"]
                else:
                    results = parsed_data
                
                final_output = json.dumps(results, indent=4, ensure_ascii=False)
        except Exception:
            pass

        # --- SENDING RESULT ---
        formatted_msg = f"```json\n{final_output}\n```\n\n{NEW_FOOTER}"
        
        await status_msg.delete()

        if len(formatted_msg) > 4000:
            chunks = [formatted_msg[i:i+4000] for i in range(0, len(formatted_msg), 4000)]
            for chunk in chunks:
                await message.reply_text(chunk)
                await asyncio.sleep(1) 
        else:
            msg = await message.reply_text(formatted_msg)
            await asyncio.sleep(60)
            try: await msg.delete()
            except: pass

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
