import os
import telebot
from telebot import types
from tradingview_ta import TA_Handler, Interval
from flask import Flask
from threading import Thread
import datetime
import time

TOKEN = "8842616064:AAEwDgWLmufrPcsvOoB-LNXIOL2O2dXehB8"
bot = telebot.TeleBot(TOKEN)

# إعداد المراقبة التلقائية
AUTO_SYMBOL = "EURUSD" # يمكنك تغيير هذا السوق لاحقاً
is_auto_running = True 

# التحليل الفني (النسخة القوية التي اتفقنا عليها)
def get_analysis(symbol):
    try:
        handler = TA_Handler(symbol=symbol, screener="forex", exchange="OANDA", interval=Interval.INTERVAL_1_MINUTE)
        analysis = handler.get_analysis()
        osc = analysis.oscillators['RECOMMENDATION']
        mov = analysis.moving_averages['RECOMMENDATION']
        
        if osc == "BUY" and mov == "BUY": return "🟢 CALL UP ⬆️"
        elif osc == "SELL" and mov == "SELL": return "🔴 PUT DOWN ⬇️"
        else: return "NEUTRAL"
    except: return "ERROR"

# خادم الويب
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is running!"
def run_web(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# المراقبة التلقائية في الخلفية
def auto_monitor():
    while True:
        if is_auto_running:
            signal = get_analysis(AUTO_SYMBOL)
            if signal in ["🟢 CALL UP ⬆️", "🔴 PUT DOWN ⬇️"]:
                next_time = (datetime.datetime.now() + datetime.timedelta(minutes=1)).strftime("%I:%M %p")
                text = f"🤖 Auto Signal\n📊 {AUTO_SYMBOL}\n⏰ {next_time}\n⏳ 1 Minutes\n🎯 {signal}"
                # استبدل YOUR_CHAT_ID برقم معرفك الخاص (Telegram ID)
                try: bot.send_message("8842616064", text)
                except: pass
            time.sleep(60) # فحص كل دقيقة

# الأوامر اليدوية
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    # أضف الأسواق التي تريدها هنا
    buttons = [types.InlineKeyboardButton("EUR/USD", callback_data="EURUSD"), 
               types.InlineKeyboardButton("GBP/USD", callback_data="GBPUSD")]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "🚀 اختر سوقاً للتحليل اليدوي:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    signal = get_analysis(call.data)
    next_time = (datetime.datetime.now() + datetime.timedelta(minutes=1)).strftime("%I:%M %p")
    text = f"📊 {call.data}\n⏰ {next_time}\n⏳ 1 Minutes\n🎯 {signal}"
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id)

if __name__ == "__main__":
    Thread(target=run_web).start()
    Thread(target=auto_monitor, daemon=True).start() # تشغيل المراقبة التلقائية
    bot.infinity_polling()
