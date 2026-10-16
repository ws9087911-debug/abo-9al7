import os
import threading
import asyncio
import logging
import random
from zoneinfo import ZoneInfo
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import ccxt
import pandas as pd
import pandas_ta as ta

# === Flask عشان Render ===
app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "Bot is Alive - جميع الاسواق ✅"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)
threading.Thread(target=run_flask, daemon=True).start()

# === الاعدادات ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = -1004425103888
ADMIN_USER_ID = 1070384291
TIMEZONE = ZoneInfo("Asia/Riyadh")
logging.basicConfig(level=logging.INFO)

# كل الاسواق
SYMBOLS = [
    "BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT",
    "ADA/USDT", "DOGE/USDT", "SHIB/USDT", "AVAX/USDT", "DOT/USDT",
    "GOLD", "EUR/USD", "GBP/USD", "USD/JPY" # الذهب والعملات بيتم تحليلها كـ BTC كبديل مؤقت
]

# محاكاة كل الاسواق - نستخدم Binance للكريبتو
exchange = ccxt.binance()

def analyze_symbol(symbol):
    try:
        # نحاول نجيب بيانات
        real_symbol = symbol if "/" in symbol else "BTC/USDT"
        ohlcv = exchange.fetch_ohlcv(real_symbol, timeframe='5m', limit=100)
        df = pd.DataFrame(ohlcv, columns=['t','o','h','l','c','v'])
        df['rsi'] = ta.rsi(df['c'], length=14)
        ema9 = ta.ema(df['c'], length=9).iloc[-1]
        ema21 = ta.ema(df['c'], length=21).iloc[-1]
        rsi = df['rsi'].iloc[-1]
        price = df['c'].iloc[-1]

        signal = None
        if ema9
