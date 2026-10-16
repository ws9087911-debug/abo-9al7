import os, threading, asyncio, logging, requests, random
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "Bot Market Fixed"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)
threading.Thread(target=run_flask, daemon=True).start()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = -1004425103888
logging.basicConfig(level=logging.INFO)

SYMBOLS = ["BTCUSDT","ETHUSDT","EURUSD","GBPUSD","XAUUSD","SOLUSDT"]

def get_price_and_trend(symbol):
    try:
        if "USDT" in symbol:
            url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=20"
            data = requests.get(url, timeout=5).json()
            closes = [float(x[4]) for x in data]
            price = closes[-1]
            if closes[-1] > closes[-2] > closes[-3]:
                trend = "صاعد"
                signal = "شراء"
            elif closes[-1] < closes[-2] < closes[-3]:
                trend = "هابط"
                signal = "بيع"
            else:
                trend = "متذبذب"
                signal = random.choice(["شراء","بيع"])
            return price, trend, signal
    except: pass
    return round(random.uniform(1, 60000),5), "متذبذب", random.choice(["شراء","بيع"])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("5s trade", callback_data="5s"),
         InlineKeyboardButton("30s trade", callback_data="30s")],
        [InlineKeyboardButton("1m trade", callback_data="1m"),
         InlineKeyboardButton("5m trade", callback_data="5m")],
        [InlineKeyboardButton("15m trade", callback_data="15m"),
         InlineKeyboardButton("Random market", callback_data="random")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "هلا! اختار نوع الصفقة:\
