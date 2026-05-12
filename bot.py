#!/usr/bin/env python3
"""
╔══════════════════════════════════════════╗
║   PAK SIM DATABASE - VIP PRO BOT        ║
║   Developed by OLD-STUDIO               ║
║   Version: 2.0 Premium                  ║
╚══════════════════════════════════════════╝
"""

import logging
import requests
import json
import os
import time
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# ============================================================
#   CONFIGURATION - APNI DETAILS YAHAN BHARO
# ============================================================
BOT_TOKEN = "8600934565:AAHZgG4CQQ_Uof4oOfIkA823sV8laIju4Io"          # BotFather se mila token
ADMIN_ID = 7878519937                       # Tumhara Telegram ID
WEBSITE_URL = "https://paksimsearch.gamer.gd"  # Tumhari website
API_URL = "https://wasifali-sim-info.netlify.app/api/search"

# Bot Info
BOT_NAME = "🇵🇰 PAK SIM DATABASE"
BOT_VERSION = "VIP PRO v2.0"
CHANNEL_LINK = "https://t.me/your_channel"  # Optional: apna channel

# Files for data storage
USERS_FILE = "users.json"
BANNED_FILE = "banned.json"
STATS_FILE = "stats.json"

# ============================================================
#   LOGGING
# ============================================================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================
#   DATA MANAGEMENT
# ============================================================
def load_json(filename):
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_json(filename, data):
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Save error: {e}")

def get_users():
    return load_json(USERS_FILE)

def save_user(user):
    users = get_users()
    uid = str(user.id)
    if uid not in users:
        users[uid] = {
            "id": user.id,
            "name": user.full_name,
            "username": user.username or "N/A",
            "joined": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "searches": 0
        }
        save_json(USERS_FILE, users)
    return users

def get_banned():
    return load_json(BANNED_FILE)

def is_banned(user_id):
    banned = get_banned()
    return str(user_id) in banned

def get_stats():
    stats = load_json(STATS_FILE)
    if not stats:
        stats = {"total_searches": 0, "total_users": 0}
    return stats

def update_stats(searches=0, users=0):
    stats = get_stats()
    stats["total_searches"] = stats.get("total_searches", 0) + searches
    stats["total_users"] = len(get_users())
    save_json(STATS_FILE, stats)

# ============================================================
#   API SEARCH FUNCTION
# ============================================================
def search_sim(query):
    try:
        url = f"{API_URL}?phone={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        data = response.json()
        if data and ('success' in data or 'records' in data):
            return data
        return None
    except Exception as e:
        logger.error(f"API Error: {e}")
        return None

# ============================================================
#   FORMAT RESULT
# ============================================================
def format_result(data, query):
    records = data.get('records', [])
    if not records:
        return None

    text = f"""
╔══════════════════════════╗
║  🇵🇰 PAK SIM DATABASE    ║
║  ✨ VIP PRO RESULTS      ║
╚══════════════════════════╝

🔍 **Search:** `{query}`
📊 **Records Found:** {len(records)}
━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    for i, record in enumerate(records[:5], 1):
        text += f"\n📋 **Record {i}:**\n"

        fields = {
            'name': '👤 Name',
            'cnic': '🪪 CNIC',
            'phone': '📱 Phone',
            'address': '🏠 Address',
            'city': '🌆 City',
            'province': '📍 Province',
            'network': '📡 Network',
            'dob': '🎂 Date of Birth',
            'father_name': "👨 Father's Name",
            'email': '📧 Email',
            'sim_count': '📊 SIM Count',
        }

        for key, label in fields.items():
            val = record.get(key, '')
            if val and str(val).strip() and str(val) != 'None':
                text += f"  {label}: `{val}`\n"

        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

    text += f"\n🌐 **Website:** {WEBSITE_URL}"
    text += f"\n⏰ **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    text += f"\n\n💎 **{BOT_NAME}** | {BOT_VERSION}"

    return text

# ============================================================
#   KEYBOARDS
# ============================================================
def main_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🔍 Search SIM", callback_data="search_info"),
            InlineKeyboardButton("📊 Statistics", callback_data="stats")
        ],
        [
            InlineKeyboardButton("ℹ️ Help", callback_data="help"),
            InlineKeyboardButton("🌐 Website", url=WEBSITE_URL)
        ],
        [
            InlineKeyboardButton("👑 About Bot", callback_data="about")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("👥 All Users", callback_data="admin_users"),
            InlineKeyboardButton("📊 Full Stats", callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
            InlineKeyboardButton("🚫 Ban User", callback_data="admin_ban")
        ],
        [
            InlineKeyboardButton("✅ Unban User", callback_data="admin_unban"),
            InlineKeyboardButton("📋 Banned List", callback_data="admin_banlist")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="back_main")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# ============================================================
#   COMMAND HANDLERS
# ============================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Ban check
    if is_banned(user.id):
        await update.message.reply_text(
            "🚫 **You are banned from using this bot.**\n"
            "Contact admin for support.",
            parse_mode='Markdown'
        )
        return

    # Save user
    save_user(user)
    update_stats(users=1)

    welcome_text = f"""
╔══════════════════════════╗
║  🇵🇰 PAK SIM DATABASE    ║
║  ✨ VIP PRO BOT          ║
╚══════════════════════════╝

👋 **Welcome, {user.first_name}!**

🔍 Search any Pakistani SIM/CNIC details instantly!

**How to use:**
• Send any **Phone Number** (10-13 digits)
• Send any **CNIC** (13 digits)
• Or use /search command

💎 **Features:**
✅ Real-time SIM Database
✅ CNIC Lookup
✅ Instant Results
✅ 24/7 Available

━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 {WEBSITE_URL}
💎 {BOT_VERSION}
"""
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=main_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
╔══════════════════════════╗
║      📚 HELP GUIDE       ║
╚══════════════════════════╝

**🔍 How to Search:**

1️⃣ **Phone Number Search:**
   Send: `03001234567`

2️⃣ **CNIC Search:**
   Send: `3520112345678`

3️⃣ **Commands:**
   /start - Main menu
   /search - Search guide
   /stats - Statistics
   /help - This help

━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 Just type the number directly!
💎 PAK SIM DATABASE VIP PRO
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = get_stats()
    users = get_users()

    stats_text = f"""
╔══════════════════════════╗
║    📊 BOT STATISTICS     ║
╚══════════════════════════╝

👥 **Total Users:** {len(users)}
🔍 **Total Searches:** {stats.get('total_searches', 0)}
🌐 **Website:** Active ✅
🤖 **Bot Status:** Online 🟢
⏰ **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

━━━━━━━━━━━━━━━━━━━━━━━━━━
💎 {BOT_NAME} | {BOT_VERSION}
"""
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_main")]]
    await update.message.reply_text(
        stats_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Access Denied!")
        return

    users = get_users()
    stats = get_stats()
    banned = get_banned()

    admin_text = f"""
╔══════════════════════════╗
║    👑 ADMIN PANEL        ║
╚══════════════════════════╝

👥 **Total Users:** {len(users)}
🔍 **Total Searches:** {stats.get('total_searches', 0)}
🚫 **Banned Users:** {len(banned)}
🟢 **Bot Status:** Online

━━━━━━━━━━━━━━━━━━━━━━━━━━
Select an option below:
"""
    await update.message.reply_text(
        admin_text,
        parse_mode='Markdown',
        reply_markup=admin_keyboard()
    )

# ============================================================
#   MESSAGE HANDLER - SEARCH
# ============================================================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    query = update.message.text.strip()

    # Ban check
    if is_banned(user.id):
        await update.message.reply_text("🚫 You are banned from this bot.")
        return

    # Save user if new
    save_user(user)

    # Validate input
    clean_query = query.replace("-", "").replace(" ", "")
    if not clean_query.isdigit() or len(clean_query) < 10 or len(clean_query) > 13:
        await update.message.reply_text(
            "❌ **Invalid Format!**\n\n"
            "Please send:\n"
            "📱 Phone: `03001234567`\n"
            "🪪 CNIC: `3520112345678`\n\n"
            "Numbers only, 10-13 digits.",
            parse_mode='Markdown'
        )
        return

    # Searching message
    searching_msg = await update.message.reply_text(
        f"⏳ **Searching...**\n\n"
        f"🔍 Query: `{clean_query}`\n"
        f"📡 Connecting to database...",
        parse_mode='Markdown'
    )

    # Perform search
    result = search_sim(clean_query)

    if result:
        formatted = format_result(result, clean_query)
        if formatted:
            # Update search stats
            stats = get_stats()
            stats['total_searches'] = stats.get('total_searches', 0) + 1
            save_json(STATS_FILE, stats)

            # Update user search count
            users = get_users()
            uid = str(user.id)
            if uid in users:
                users[uid]['searches'] = users[uid].get('searches', 0) + 1
                save_json(USERS_FILE, users)

            keyboard = [
                [
                    InlineKeyboardButton("🔍 Search Again", callback_data="search_info"),
                    InlineKeyboardButton("🌐 Website", url=WEBSITE_URL)
                ]
            ]

            await searching_msg.edit_text(
                formatted,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await searching_msg.edit_text(
                f"❌ **No Records Found**\n\n"
                f"🔍 Query: `{clean_query}`\n\n"
                f"No data available for this number.",
                parse_mode='Markdown'
            )
    else:
        await searching_msg.edit_text(
            f"❌ **Search Failed**\n\n"
            f"🔍 Query: `{clean_query}`\n\n"
            f"• No records found, OR\n"
            f"• Database temporarily unavailable\n\n"
            f"Please try again later.",
            parse_mode='Markdown'
        )

# ============================================================
#   CALLBACK HANDLERS
# ============================================================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = query.from_user

    # ── MAIN MENU CALLBACKS ──
    if data == "back_main":
        welcome_text = f"""
╔══════════════════════════╗
║  🇵🇰 PAK SIM DATABASE    ║
║  ✨ VIP PRO BOT          ║
╚══════════════════════════╝

👋 **Welcome back, {user.first_name}!**

Send a Phone Number or CNIC to search.
💎 {BOT_VERSION}
"""
        await query.edit_message_text(
            welcome_text,
            parse_mode='Markdown',
            reply_markup=main_keyboard()
        )

    elif data == "search_info":
        await query.edit_message_text(
            "🔍 **HOW TO SEARCH:**\n\n"
            "Simply type and send:\n\n"
            "📱 **Phone:** `03001234567`\n"
            "🪪 **CNIC:** `3520112345678`\n\n"
            "Results will appear instantly! ⚡",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data="back_main")
            ]])
        )

    elif data == "stats":
        stats = get_stats()
        users = get_users()
        await query.edit_message_text(
            f"📊 **STATISTICS:**\n\n"
            f"👥 Total Users: `{len(users)}`\n"
            f"🔍 Total Searches: `{stats.get('total_searches', 0)}`\n"
            f"🟢 Status: Online\n"
            f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data="back_main")
            ]])
        )

    elif data == "help":
        await query.edit_message_text(
            "📚 **HELP:**\n\n"
            "Send Phone or CNIC number directly.\n\n"
            "📱 Phone: `03001234567`\n"
            "🪪 CNIC: `3520112345678`\n\n"
            "Commands:\n"
            "/start - Main menu\n"
            "/stats - Statistics\n"
            "/help - Help",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data="back_main")
            ]])
        )

    elif data == "about":
        await query.edit_message_text(
            f"👑 **ABOUT BOT:**\n\n"
            f"🤖 Name: {BOT_NAME}\n"
            f"💎 Version: {BOT_VERSION}\n"
            f"🌐 Website: {WEBSITE_URL}\n"
            f"👨‍💻 Developer: OLD-STUDIO\n\n"
            f"✅ 24/7 Online\n"
            f"✅ Real Database\n"
            f"✅ Instant Results",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🌐 Visit Website", url=WEBSITE_URL),
                InlineKeyboardButton("🔙 Back", callback_data="back_main")
            ]])
        )

    # ── ADMIN CALLBACKS ──
    elif data == "admin_users" and user.id == ADMIN_ID:
        users = get_users()
        text = f"👥 **ALL USERS ({len(users)}):**\n\n"
        for uid, info in list(users.items())[:20]:
            text += f"• {info['name']} | ID: `{info['id']}` | Searches: {info.get('searches', 0)}\n"
        if len(users) > 20:
            text += f"\n...and {len(users) - 20} more users"
        await query.edit_message_text(
            text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data="admin_back")
            ]])
        )

    elif data == "admin_stats" and user.id == ADMIN_ID:
        stats = get_stats()
        users = get_users()
        banned = get_banned()
        await query.edit_message_text(
            f"📊 **FULL STATISTICS:**\n\n"
            f"👥 Total Users: `{len(users)}`\n"
            f"🔍 Total Searches: `{stats.get('total_searches', 0)}`\n"
            f"🚫 Banned: `{len(banned)}`\n"
            f"🟢 Status: Online\n"
            f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data="admin_back")
            ]])
        )

    elif data == "admin_broadcast" and user.id == ADMIN_ID:
        context.user_data['waiting_for'] = 'broadcast'
        await query.edit_message_text(
            "📢 **BROADCAST MESSAGE:**\n\n"
            "Send your message now.\n"
            "It will be sent to ALL users.\n\n"
            "Send /cancel to cancel.",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ Cancel", callback_data="admin_back")
            ]])
        )

    elif data == "admin_ban" and user.id == ADMIN_ID:
        context.user_data['waiting_for'] = 'ban'
        await query.edit_message_text(
            "🚫 **BAN USER:**\n\n"
            "Send the User ID to ban.\n"
            "Example: `923456789`\n\n"
            "Send /cancel to cancel.",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ Cancel", callback_data="admin_back")
            ]])
        )

    elif data == "admin_unban" and user.id == ADMIN_ID:
        context.user_data['waiting_for'] = 'unban'
        await query.edit_message_text(
            "✅ **UNBAN USER:**\n\n"
            "Send the User ID to unban.\n"
            "Example: `923456789`\n\n"
            "Send /cancel to cancel.",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ Cancel", callback_data="admin_back")
            ]])
        )

    elif data == "admin_banlist" and user.id == ADMIN_ID:
        banned = get_banned()
        if banned:
            text = f"🚫 **BANNED USERS ({len(banned)}):**\n\n"
            for uid, info in banned.items():
                text += f"• ID: `{uid}` | {info.get('name', 'Unknown')}\n"
        else:
            text = "✅ No banned users."
        await query.edit_message_text(
            text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data="admin_back")
            ]])
        )

    elif data == "admin_back" and user.id == ADMIN_ID:
        users = get_users()
        stats = get_stats()
        banned = get_banned()
        await query.edit_message_text(
            f"👑 **ADMIN PANEL**\n\n"
            f"👥 Users: `{len(users)}`\n"
            f"🔍 Searches: `{stats.get('total_searches', 0)}`\n"
            f"🚫 Banned: `{len(banned)}`\n"
            f"🟢 Status: Online",
            parse_mode='Markdown',
            reply_markup=admin_keyboard()
        )

# ============================================================
#   ADMIN ACTION HANDLER (Broadcast / Ban / Unban)
# ============================================================
async def handle_admin_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        return False

    waiting = context.user_data.get('waiting_for')
    if not waiting:
        return False

    text = update.message.text.strip()

    if text == '/cancel':
        context.user_data.pop('waiting_for', None)
        await update.message.reply_text("❌ Cancelled.", reply_markup=main_keyboard())
        return True

    if waiting == 'broadcast':
        users = get_users()
        success = 0
        failed = 0
        await update.message.reply_text(f"📢 Broadcasting to {len(users)} users...")

        for uid, info in users.items():
            try:
                await context.bot.send_message(
                    chat_id=int(uid),
                    text=f"📢 **ANNOUNCEMENT**\n\n{text}\n\n💎 {BOT_NAME}",
                    parse_mode='Markdown'
                )
                success += 1
                time.sleep(0.05)
            except:
                failed += 1

        await update.message.reply_text(
            f"✅ **Broadcast Done!**\n\n"
            f"✅ Success: {success}\n"
            f"❌ Failed: {failed}"
        )
        context.user_data.pop('waiting_for', None)
        return True

    elif waiting == 'ban':
        if text.isdigit():
            banned = get_banned()
            users = get_users()
            name = users.get(text, {}).get('name', 'Unknown')
            banned[text] = {"name": name, "banned_at": datetime.now().strftime("%Y-%m-%d %H:%M")}
            save_json(BANNED_FILE, banned)
            await update.message.reply_text(f"🚫 User `{text}` ({name}) has been banned!", parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Invalid ID. Send numbers only.")
        context.user_data.pop('waiting_for', None)
        return True

    elif waiting == 'unban':
        if text.isdigit():
            banned = get_banned()
            if text in banned:
                del banned[text]
                save_json(BANNED_FILE, banned)
                await update.message.reply_text(f"✅ User `{text}` has been unbanned!", parse_mode='Markdown')
            else:
                await update.message.reply_text(f"⚠️ User `{text}` is not banned.", parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Invalid ID. Send numbers only.")
        context.user_data.pop('waiting_for', None)
        return True

    return False

# Combined message handler
async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # First check admin actions
    if update.effective_user.id == ADMIN_ID:
        handled = await handle_admin_actions(update, context)
        if handled:
            return
    # Otherwise handle as search
    await handle_message(update, context)

# ============================================================
#   MAIN - BOT START
# ============================================================
def main():
    print("""
╔══════════════════════════════════════════╗
║   PAK SIM DATABASE - VIP PRO BOT        ║
║   Starting up...                        ║
╚══════════════════════════════════════════╝
    """)

    app = Application.builder().token(BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("admin", admin_command))

    # Callback handler
    app.add_handler(CallbackQueryHandler(handle_callback))

    # Message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_router))

    print("✅ Bot is running! Press Ctrl+C to stop.")
    logger.info("Bot started successfully!")

    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
