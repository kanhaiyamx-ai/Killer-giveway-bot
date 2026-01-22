import json, os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ================= CONFIG =================
BOT_TOKEN = "8535994212:AAGE4A-F594gZVMFNd2278InwSG93-AJJrY"
ADMIN_ID = 7416432337  # your numeric Telegram ID

# PRIVATE CHANNEL
PRIVATE_CHANNEL_ID = -1003636897874
PRIVATE_INVITE_LINK = "https://t.me/+SDer3T7su6s3YmI1"

# SUPPORT
SUPPORT_USERNAME = "@KILL4R_UR"

# APIs
INSTA_API_URL = "https://web-production-99d43.up.railway.app/profile/USERNAME"
NUMBER_API_URL = "https://number-to-info-api-production.up.railway.app/api/info?number=XXXXXXXXXX"

DATA_FILE = "users.json"
REFERRAL_POINTS = 10

# ================= STORAGE =================
def load():
    if not os.path.exists(DATA_FILE):
        return {"STOCK": {"netflix": 2}}
    with open(DATA_FILE) as f:
        return json.load(f)

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

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
        "*_*📢 Channel Join Required_*_\n\n"
        "_You must join our private channel to use this bot._\n\n"
        "👇 *Join the channel, then tap* **I Joined**",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )

async def recheck(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if not await is_joined(context.bot, q.from_user.id):
        await q.edit_message_text(
            "*_*❌ Not Joined Yet_*_\n\n"
            "_Please join the channel first._",
            parse_mode="Markdown"
        )
    else:
        await q.edit_message_text(
            "*_*✅ Access Granted_*_\n\n"
            "_Now click* /start",
            parse_mode="Markdown"
        )

# ================= REFERRAL SUCCESS MESSAGE =================
async def send_referral_success(bot, referrer_id, new_user):
    try:
        await bot.send_message(
            chat_id=int(referrer_id),
            text=
            "*_*🎉 New Referral Successful!*_\n\n"
            f"_You just earned *{REFERRAL_POINTS} Points*._\n\n"
            f"👤 *New User:* @{new_user.username if new_user.username else 'User'}\n\n"
            "_Keep inviting to earn more rewards 🚀_",
            parse_mode="Markdown"
        )
    except:
        pass

# ================= ADMIN REDEEM ALERT =================
async def notify_admin_redeem(bot, user, prize, cost):
    try:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=
            "*_*🚨 New Redeem Alert!*_\n\n"
            f"👤 *User:* @{user.username if user.username else 'User'}\n"
            f"🆔 *User ID:* `{user.id}`\n\n"
            f"🎁 *Prize:* *{prize}*\n"
            f"💰 *Points Used:* *{cost}*\n\n"
            "_Ask the user to DM you with proof._",
            parse_mode="Markdown"
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
    kb = [[InlineKeyboardButton("📋 Copy Referral Link", url=referral_link)]]

    await update.message.reply_text(
        "*_*👋 Welcome to the Rewards Bot_*_\n\n"
        f"*💰 Your Points:* *{users[uid]['points']}*\n\n"
        "*🔗 Your Referral Link:*\n"
        f"_{referral_link}_\n\n"
        "_Invite friends and earn rewards 🚀_",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )

# ================= POINTS =================
async def points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load()
    uid = str(update.effective_user.id)
    await update.message.reply_text(
        "*_*💰 Your Points Balance_*_\n\n"
        f"You have *{users[uid]['points']} Points*",
        parse_mode="Markdown"
    )

# ================= REDEEM =================
async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_joined(context.bot, update.effective_user.id):
        await force_join(update)
        return

    kb = [
        [InlineKeyboardButton("🎬 Prime 3M – Account | 20 pts", callback_data="prime_acc")],
        [InlineKeyboardButton("📞 Advanced Number API | 30 pts", callback_data="number_api")],
        [InlineKeyboardButton("🎬 Prime 3M – Method | 40 pts", callback_data="prime_method")],
        [InlineKeyboardButton("📸 Instagram Info API | 40 pts", callback_data="insta_api")],
        [InlineKeyboardButton("🍿 Netflix 1M – Limited | 50 pts", callback_data="netflix")],
        [InlineKeyboardButton("🔐 Paid Channel Entry | 100 pts", callback_data="paid")]
    ]

    await update.message.reply_text(
        "*_*🎁 Redeem Your Rewards_*_\n\n"
        "_Choose a reward below:_",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )

# ================= REDEEM HANDLER =================
async def redeem_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    users = load()
    user = q.from_user
    uid = str(user.id)

    def low():
        return q.edit_message_text("❌ _Not enough points._", parse_mode="Markdown")

    async def success(prize, cost):
        await notify_admin_redeem(context.bot, user, prize, cost)
        return await q.edit_message_text(
            "*_*✅ Redeem Successful!*_\n\n"
            f"*🎁 Prize:* *{prize}*\n\n"
            f"📩 _Please DM admin {SUPPORT_USERNAME} with proof to receive your reward._",
            parse_mode="Markdown"
        )

    if q.data == "prime_acc":
        if users[uid]["points"] < 20: return await low()
        users[uid]["points"] -= 20; save(users)
        return await success("Prime Video 3 Months (Account)", 20)

    if q.data == "number_api":
        if users[uid]["points"] < 30: return await low()
        users[uid]["points"] -= 30; save(users)
        await notify_admin_redeem(context.bot, user, "Advanced Number Info API", 30)
        return await q.edit_message_text(
            "*_*📞 Advanced Number API Unlocked_*_\n\n"
            "_Tap below to copy API URL._\n\n"
            f"📩 _Also DM admin {SUPPORT_USERNAME} with proof._",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("📋 Copy API URL", url=NUMBER_API_URL)]]
            ),
            parse_mode="Markdown"
        )

    if q.data == "prime_method":
        if users[uid]["points"] < 40: return await low()
        users[uid]["points"] -= 40; save(users)
        return await success("Prime Video 3 Months (Method)", 40)

    if q.data == "insta_api":
        if users[uid]["points"] < 40: return await low()
        users[uid]["points"] -= 40; save(users)
        await notify_admin_redeem(context.bot, user, "Instagram Info API", 40)
        return await q.edit_message_text(
            "*_*📸 Instagram API Unlocked_*_\n\n"
            "_Tap below to copy API URL._\n\n"
            f"📩 _Also DM admin {SUPPORT_USERNAME} with proof._",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("📋 Copy API URL", url=INSTA_API_URL)]]
            ),
            parse_mode="Markdown"
        )

    if q.data == "netflix":
        if users["STOCK"]["netflix"] <= 0:
            return await q.edit_message_text("*_*❌ Netflix Out of Stock_*_", parse_mode="Markdown")
        if users[uid]["points"] < 50: return await low()
        users[uid]["points"] -= 50
        users["STOCK"]["netflix"] -= 1
        save(users)
        return await success("Netflix 1 Month", 50)

    if q.data == "paid":
        if users[uid]["points"] < 100: return await low()
        users[uid]["points"] -= 100; save(users)
        return await success("Paid Channel Entry (Lifetime)", 100)

# ================= SUPPORT =================
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*_*🆘 Support Center_*_\n\n"
        f"_For any help, DM {SUPPORT_USERNAME}_",
        parse_mode="Markdown"
    )

# ================= APP =================
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("points", points))
app.add_handler(CommandHandler("redeem", redeem))
app.add_handler(CommandHandler("support", support))
app.add_handler(CallbackQueryHandler(redeem_cb))
app.add_handler(CallbackQueryHandler(recheck, pattern="recheck"))

print("🔥 Rewards Bot Running")
app.run_polling()
