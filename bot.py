import os
import re
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("TOKEN")

BAD_WORDS = [
    "jala",
    "gandon",
    "pidaraz",
    "qoto",
    "am",
]

pattern = r"\b(" + "|".join(BAD_WORDS) + r")\b"


# ── Keep-alive server (Render bepul plan uchun) ──────────────────────────────
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot ishlayapti!")

    def log_message(self, format, *args):
        pass  # server loglarini o'chirish


def run_keep_alive():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), KeepAliveHandler)
    print(f"Keep-alive server port {port} da ishga tushdi")
    server.serve_forever()


# ── Handlers ─────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    bot_username = context.bot.username
    add_group_url = f"https://t.me/{bot_username}?startgroup=true"

    keyboard = [[InlineKeyboardButton("➕ Guruhga qo'shish", url=add_group_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        "⚠️ Bu botni gruppaga qo'shing va uni admin qiling.\n\n"
        "🤖 Bot vazifasi:\n"
        "• Gruppadagi so'kinishlarni o'chirish\n"
        "• Tartibni saqlash"
    )
    await update.message.reply_text(text, reply_markup=reply_markup)


async def anti_mat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text

    if re.search(pattern, text, re.IGNORECASE):
        try:
            await update.message.delete()
        except Exception:
            pass


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Keep-alive serverni alohida thread da ishga tushirish
    t = threading.Thread(target=run_keep_alive, daemon=True)
    t.start()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, anti_mat))

    print("Bot ishga tushdi!")
    app.run_polling(drop_pending_updates=True)
