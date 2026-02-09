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
SESSION_STRING = "BQI5Xz4AronAZ7V9PIFgqmRM2DaXCgjVJrmVEJlOi_cc4K1OWuAqNx8YHuaFRL5hxjSIlod4-c264ReWY2Tv3LuPTufyuH-SYe9ZLKzjgeNgXu9B9ZkU2WWrpuIo_Cl7_k5xO7vM_pvIoP6Q1plOu_mpGh3A2NicHzG5hUFAPVNy7AY8UQf5wC-erUyChpEPIhs5nniAvbojHoBZXewVSyGhJKsmX2ifmOIkb0UUHvQqAavnEudmZWavLSl5h4ob-09hkb0PJoX4qLQus4RTt-OFIEer-40v9k17ktdfN1ayWvRLzCq66MQRH45IB2xrQxd1KQPiozqOI5HEP2WOcmErhT9VdAAAAAH3kmItAA"

TARGET_BOT = "DT_USERTONUMBOT"
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

        # --- FINAL FIXED WAIT LOOP ---
        for attempt in range(25): 
            await asyncio.sleep(2) 
            try:
                async for log in client.get_chat_history(TARGET_BOT, limit=1):
                    if log.id == sent_req.id: continue

                    text_content = (log.text or log.caption or "").lower()
                    
                    # 1. SUCCESS CHECK: Kya message me '{' bracket hai? (JSON Detection)
                    # Yeh sabse important check hai. Agar yeh mil gaya, to loop tod do.
                    if "{" in text_content or "success" in text_content or log.document:
                        target_response = log
                        break
                    
                    # 2. WAIT CHECK: Kya message me "wait" ya "looking" likha hai?
                    # Agar haan, to continue karo (wait karo).
                    ignore_words = [
                        "wait", "processing", "searching", "scanning", 
                        "generating", "loading", "checking", 
                        "looking up"
                    ]

                    if any(word in text_content for word in ignore_words):
                        if f"Attempt {attempt+1}" not in status_msg.text:
                            await status_msg.edit(f"⏳ **Fetching Data... (Attempt {attempt+1})**")
                        continue 
                    
                    # 3. OTHER: Agar na JSON hai, na Wait message hai (Maybe error text)
                    # To ise hi result maan lo.
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

        # --- SMART JSON PARSER ---
        all_records = []
        try:
            # 1. Try to parse as Clean JSON
            # Remove Markdown code blocks if present
            clean_json_text = raw_text.replace("```json", "").replace("```", "").strip()
            
            # Extract JSON part using Regex (Find content between first { and last })
            json_match = re.search(r'\{.*\}', clean_json_text, re.DOTALL)
            if json_match:
                clean_json_text = json_match.group(0)
            
            data_obj = json.loads(clean_json_text)
            
            # Logic to handle specific structure: {"data": [{"results": [...]}]}
            if "data" in data_obj and isinstance(data_obj["data"], list):
                if "results" in data_obj["data"][0]:
                    all_records = data_obj["data"][0]["results"]
                else:
                    all_records = data_obj["data"]
            elif "results" in data_obj:
                all_records = data_obj["results"]
            else:
                all_records = [data_obj] if isinstance(data_obj, dict) else data_obj
                
        except (json.JSONDecodeError, AttributeError):
            # 2. Fallback: Line-by-Line Parsing (Old Method)
            lines = raw_text.splitlines()
            current_record = {}
            for line in lines:
                clean_line = line.strip()
                if not clean_line or any(x in clean_line for x in ["@DuXxZx_info", "Designed & Powered", "Scanning Vehicle", "JSON", "```"]):
                    continue
                if ":" in clean_line:
                    try:
                        p = clean_line.split(":", 1)
                        k, v = p[0].strip().strip('"'), p[1].strip().strip('",')
                        if k in current_record:
                            all_records.append(current_record)
                            current_record = {}
                        current_record[k] = v
                    except: pass
            if current_record: all_records.append(current_record)

        # Output Generation
        if all_records:
            json_output = json.dumps(all_records, indent=4, ensure_ascii=False)
        else:
            # If parsing failed completely, show raw text
            json_output = raw_text

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
