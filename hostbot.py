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
BOT_TOKEN = "8501688715:AAEgs35fziTuPM3ziwV1i7ZY9fRHnNH7g-0"

# 👑 OWNER ID
OWNER_ID = 6554433221

# 📢 OPTIONAL: Force Sub
FORCE_CHANNEL = "Anysnapupdate" 
FORCE_GROUP = "Anysnapsupport"

# 📦 COMMON LIBRARIES
COMMON_LIBS = [
    "requests", "aiohttp", "pymongo", "pyTelegramBotAPI", 
    "yt-dlp", "bs4", "motor", "pillow", "flask"
]

app = Client("SafeHostBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- 🌐 FAKE WEB SERVER (Render Ke Liye) ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "🤖 Bot is Running Successfully! (Do not close this tab)"

def run_web_server():
    # Render PORT environment variable automatically set karta hai
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
        "🤖 **Python Script Manager (Render Ready)**\n\n"
        "Main Python scripts ko run aur libraries install kar sakta hoon.\n\n"
        "⚙️ **Commands:**\n"
        "• `/install <package>` - Install pip package\n"
        "• `/status` - Check running scripts\n"
        "• `/stop <filename>` - Stop a script\n"
        "• `/logs <filename>` - View logs"
    )

@app.on_message(filters.command("install"))
async def install_command(client, message):
    if not await check_auth(client, message):
        return
    try:
        if len(message.command) < 2:
            await message.reply_text("⚠️ Usage: `/install <package_name>`")
            return
        package = message.command[1]
        msg = await message.reply_text(f"🔄 Installing `{package}`...")
        code, out, err = await install_dependency(package)
        if code == 0:
            await msg.edit(f"✅ **Installed:** `{package}`\n\nOutput:\n`{out[:500]}`")
        else:
            await msg.edit(f"❌ **Error:**\n`{err[:500]}`")
    except Exception as e:
        await message.reply_text(f"Error: {e}")

@app.on_message(filters.command("status"))
async def status(client, message):
    if not await check_auth(client, message):
        return
    active_bots = []
    for file, proc in list(running_processes.items()):
        if proc.returncode is not None:
            del running_processes[file]
        else:
            active_bots.append(f"🟢 `{file}` (PID: {proc.pid})")
    if not active_bots:
        await message.reply_text("💤 No scripts are running.")
    else:
        await message.reply_text("**Running Scripts:**\n\n" + "\n".join(active_bots))

@app.on_message(filters.command("stop"))
async def stop_script(client, message):
    if not await check_auth(client, message):
        return
    try:
        filename = message.command[1]
        if filename in running_processes:
            proc = running_processes[filename]
            proc.terminate()
            del running_processes[filename]
            await message.reply_text(f"🛑 Stopped `{filename}`.")
        else:
            await message.reply_text("❌ Script not found running.")
    except IndexError:
        await message.reply_text("⚠️ Usage: `/stop filename.py`")

@app.on_message(filters.command("logs"))
async def get_logs(client, message):
    if not await check_auth(client, message):
        return
    try:
        filename = message.command[1]
        log_file = f"{filename}.log"
        if os.path.exists(log_file):
            await message.reply_document(log_file, caption=f"📄 Logs: `{filename}`")
        else:
            await message.reply_text("❌ Log file not found.")
    except IndexError:
        await message.reply_text("⚠️ Usage: `/logs filename.py`")

# --- 🚀 FILE HANDLER (Crash Protection) ---

@app.on_message(filters.document)
async def handle_file(client, message):
    if not await check_auth(client, message):
        return

    file_name = message.document.file_name

    # Handle Requirements.txt
    if file_name == "requirements.txt":
        msg = await message.reply_text(f"📥 Downloading `requirements.txt`...")
        path = await message.download()
        await msg.edit("🔄 Installing libraries from requirements...")
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "pip", "install", "-r", path,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode == 0:
            await msg.edit(f"✅ **Dependencies Installed!**\n\nLogs:\n`{stdout.decode()[:500]}`")
        else:
            await msg.edit(f"❌ **Install Failed:**\n`{stderr.decode()[:500]}`")
        os.remove(path)
        return

    # Handle Python Scripts
    if not file_name.endswith(".py"):
        await message.reply_text("⚠️ Only `.py` files or `requirements.txt` allowed.")
        return
    
    if file_name in running_processes:
        await message.reply_text(f"⚠️ `{file_name}` is already running! Use `/stop` first.")
        return

    msg = await message.reply_text(f"📥 Downloading `{file_name}`...")
    path = await message.download()

    # Syntax Check
    try:
        with open(path, "r") as f:
            content = f.read()
            compile(content, path, 'exec')
    except SyntaxError as e:
        await msg.edit(f"❌ **Syntax Error:**\nLine {e.lineno}: {e.msg}")
        os.remove(path)
        return
    except Exception as e:
        await msg.edit(f"❌ **Error:** {e}")
        return

    # Run
    try:
        log_out = open(f"{file_name}.log", "w")
        proc = await asyncio.create_subprocess_exec(
            sys.executable, path, stdout=log_out, stderr=log_out
        )
        await msg.edit("⏳ **Checking health (3s)...**")
        await asyncio.sleep(3)
        
        if proc.returncode is not None:
            log_out.close()
            error_msg = "Unknown Error"
            if os.path.exists(f"{file_name}.log"):
                with open(f"{file_name}.log", "r") as f:
                    error_msg = f.read()[-1000:]
            await msg.edit(f"❌ **Crashed:**\n`{error_msg}`")
            if file_name in running_processes: del running_processes[file_name]
        else:
            running_processes[file_name] = proc
            await msg.edit(f"✅ **Running:** `{file_name}`\nPID: `{proc.pid}`")

    except Exception as e:
        await msg.edit(f"❌ **System Error:** {e}")

# --- 🏁 STARTUP ---
async def pre_install():
    print("📦 Checking common libraries...")
    for lib in COMMON_LIBS:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
        except Exception:
            pass

if __name__ == "__main__":
    # 1. Start Flask Server in Background Thread
    print("🌍 Starting Web Server for Render...")
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()

    # 2. Update Pip
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    except:
        pass
    
    # 3. Install Libs
    loop = asyncio.get_event_loop()
    loop.run_until_complete(pre_install())
    
    # 4. Start Bot
    print("🤖 Bot Started Successfully...")
    app.run()
