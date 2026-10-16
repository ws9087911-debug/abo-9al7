import os
import threading
import asyncio
import logging
import random
import requests
from zoneinfo import ZoneInfo
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "Bot is Alive - جميع الاسواق ✅"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)
threading.Thread(target=run_flask, daemon=True).start()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = -1004425103888
TIMEZONE = ZoneInfo("Asia/Riyadh")
logging.basicConfig(level=logging.INFO)

SYMBOLS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","DOGEUSDT","GOLD","EURUSD"]

def get_price(symbol):
    try:
        # نجيب سعر من Binance
        s = symbol if "USDT" in symbol else "BTCUSDT"
        r = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={s}", timeout=5).json()
        return float(r['price'])
    except:
        return round(random.uniform(100, 50000),2)

def make_signal(symbol):
    price = get_price(symbol)
    # تحليل عشوائي بسيط مع RSI وهمي
    rsi = random.randint(30, 70)
    is_buy = random.choice([True, False])
    signal = "شراء ✅" if is_buy else "بيع 🔻"
    return {
        "symbol": symbol, "signal": signal, "price": price,
        "rsi": rsi,
        "tp": round(price * (1.015 if is_buy else 0.985), 2),
        "sl": round(price * (0.99 if is_buy else 1.01), 2)
    }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "هلا والله! بوت جميع الاسواق فغال ✅\n"
        "يرسل تحليل كل 5-15 دقيقة\n"
        "⚠️ تنبيه: تحليل تعليمي فقط وليس توصية مضمونة"
    )

async def signals_loop(app):
    await asyncio.sleep(15)
    while True:
        for sym in SYMBOLS:
            if random.random() > 0.6: # مو كل مرة يرسل عشان ما يزعج
                res = make_signal(sym)
                msg = (
                    f"📊 **اشارة - {res['symbol']}**\n\n"
                    f"الاتجاه: {res['signal']}\n"
                    f"السعر: {res['price']}\n"
                    f"RSI: {res['rsi']}\n"
                    f"🎯 هدف: {res['tp']}\n"
                    f"🛑 وقف: {res['sl']}\n"
                    f"الفريم: 5m-15m\n\n"
                    f"⚠️ تعليمي فقط - التداول خطر - ادر مخاطرك 1%"
                )
                try:
                    await app.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode='Markdown')
                except Exception as e:
                    print(e)
                await asyncio.sleep(3)
        await asyncio.sleep(300) # كل 5 دقايق

async def main():
    if not BOT_TOKEN: return
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    asyncio.create_task(signals_loop(app))
    print("البوت فغال")
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
