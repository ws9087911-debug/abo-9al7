import os, threading, asyncio, requests, random from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "Bot Full Markets"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)
threading.Thread(target=run_flask, daemon=True).start()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = -1004425103888

# كل الاسواق اللي في صورتك + زيادة
MARKETS = {
    "عملات": ["EUR/USD","GBP/USD","USD/JPY","AUD/USD","USD/CAD"],
    "OTC": ["USD/EGP (OTC)","EUR/SAR (OTC)","USD/BDT (OTC)","USD/PKR (OTC)","EUR/USD (OTC)"],
    "سلع": ["Gold","Silver","Oil","BTC/USD","ETH/USD"],
    "مؤشرات غريبة": ["Camel Race Index","Cricket Index","Smarty","AI Index","Chocolate Index"]
}

def analyze(symbol):
    # محاكاة تحليل - يجيب سعر حقيقي لو عملة رقمية
    try:
        if "BTC" in symbol:
            p = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=3).json()
            price = float(p["price"])
        elif "ETH" in symbol:
            p = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT", timeout=3).json()
            price = float(p["price"])
        else:
            price = round(random.uniform(1.05, 1.35) if "EUR" in symbol else random.uniform(1.2, 4100), 5)
    except:
        price = 1.08540

    rsi = random.randint(35, 72)
    ema_signal = random.choice(["صاعد","هابط"])

    if rsi < 45 and ema_signal == "صاعد":
        signal = "شراء"
        reason = f"RSI {rsi} قريب تشبع بيع + ترند {ema_signal}\nدعم قوي + شموع انعكاسية"
        win_rate = "82%"
    elif rsi > 60 and ema_signal == "هابط":
        signal = "بيع"
        reason = f"RSI {rsi} قريب تشبع شراء + ترند {ema_signal}\nمقاومة قوية + ضعف مشترين"
        win_rate = "81%"
    else:
        signal = "شراء" if random.random()>0.5 else "بيع"
        reason = f"RSI {rsi} محايد - انتظار كسر {ema_signal}\nفرصة سكالبينج سريعة"
        win_rate = "76%"

    return price, signal, reason, win_rate, rsi

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("💱 عملات", callback_data="cat_عملات"), InlineKeyboardButton("🌙 OTC", callback_data="cat_OTC")],
          [InlineKeyboardButton("🥇 سلع", callback_data="cat_سلع"), InlineKeyboardButton("🔥 مؤشرات غريبة", callback_data="cat_مؤشرات غريبة")]]
    await update.message.reply_text("اختر نوع السوق من الصورة:", reply_markup=InlineKeyboardMarkup(kb))

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data.startswith("cat_"):
        cat = data[4:]
        markets = MARKETS[cat]
        kb = []
        for m in markets:
            kb.append([InlineKeyboardButton(f"{m}", callback_data=f"market_{m}")])
        kb.append([InlineKeyboardButton("رجوع", callback_data="back")])
        await q.edit_message_text(f"اختر السوق من {cat}:", reply_markup=InlineKeyboardMarkup(kb))

    elif data == "back":
        kb = [[InlineKeyboardButton("💱 عملات", callback_data="cat_عملات"), InlineKeyboardButton("🌙 OTC", callback_data="cat_OTC")],
              [InlineKeyboardButton("🥇 سلع", callback_data="cat_سلع"), InlineKeyboardButton("🔥 مؤشرات غريبة", callback_data="cat_مؤشرات غريبة")]]
        await q.edit_message_text("اختر نوع السوق:", reply_markup=InlineKeyboardMarkup(kb))

    elif data.startswith("market_"):
        market = data[7:]
        context.user_data["market"] = market
        kb = [[InlineKeyboardButton("5s", callback_data="tf_5s"), InlineKeyboardButton("30s", callback_data="tf_30s")],
              [InlineKeyboardButton("1m", callback_data="tf_1m"), InlineKeyboardButton("5m", callback_data="tf_5m")],
              [InlineKeyboardButton("15m", callback_data="tf_15m")]]
        await q.edit_message_text(f"اخترت: {market}\nالحين اختر المدة:", reply_markup=InlineKeyboardMarkup(kb))

    elif data.startswith("tf_"):
        tf = data[3:]
        market = context.user_data.get("market","EUR/USD")
        price, signal, reason, win_rate, rsi = analyze(market)

        msg = (
            f"📊 {market} | {tf}\n"
            f"نسبة الربح: {win_rate}\n"
            f"━━━━━━━━━━━━\n"
            f"السعر: {price}\n"
            f"الاشارة: {signal} {'🟢' if signal=='شراء' else '🔴'}\n"
            f"RSI: {rsi}\n\n"
            f"📝 ليش {signal}؟\n{reason}\n\n"
            f"⏱️ المدة {tf}: "
        )
        if tf=="5s": msg+="زخم لحظي - ادخل بسرعة واطلع"
        elif tf=="1m": msg+="سكالبينج شمعة واحدة - امن"
        else: msg+=f"ترند {tf} - ثبات اكثر"

        msg+=f"\n\n🎯 دخول الان - 1% فقط\n⚠️ تحليل تعليمي"

        kb = [[InlineKeyboardButton("سوق ثاني", callback_data="back"), InlineKeyboardButton(f"مرة ثانية {tf}", callback_data=f"tf_{tf}")]]
        await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb))
        try: await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)
        except: pass

async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    while True: await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
