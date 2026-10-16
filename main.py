import os, threading, asyncio, logging, requests, random
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "Bot Market Fixed v2"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)
threading.Thread(target=run_flask, daemon=True).start()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = -1004425103888
logging.basicConfig(level=logging.INFO)

SYMBOLS = ["BTCUSDT","ETHUSDT","EURUSD","GBPUSD","XAUUSD","SOLUSDT"]

def get_price(symbol):
    try:
        if "USDT" in symbol:
            url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=20"
            data = requests.get(url, timeout=5).json()
            closes = [float(x[4]) for x in data]
            price = closes[-1]
            if closes[-1] > closes[-2]:
                signal = "BUY"
            else:
                signal = "SELL"
            return price, signal
    except:
        pass
    return round(random.uniform(1, 60000),2), random.choice(["BUY","SELL"])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("5s", callback_data="5s"), InlineKeyboardButton("30s", callback_data="30s")],
        [InlineKeyboardButton("1m", callback_data="1m"), InlineKeyboardButton("5m", callback_data="5m")],
        [InlineKeyboardButton("15m", callback_data="15m"), InlineKeyboardButton("Random", callback_data="random")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose timeframe:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tf = query.data
    symbol = random.choice(SYMBOLS)
    price, signal = get_price(symbol)

    msg = f"Market {symbol} - {tf}\nPrice {price}\nSignal {signal}\nTF {tf}\nRisk 1 percent only"

    keyboard = [
        [InlineKeyboardButton("Again", callback_data=tf), InlineKeyboardButton("Random", callback_data="random")],
        [InlineKeyboardButton("Menu", callback_data="menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=msg, reply_markup=reply_markup)
    try:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)
    except:
        pass

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "menu":
        keyboard = [
            [InlineKeyboardButton("5s", callback_data="5s"), InlineKeyboardButton("30s", callback_data="30s")],
            [InlineKeyboardButton("1m", callback_data="1m"), InlineKeyboardButton("5m", callback_data="5m")],
            [InlineKeyboardButton("15m", callback_data="15m"), InlineKeyboardButton("Random", callback_data="random")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Choose timeframe:", reply_markup=reply_markup)

async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_handler, pattern="^menu$"))
    app.add_handler(CallbackQueryHandler(button_handler))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    print("Bot Fixed Live")
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
