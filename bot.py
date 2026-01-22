import os
import json
import asyncio
import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ===================== BASIC CONFIG =====================
BOT_NAME = "ᴋɪʟʟᴇʀ ᴘʀɪᴢᴇ"

BOT_TOKEN = os.environ.get("BOT_TOKEN")  # set in Railway
ADMIN_ID = int(os.environ.get("ADMIN_ID", "7416432337"))  # CHANGE_THIS

DATA_FILE = "users.json"

# ===================== WEBHOOK CONFIG =====================
PORT = int(os.environ.get("PORT", 8080))

# 👉 IMPORTANT: set this env var in Railway
# Example value: https://killer-prize.up.railway.app
WEBHOOK_BASE_URL = os.environ.get("WEBHOOK_BASE_URL")

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_BASE_URL}{WEBHOOK_PATH}"

# ===================== STARTUP GUARD =====================
BOOT_LOCK = ".boot.lock"

def startup_guard():
    if os.path.exists(BOOT_LOCK):
        print("⚠️ Duplicate startup detected. Exiting.")
        exit(0)
    with open(BOOT_LOCK, "w") as f:
        f.write("locked")

# ===================== STORAGE =====================
def load():
    if not os.path.exists(DATA_FILE):
        return {"STOCK": {"netflix": 2}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ===================== UI =====================
def main_menu():
    return ReplyKeyboardMarkup(
        [
            ["👤 Profile", "🎁 Redeem"],
            ["💰 Points", "🆘 Support"],
        ],
        resize_keyboard=True,
    )

# ===================== ERROR HANDLER =====================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.exception("Unhandled error:", exc_info=context.error)

# ===================== HANDLERS =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load()
    uid = str(update.effective_user.id)

    if uid not in users:
        users[uid] = {"points": 0, "banned": False}

    save(users)

    ref_link = f"https://t.me/{context.bot.username}?start={uid}"

    await update.message.reply_text(
        f"👋 *Welcome to {BOT_NAME}*\n\n"
        "Invite friends, earn points and redeem premium rewards 🎁\n\n"
        f"💰 *Your Points:* {users[uid]['points']}\n\n"
        "🔗 *Your Referral Link:*\n"
        f"{ref_link}",
        reply_markup=main_menu(),
        parse_mode="Markdown",
    )

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load()
    uid = str(update.effective_user.id)

    await update.message.reply_text(
        f"👤 *Your Profile – {BOT_NAME}*\n\n"
        f"🆔 ID: `{uid}`\n"
        f"💰 Points: {users[uid]['points']}",
        reply_markup=main_menu(),
        parse_mode="Markdown",
    )

async def points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load()
    uid = str(update.effective_user.id)

    await update.message.reply_text(
        f"💰 *Your Balance*\n\nYou have *{users[uid]['points']} Points*",
        reply_markup=main_menu(),
        parse_mode="Markdown",
    )

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆘 *Support*\n\nDM admin for help.",
        reply_markup=main_menu(),
        parse_mode="Markdown",
    )

async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("🍿 Netflix – 50", callback_data="redeem_netflix")],
    ]
    await update.message.reply_text(
        f"🎁 *Redeem – {BOT_NAME}*\n\nChoose a reward 👇",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown",
    )

async def redeem_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    users = load()
    uid = str(q.from_user.id)

    if q.data == "redeem_netflix":
        if users["STOCK"]["netflix"] <= 0:
            return await q.edit_message_text("❌ Netflix out of stock")

        if users[uid]["points"] < 50:
            return await q.edit_message_text("❌ Not enough points")

        users["STOCK"]["netflix"] -= 1
        users[uid]["points"] -= 50
        save(users)

        await context.bot.send_message(
            ADMIN_ID,
            f"🚨 New Redeem\nUser: {uid}\nPrize: Netflix",
        )

        await q.edit_message_text(
            "✅ *Redeem Successful*\n\nPlease DM admin with proof.",
            parse_mode="Markdown",
        )

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t = update.message.text
    if t == "👤 Profile":
        return await profile(update, context)
    if t == "🎁 Redeem":
        return await redeem(update, context)
    if t == "💰 Points":
        return await points(update, context)
    if t == "🆘 Support":
        return await support(update, context)

# ===================== MAIN =====================
async def main():
    startup_guard()

    app: Application = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_error_handler(error_handler)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(redeem_cb))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))

    # Reset + set webhook
    await app.bot.delete_webhook(drop_pending_updates=True)
    await app.bot.set_webhook(WEBHOOK_URL)

    print("🔥 ᴋɪʟʟᴇʀ ᴘʀɪᴢᴇ running in WEBHOOK mode")

    await app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=WEBHOOK_PATH,
        webhook_url=WEBHOOK_URL,
    )

if __name__ == "__main__":
    asyncio.run(main())
