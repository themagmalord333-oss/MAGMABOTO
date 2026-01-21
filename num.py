import sys
import asyncio
import time
import os
from aiohttp import web  # Render ke liye zaroori
from pyrogram import Client, filters, idle, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import UserNotParticipant, ChatAdminRequired, UsernameNotOccupied

# --- ⚙️ SYSTEM CONFIGURATION ⚙️ ---
API_ID = 37314366
API_HASH = "bd4c934697e7e91942ac911a5a287b46"
BOT_TOKEN = "8501688715:AAGfwajpOazHdTNSXTLNV2fft1KMs0uVqtE"

# 👑 OWNER ID (Important for /term command)
OWNER_ID = 8081343902 

# 📢 FORCE SUBSCRIPTION CONFIG
# Note: Bot ko in dono channels/groups mein ADMIN banana zaroori hai!
FORCE_CHANNEL = "Anysnapupdate" 
FORCE_GROUP = "Anysnapsupport"

app = Client("NexusHost", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# System Start Time
BOT_START_TIME = time.time()
running_bots = {}

# --- 🌍 FAKE WEB SERVER (Render Support) ---
async def web_server():
    async def handle(request):
        return web.Response(text="✅ Nexus Host is Running on Render!")

    web_app = web.Application()
    web_app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(web_app)
    await runner.setup()
    # Render PORT environment variable automatically deta hai
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌍 Web Server Started on Port {port}")

# --- 🛠️ PROFESSIONAL HELPERS ---

def get_uptime(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return f"{int(days)}d {int(hours)}h {int(minutes)}m"

async def check_fsub(client: Client, message: Message) -> bool:
    if message.from_user.id == OWNER_ID:
        return True

    try:
        await client.get_chat_member(FORCE_CHANNEL, message.from_user.id)
        await client.get_chat_member(FORCE_GROUP, message.from_user.id)
        return True
    except UserNotParticipant:
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Join Update Channel", url=f"https://t.me/{FORCE_CHANNEL}")],
            [InlineKeyboardButton("👥 Join Support Group", url=f"https://t.me/{FORCE_GROUP}")],
            [InlineKeyboardButton("✅ Verify Access", url=f"https://t.me/{client.me.username}?start=start")]
        ])
        await message.reply_text(
            "🔒 **Access Restricted**\n\n"
            "Nexus Hosting use karne ke liye neeche diye gaye channels join karein.",
            reply_markup=btn
        )
        return False
    except Exception as e:
        await message.reply_text(f"⚠️ **Error:** Bot ko Check karein ki wo Channel/Group me Admin hai ya nahi.\nError: `{e}`")
        return False

# --- 🚀 CORE COMMANDS ---

@app.on_message(filters.command("start"))
async def start_cmd(client, message):
    if not await check_fsub(client, message):
        return

    uptime = get_uptime(int(time.time() - BOT_START_TIME))
    
    txt = (
        f"👋 **Hello, {message.from_user.mention}.**\n\n"
        "**Welcome to Nexus Hosting Environment.**\n"
        "Main aapki Python scripts ko 24/7 host kar sakta hoon.\n\n"
        "📊 **System Stats:**\n"
        f"├ ⏳ **Uptime:** `{uptime}`\n"
        f"├ 🟢 **Active Bots:** `{len(running_bots)}`\n"
        f"└ ⚡ **Server:** `Render Cloud`\n\n"
        "**📚 How to Use:**\n"
        "1️⃣ Send any `.py` file here.\n"
        "2️⃣ Wait for deployment confirmation.\n"
        "3️⃣ Use `/status` to monitor."
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Updates", url=f"https://t.me/{FORCE_CHANNEL}"),
         InlineKeyboardButton("🆘 Support", url=f"https://t.me/{FORCE_GROUP}")]
    ])
    
    await message.reply_text(txt, reply_markup=buttons)

@app.on_message(filters.command("status"))
async def status_cmd(client, message):
    if not await check_fsub(client, message):
        return

    if not running_bots:
        await message.reply_text("📉 **Status:** No active scripts running.")
        return
    
    text = "**🖥️ Active Processes Dashboard**\n━━━━━━━━━━━━━━━━━━\n"
    
    active_count = 0
    for file_name, proc in list(running_bots.items()):
        if proc.returncode is None:
            active_count += 1
            text += f"🟢 **{file_name}**\n└ 🆔 PID: `{proc.pid}`\n\n"
        else:
            del running_bots[file_name]
            
    text += f"━━━━━━━━━━━━━━━━━━\n⚡ **Total Running:** `{active_count}`"
    await message.reply_text(text)

# --- 🛡️ HOSTING LOGIC (Public) ---

@app.on_message(filters.document)
async def host_file(client, message):
    if not await check_fsub(client, message):
        return

    if not message.document.file_name.endswith(".py"):
        await message.reply_text("⚠️ **Format Error:** Only `.py` (Python) files are supported.")
        return

    file_name = message.document.file_name
    msg = await message.reply_text(f"🔄 **Initializing Deployment:** `{file_name}`...", quote=True)
    
    if file_name in running_bots:
        try:
            running_bots[file_name].terminate()
            await asyncio.sleep(1)
        except:
            pass

    path = await message.download()

    try:
        log_file = open(f"{file_name}.log", "w")
        process = await asyncio.create_subprocess_exec(
            sys.executable, path,
            stdout=log_file,
            stderr=log_file
        )
        running_bots[file_name] = process
        
        await msg.edit(
            f"✅ **Deployment Successful**\n\n"
            f"📂 **Script:** `{file_name}`\n"
            f"🆔 **PID:** `{process.pid}`\n"
            f"👤 **User:** {message.from_user.mention}\n\n"
            f"💡 *Use /logs {file_name} to check errors.*"
        )
    except Exception as e:
        await msg.edit(f"❌ **Deployment Failed:**\n`{str(e)}`")

# --- 🔧 UTILITIES ---

@app.on_message(filters.command("stop"))
async def stop_cmd(client, message):
    if not await check_fsub(client, message):
        return

    if len(message.command) < 2:
        await message.reply_text("ℹ️ **Usage:** `/stop filename.py`")
        return
        
    target = message.command[1]
    
    if target in running_bots:
        running_bots[target].terminate()
        del running_bots[target]
        await message.reply_text(f"🛑 **Terminated:** `{target}` has been stopped.")
    else:
        await message.reply_text("⚠️ **Error:** File not found in active registry.")

@app.on_message(filters.command("logs"))
async def logs_cmd(client, message):
    if not await check_fsub(client, message):
        return

    if len(message.command) < 2:
        await message.reply_text("ℹ️ **Usage:** `/logs filename.py`")
        return

    file_name = message.command[1]
    log_path = f"{file_name}.log"
    
    if os.path.exists(log_path):
        await message.reply_document(log_path, caption=f"📝 **System Logs:** `{file_name}`")
    else:
        await message.reply_text("⚠️ **Error:** No log file found.")

# --- ☠️ ADMIN AREA (Owner Only) ---

@app.on_message(filters.command(["term", "sh"]) & filters.user(OWNER_ID))
async def terminal(client, message):
    if len(message.command) < 2:
        await message.reply_text("💻 **Terminal:** Command required.")
        return

    cmd = message.text.split(maxsplit=1)[1]
    msg = await message.reply_text("⚙️ **Executing...**")
    
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    output = stdout.decode() or stderr.decode() or "Done."
    
    if len(output) > 4000:
        with open("term_output.txt", "w") as f: f.write(output)
        await message.reply_document("term_output.txt")
        os.remove("term_output.txt")
    else:
        await msg.edit(f"💻 **Output:**\n```\n{output}\n```")

# --- MAIN EXECUTION ---
async def main():
    print("✅ Nexus Hosting Pro is Live...")
    await app.start()
    await web_server() # Render Hack
    await idle()
    await app.stop()

if __name__ == "__main__":
    app.run(main())