import os
import threading
import asyncio
import logging
from zoneinfo import ZoneInfo
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# عشان Render يشتغل
app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "Bot is Alive - فغال ✅"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

threading.Thread(target=run_flask, daemon=True).start()

# كود البوت
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = -1004425103888
ADMIN_USER_ID = 1070384291
TIMEZONE = ZoneInfo("Asia/Riyadh")

logging.basicConfig(level=logging.INFO)

# هذا اللي يرد في الخاص
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("هلا والله! البوت فغال ✅\nارسل /start")

async def main():
    print("Bot is Alive - فغال ✅")
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN مو موجود!")
        return
    app = Application.builder().token(BOT_TOKEN).build()
    
    # نضيف الاوامر
    app.add_handler(CommandHandler("start", start))
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    print("البوت فغال الحين")
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
