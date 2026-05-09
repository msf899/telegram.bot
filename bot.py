import os
import re
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ChatMemberHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("TOKEN")

BAD_WORDS = [
    "jala",
    "jalla",
    "jallab",
    "jalab",
    "sikaman",
    "siktim",
    "sikey",
    "siki",
    "aminga qotogim",
    "popish",
    "xuyela",
    "pidr",
    "dinnaxuy",
    "pawol naxxuy",
    "gandon",
    "pidaraz",
    "pidoras",
    "qoto",
    "qotoq",
    "yiban",
    "skb",
    "oneni ami",
    "am",
]


def make_flexible_pattern(word):
    return "".join(f"{re.escape(c)}+" for c in word)


flexible_patterns = [make_flexible_pattern(w) for w in BAD_WORDS]
pattern = re.compile(
    r"(" + "|".join(flexible_patterns) + r")",
    re.IGNORECASE,
)


# ── Keep-alive server ────────────────────────────────────────────────────────
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot ishlayapti!")

    def log_message(self, format, *args):
        pass


def run_keep_alive():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), KeepAliveHandler)
    print(f"Keep-alive server port {port} da ishga tushdi")
    server.serve_forever()


# ── Xabarni N sekunddan keyin o'chirish ─────────────────────────────────────
async def delete_after(message, seconds: int):
    await asyncio.sleep(seconds)
    try:
        await message.delete()
    except Exception:
        pass


# ── /start — faqat private chatda ───────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    if update.message.chat.type in ["group", "supergroup"]:
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


# ── Bot guruhga qo'shilganda salom ──────────────────────────────────────────
async def bot_added_to_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.my_chat_member
    if not result:
        return

    old_status = result.old_chat_member.status
    new_status = result.new_chat_member.status

    if old_status in ["left", "kicked"] and new_status in ["member", "administrator"]:
        await result.chat.send_message(
            "👋 Salom! Men so'kinishlarni nazorat qiluvchi botman.\n\n"
            "⚠️ Meni admin qiling va 'Delete messages' ruxsatini bering.\n"
            "🚫 Guruhda so'kingan foydalanuvchilar ogohlantiriladi!"
        )


# ── So'kinish filtri ─────────────────────────────────────────────────────────
async def anti_mat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text

    if pattern.search(text):
        user = update.message.from_user
        name = f"@{user.username}" if user.username else (user.first_name or "Foydalanuvchi")

        try:
            await update.message.delete()
        except Exception:
            pass

        try:
            warning = await update.message.chat.send_message(
                f"⚠️ {name}, iltimos so'kinmang! Guruh qoidalariga rioya qiling. 🙏"
            )
            context.application.create_task(delete_after(warning, 5 * 60))
        except Exception:
            pass


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    t = threading.Thread(target=run_keep_alive, daemon=True)
    t.start()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(ChatMemberHandler(bot_added_to_group, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, anti_mat))

    print("Bot ishga tushdi!")
    app.run_polling(drop_pending_updates=True)
