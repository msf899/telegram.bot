from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# TOKEN
TOKEN = "BU_YERGA_TOKEN"

# So'kinishlar
BAD_WORDS = [
    "mat",
    "suka",
    "blyat",
    "fuck",
]

# START komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    bot_username = context.bot.username

    # Guruhga qo'shish linki
    add_group_url = f"https://t.me/{bot_username}?startgroup=true"

    keyboard = [
        [
            InlineKeyboardButton(
                "➕ Guruhga qo'shish",
                url=add_group_url
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        "⚠️ Bu botni gruppaga qo'shing va uni admin qiling.\n\n"
        "🤖 Bot vazifasi:\n"
        "• Gruppadagi so'kingan habarlarni o'chirish\n"
        "• So'kingan foydalanuvchiga tanbeh berish"
    )

    await update.message.reply_text(
        text,
        reply_markup=reply_markup
    )

# Anti-mat
async def anti_mat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    if not update.message.text:
        return

    text = update.message.text.lower()

    for word in BAD_WORDS:

        if word in text:

            try:
                await update.message.delete()
            except:
                pass

            break

# APP
app = ApplicationBuilder().token(TOKEN).build()

# Handlers
app.add_handler(CommandHandler("start", start))

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        anti_mat
    )
)

print("Bot ishladi!")

app.run_polling()