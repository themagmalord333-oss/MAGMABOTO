import sys
import asyncio
import time
import os
import subprocess
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant

# --- ⚙️ CONFIGURATION ⚙️ ---
API_ID = 37314366
API_HASH = "bd4c934697e7e91942ac911a5a287b46"
BOT_TOKEN = "8501688715:AAEDg3xQbd4P0H4jm9mxSNQxhYmavt2hKYc"

# 👑 OWNER ID (Supreme Control)
OWNER_ID = 8081343902

# 📢 OPTIONAL: Force Sub
FORCE_CHANNEL = "Anysnapupdate" 
FORCE_GROUP = "Anysnapsupport"

# 📦 ULTIMATE LIBRARY LIST (Ye sab auto-install ho jayengi)
COMMON_LIBS = [
    # Telegram Libs
    "pyrogram", "telethon", "pyTelegramBotAPI", "aiogram",
    # Network & Requests
    "requests", "aiohttp", "httpx", "bs4", "beautifulsoup4", "html5lib", "lxml",
    # Database
    "pymongo", "motor", "redis", "sqlalchemy",
    # Media & YouTube
    "yt-dlp", "pafy", "pillow", "opencv-python-headless", "pydub", "ffmpeg-python",
    # Utils & Math
    "numpy", "pandas", "schedule", "pytz", "psutil", "emoji", "qrcode",
    # Hacking/Security (Common usage)
    "colorama", "fake-useragent", "dnspython",
    # Web
    "flask", "fastapi", "uvicorn"
]

app = Client("SafeHostBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- 🌐 FAKE WEB SERVER (For Render 24/7) ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "🚀 Bot is Running in Beast Mode!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

# --- 💾 PROCESS MANAGER ---
running_processes = {}

# --- 🛠️ HELPER FUNCTIONS ---
async def install_dependency(package_name):
    process = await asyncio.create_subprocess_exec(
        sys.executable, "-m", "pip", "install", package_name,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return process.returncode, stdout.decode(), stderr.decode()

async def check_auth(client, message):
    user_id = message.from_user.id
    if user_id == OWNER_ID:
        return True
    if FORCE_CHANNEL and FORCE_GROUP:
        try:
            await client.get_chat_member(FORCE_CHANNEL, user_id)
            await client.get_chat_member(FORCE_GROUP, user_id)
            return True
        except UserNotParticipant:
            btn = InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FORCE_CHANNEL}")],
                [InlineKeyboardButton("👥 Join Group", url=f"https://t.me/{FORCE_GROUP}")],
                [InlineKeyboardButton("✅ Try Again", url=f"https://t.me/{client.me.username}?start=start")]
            ])
            await message.reply_text("🔒 **Access Denied:** Please join our channels first.", reply_markup=btn)
            return False
        except Exception:
            return True
    return True

# --- 🕹️ COMMANDS ---

@app.on_message(filters.command("start"))
async def start(client, message):
    if not await check_auth(client, message):
        return
    await message.reply_text(
        "⚡ **Fast Hosting Bot**\n\n"
        "Send me any `.py` file. I will run it instantly.\n"
        "No checks. No questions.\n\n"
        "🛠 **Commands:** `/status`, `/stop <file>`, `/logs <file>`, `/killall`"
    )

@app.on_message(filters.command("ping"))
async def ping(client, message):
    start = time.time()
    msg = await message.reply_text("⚡")
    end = time.time()
    await msg.edit(f"⚡ **Speed:** `{round((end - start) * 1000)}ms`")

@app.on_message(filters.command("install"))
async def install_command(client, message):
    if not await check_auth(client, message):
        return
    try:
        if len(message.command) < 2: return
        package = message.command[1]
        msg = await message.reply_text(f"📥 Installing `{package}`...")
        code, out, err = await install_dependency(package)
        if code == 0: await msg.edit(f"✅ Installed `{package}`")
        else: await msg.edit(f"❌ Error:\n`{err[:500]}`")
    except: pass

@app.on_message(filters.command("status"))
async def status(client, message):
    if not await check_auth(client, message):
        return
    active = [f"🟢 `{f}` (PID: {p.pid})" for f, p in running_processes.items() if p.returncode is None]
    await message.reply_text(f"**Running Files:**\n\n" + "\n".join(active) if active else "💤 No files running.")

@app.on_message(filters.command("stop"))
async def stop_script(client, message):
    if not await check_auth(client, message):
        return
    try:
        filename = message.command[1]
        if filename in running_processes:
            running_processes[filename].terminate()
            del running_processes[filename]
            await message.reply_text(f"🛑 Killed `{filename}`")
        else:
            await message.reply_text("❌ Not running.")
    except:
        await message.reply_text("⚠️ Use: `/stop filename.py`")

@app.on_message(filters.command("logs"))
async def get_logs(client, message):
    if not await check_auth(client, message):
        return
    try:
        filename = message.command[1]
        if os.path.exists(f"{filename}.log"):
            await message.reply_document(f"{filename}.log", caption=f"📄 `{filename}`")
        else:
            await message.reply_text("❌ No logs.")
    except:
        pass

@app.on_message(filters.command("killall") & filters.user(OWNER_ID))
async def kill_all(client, message):
    for f, p in list(running_processes.items()):
        p.terminate()
        del running_processes[f]
    await message.reply_text("☠️ **All processes killed.**")

# --- 🚀 DIRECT RUNNER (No Checks) ---
@app.on_message(filters.document)
async def handle_file(client, message):
    if not await check_auth(client, message):
        return

    file_name = message.document.file_name

    # Requirements.txt support
    if file_name == "requirements.txt":
        msg = await message.reply_text("📥 Installing requirements...")
        path = await message.download()
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "pip", "install", "-r", path,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
        await msg.edit("✅ Done.")
        return

    if not file_name.endswith(".py"):
        await message.reply_text("⚠️ Send `.py` file only.")
        return

    if file_name in running_processes:
        await message.reply_text("⚠️ Already running. Stop it first.")
        return

    msg = await message.reply_text(f"🚀 **Launching `{file_name}`...**")
    path = await message.download()

    # --- DIRECT EXECUTION (No Syntax Check) ---
    try:
        log_out = open(f"{file_name}.log", "w")
        proc = await asyncio.create_subprocess_exec(
            sys.executable, path, stdout=log_out, stderr=log_out
        )
        
        # Sirf 2 second wait karega crash check ke liye
        await asyncio.sleep(2)
        
        if proc.returncode is not None:
            log_out.close()
            # Read error just to show WHY it failed (script fault)
            err = open(f"{file_name}.log").read()[-800:] if os.path.exists(f"{file_name}.log") else "Unknown"
            await msg.edit(f"❌ **Script Crashed:**\n`{err}`")
        else:
            running_processes[file_name] = proc
            await msg.edit(f"✅ **Hosted:** `{file_name}`\n🆔 PID: `{proc.pid}`")

    except Exception as e:
        await msg.edit(f"❌ System Error: {e}")

# --- 🏁 PRE-INSTALL ALL LIBS ---
async def pre_install():
    print("📦 Installing ULTIMATE libraries...")
    # Ek saath install karega taaki fast ho
    pip_cmd = [sys.executable, "-m", "pip", "install"] + COMMON_LIBS
    try:
        process = await asyncio.create_subprocess_exec(
            *pip_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        print("✅ All Libraries Installed!")
    except:
        print("⚠️ Some libs failed, but continuing...")

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(pre_install())
    
    app.run()
