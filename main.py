import os, asyncio, logging
from zoneinfo import ZoneInfo
from telegram.ext import Application

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = -1004425103888
ADMIN_USER_ID = 1070384291
TIMEZONE = ZoneInfo("Asia/Riyadh")

logging.basicConfig(level=logging.INFO)

async def main():
    print("Bot is Alive - شغال ✅")
    app = Application.builder().token(BOT_TOKEN).build()
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    print("البوت شغال الحين")
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
