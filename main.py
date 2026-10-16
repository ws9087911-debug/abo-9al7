import os, time, requests
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
app = Flask(__name__)

@app.route('/')
def home(): return "V9 LIVE - Tawfiq Bot"

# الاسواق اللي نفحصها
MARKETS = ["Gold", "Silver", "Camel Race Index", "US 500", "US Tech 100", "Volatility 100"]

def get_signal(market):
    try:
        # محاكاة سعر + تحليل - تقدر تربطه بـ API حقيقي بعدين
        import random
        price = round(random.uniform(1.0, 2000.0), 6)
        ema9 = random.uniform(price*0.99, price*1.01)
        ema21 = random.uniform(price*0.98, price*1.02)
        rsi = random.uniform(15, 85)

        if ema9 > ema21 and 25 < rsi < 75:
            status = "🟢 شراء"
            reason = f"EMA9 فوق EMA21\nRSI {rsi:.1f} - ممتاز"
        elif ema9 < ema21 and 25 < rsi < 75:
            status = "🔴 بيع"
            reason = f"EMA21 فوق EMA9\nRSI {rsi:.1f} - فرصة بيع"
        else:
            status = "⛔ انتظار"
            reason = f"هابط EMA21 تحت EMA9\nRSI {rsi:.1f}"
        
        # V9 ميزة: اذا انتظار ندور سوق ثاني تلقائي
        return price, status, reason, rsi, ema9, ema21
    except:
        return 0, "⛔", "خطأ", 50, 0, 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(m, callback_data=f"market_{m}")] for m in MARKETS]
    keyboard.append([InlineKeyboardButton("🔍 فحص سريع لكل الاسواق", callback_data="scan_all")])
    await update.message.reply_text("🔥 **Tawfiq V9 - اختر السوق:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "scan_all":
        text = "🔍 **فحص V9 السريع:**\n\n"
        best = None
        for m in MARKETS:
            price, status, reason, rsi, _, _ = get_signal(m)
            emoji = "✅" if "شراء" in status or "بيع" in status else "⏳"
            text += f"{emoji} {m}: {status}\n"
            if "شراء" in status and best is None:
                best = m
        if best:
            text += f"\n🎯 **افضل فرصة: {best}**"
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("تحديث", callback_data="scan_all")]]), parse_mode='Markdown')
        return

    market = data.replace("market_", "")
    price, status, reason, rsi, ema9, ema21 = get_signal(market)

    msg = f"📊 {market} | 1m\nالسعر {price}\n\n{status}\nالسبب:\n{reason}\n\nRSI {rsi:.1f} - المؤشر يلحق الان انتظر"
    
    keyboard = [
        [InlineKeyboardButton("تحديث", callback_data=f"market_{market}"), InlineKeyboardButton("سوق ثاني", callback_data="back")],
        [InlineKeyboardButton("🔍 فحص كل الاسواق", callback_data="scan_all")]
    ]
    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    # ميزة V9: اذا انتظار اقترح سوق ثاني تلقائي
    if "انتظار" in status:
        await context.bot.send_message(chat_id=query.message.chat_id, text=f"⏳ {market} انتظار - جرب تفحص الكل 👆")

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton(m, callback_data=f"market_{m}")] for m in MARKETS]
    keyboard.append([InlineKeyboardButton("🔍 فحص سريع لكل الاسواق", callback_data="scan_all")])
    await query.edit_message_text("اختر سوق ثاني:", reply_markup=InlineKeyboardMarkup(keyboard))

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler, pattern="^market_|^scan_all"))
    application.add_handler(CallbackQueryHandler(back_handler, pattern="^back"))
    # شغل البوت
    application.run_polling()
