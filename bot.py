import json, os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ================= CONFIG =================
BOT_TOKEN = "8535994212:AAHx0qTj8mLlo_V1Z96SH6Ul-9G-XCKKMp4"
ADMIN_ID = 7416432337  # your numeric Telegram ID

PRIVATE_CHANNEL_ID = -1003636897874
PRIVATE_INVITE_LINK = "https://t.me/+SDer3T7su6s3YmI1"

SUPPORT_USERNAME = "@KILL4R_UR"

INSTA_API_URL = "https://web-production-99d43.up.railway.app/profile/USERNAME"
NUMBER_API_URL = "https://number-to-info-api-production.up.railway.app/api/info?number=XXXXXXXXXX"

DATA_FILE = "users.json"
REFERRAL_POINTS = 10
BOT_NAME = "ᴋɪʟʟᴇʀ ᴘʀɪᴢᴇ"

# ================= STORAGE =================
def load():
    if not os.path.exists(DATA_FILE):
        return {"STOCK": {"netflix": 2}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ================= MENU =================
def main_menu():
    return ReplyKeyboardMarkup(
        [
            ["👤 Profile", "🎁 Redeem"],
            ["💰 Points", "🆘 Support"]
        ],
        resize_keyboard=True
    )

# ================= FORCE JOIN =================
async def is_joined(bot, user_id):
    try:
        m = await bot.get_chat_member(PRIVATE_CHANNEL_ID, user_id)
        return m.status in ["member", "administrator", "creator"]
    except:
        return False

async def force_join(update):
    kb = [
        [InlineKeyboardButton("📢 Join Private Channel", url=PRIVATE_INVITE_LINK)],
        [InlineKeyboardButton("✅ I Joined", callback_data="recheck")]
    ]
    await update.message.reply_text(
        f"📢 *Channel Join Required*\n\n"
        f"To use *{BOT_NAME}*, you must join our private channel 🔒\n\n"
        "👇 Join first, then tap *I Joined*",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="MarkdownV2"
    )

async def recheck(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if not await is_joined(context.bot, q.from_user.id):
        await q.edit_message_text(
            "❌ *Access Restricted*\n\nPlease join the channel first.",
            parse_mode="MarkdownV2"
        )
    else:
        await q.edit_message_text(
            "✅ *Access Granted*\n\nNow send /start",
            parse_mode="MarkdownV2"
        )

# ================= REFERRAL SUCCESS =================
async def send_referral_success(bot, referrer_id, new_user):
    try:
        await bot.send_message(
            chat_id=int(referrer_id),
            text=(
                "🎉 *New Referral Successful*\n\n"
                f"You earned *{REFERRAL_POINTS} Points* 💰\n\n"
                f"👤 User: @{new_user.username if new_user.username else 'User'}\n\n"
                f"Keep winning with *{BOT_NAME}* 🔥"
            ),
            parse_mode="MarkdownV2"
        )
    except:
        pass

# ================= ADMIN ALERT =================
async def notify_admin(bot, user, prize, cost):
    try:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"🚨 *New Redeem – {BOT_NAME}*\n\n"
                f"👤 User: @{user.username if user.username else 'User'}\n"
                f"🆔 ID: `{user.id}`\n\n"
                f"🎁 Reward: *{prize}*\n"
                f"💰 Points Used: *{cost}*\n\n"
                "Ask the user to DM with proof ✅"
            ),
            parse_mode="MarkdownV2"
        )
    except:
        pass

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_joined(context.bot, update.effective_user.id):
        await force_join(update)
        return

    users = load()
    user = update.effective_user
    uid = str(user.id)

    if uid not in users:
        users[uid] = {"points": 0, "ref_by": None, "banned": False}

        if context.args:
            ref = context.args[0]
            if ref != uid and ref in users and users[uid]["ref_by"] is None:
                users[uid]["ref_by"] = ref
                users[ref]["points"] += REFERRAL_POINTS
                await send_referral_success(context.bot, ref, user)

    save(users)

    referral_link = f"https://t.me/{context.bot.username}?start={uid}"

    await update.message.reply_text(
        f"👋 *Welcome to {BOT_NAME}*\n\n"
        "Earn points by inviting friends and redeem premium rewards 🎁\n\n"
        f"💰 *Your Points:* {users[uid]['points']}\n\n"
        "🔗 *Your Referral Link:*\n"
        f"{referral_link}\n\n"
        "Invite • Earn • Redeem • Win 🚀",
        reply_markup=main_menu(),
        parse_mode="MarkdownV2"
    )

# ================= PROFILE =================
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load()
    user = update.effective_user
    uid = str(user.id)

    referrals = sum(
        1 for u in users.values()
        if isinstance(u, dict) and u.get("ref_by") == uid
    )

    referral_link = f"https://t.me/{context.bot.username}?start={uid}"

    await update.message.reply_text(
        f"👤 *Your Profile – {BOT_NAME}*\n\n"
        f"👤 Name: {user.first_name}\n"
        f"🆔 ID: `{user.id}`\n\n"
        f"💰 Points: {users[uid]['points']}\n"
        f"👥 Referrals: {referrals}\n\n"
        "🔗 *Referral Link:*\n"
        f"{referral_link}",
        reply_markup=main_menu(),
        parse_mode="MarkdownV2"
    )

# ================= POINTS =================
async def points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load()
    uid = str(update.effective_user.id)
    await update.message.reply_text(
        f"💰 *Your Balance*\n\nYou have *{users[uid]['points']} Points* 💎",
        reply_markup=main_menu(),
        parse_mode="MarkdownV2"
    )

# ================= REDEEM =================
async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("🎬 Prime Account – 20", callback_data="prime_acc")],
        [InlineKeyboardButton("📞 Number API – 30", callback_data="number_api")],
        [InlineKeyboardButton("🎬 Prime Method – 40", callback_data="prime_method")],
        [InlineKeyboardButton("📸 Insta API – 40", callback_data="insta_api")],
        [InlineKeyboardButton("🍿 Netflix – 50", callback_data="netflix")]
    ]
    await update.message.reply_text(
        f"🎁 *Redeem Rewards – {BOT_NAME}*\n\nChoose a reward below 👇",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="MarkdownV2"
    )

# ================= CONFIRM =================
def confirm_keyboard(action):
    return InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_{action}"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel")
        ]]
    )

# ================= REDEEM HANDLER =================
async def redeem_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    users = load()
    user = q.from_user
    uid = str(user.id)

    prizes = {
        "prime_acc": ("Prime Video 3 Months (Account)", 20),
        "number_api": ("Advanced Number Info API", 30),
        "prime_method": ("Prime Video 3 Months (Method)", 40),
        "insta_api": ("Instagram Info API", 40),
        "netflix": ("Netflix 1 Month", 50)
    }

    if q.data == "cancel":
        return await q.edit_message_text(
            "❌ *Redeem Cancelled*\n\nNo points were deducted.",
            parse_mode="MarkdownV2"
        )

    if q.data in prizes:
        prize, cost = prizes[q.data]
        if users[uid]["points"] < cost:
            return await q.edit_message_text("❌ Not enough points.")
        if q.data == "netflix" and users["STOCK"]["netflix"] <= 0:
            return await q.edit_message_text("❌ Netflix out of stock.")
        return await q.edit_message_text(
            f"🛒 *Confirm Your Purchase*\n\n"
            f"🎁 Reward: {prize}\n"
            f"💰 Cost: {cost} Points\n\n"
            "Do you want to continue?",
            reply_markup=confirm_keyboard(q.data),
            parse_mode="MarkdownV2"
        )

    if q.data.startswith("confirm_"):
        action = q.data.replace("confirm_", "")
        prize, cost = prizes[action]

        if users[uid]["points"] < cost:
            return await q.edit_message_text("❌ Not enough points.")

        if action == "netflix":
            if users["STOCK"]["netflix"] <= 0:
                return await q.edit_message_text("❌ Netflix out of stock.")
            users["STOCK"]["netflix"] -= 1

        users[uid]["points"] -= cost
        save(users)

        await notify_admin(context.bot, user, prize, cost)

        return await q.edit_message_text(
            f"✅ *Redeem Successful*\n\n"
            f"🎁 Reward: {prize}\n\n"
            f"📩 Please DM admin with proof to receive your reward.\n\n"
            f"Thanks for using *{BOT_NAME}* 💎",
            parse_mode="MarkdownV2"
        )

# ================= SUPPORT =================
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🆘 *Support – {BOT_NAME}*\n\nDM {SUPPORT_USERNAME} for help.",
        reply_markup=main_menu(),
        parse_mode="MarkdownV2"
    )

# ================= MENU HANDLER =================
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

# ================= APP =================
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(redeem_cb))
app.add_handler(CallbackQueryHandler(recheck, pattern="recheck"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))

print("🔥 ᴋɪʟʟᴇʀ ᴘʀɪᴢᴇ is running")
app.run_polling(drop_pending_updates=True)
