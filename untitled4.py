import os
import telebot
from telebot import types
from tradingview_ta import TA_Handler, Interval
from flask import Flask
from threading import Thread
import datetime
import pytz
import time

TOKEN = "8842616064:AAEwDgWLmufrPcsvOoB-LNXIOL2O2dXehB8"
bot = telebot.TeleBot(TOKEN)

def get_jeddah_time():
    jeddah_tz = pytz.timezone('Asia/Riyadh')
    return datetime.datetime.now(jeddah_tz).strftime("%I:%M:%S %p")

# القائمة الأساسية للتحليل (بدون أعلام لضمان دقة السحب)
SYMBOLS_LIST = [
    "AUDCHF", "CADCHF", "CHFJPY", "EURUSD", "EURJPY", 
    "AUDUSD", "USDCHF", "EURAUD", "AUDJPY", "CADJPY", 
    "EURCHF", "USDJPY", "AUDCAD"
]
is_auto_running = True 
MY_CHAT_ID = "ضع_رقم_الـ_ID_هنا" 

def get_analysis(symbol):
    try:
        handler = TA_Handler(symbol=symbol, screener="forex", exchange="OANDA", interval=Interval.INTERVAL_1_MINUTE)
        analysis = handler.get_analysis()
        osc = analysis.oscillators['RECOMMENDATION']
        mov = analysis.moving_averages['RECOMMENDATION']
        if osc == "BUY" and mov == "BUY": return "🟢 CALL UP ⬆️"
        elif osc == "SELL" and mov == "SELL": return "🔴 PUT DOWN ⬇️"
        else: return "⚪ NEUTRAL"
    except: return "ERROR"

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is running!"
def run_web(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def auto_monitor():
    while True:
        if is_auto_running:
            for symbol in SYMBOLS_LIST:
                signal = get_analysis(symbol)
                if signal in ["🟢 CALL UP ⬆️", "🔴 PUT DOWN ⬇️"]:
                    text = f"🤖 Auto Signal\n📊 {symbol}\n⏰ {get_jeddah_time()}\n⏳ 1 Minute\n🎯 {signal}"
                    try: bot.send_message(MY_CHAT_ID, text)
                    except: pass
                time.sleep(5) 
            time.sleep(30) 

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    # قائمة الأزرار مع الأعلام
    buttons_text = [
        "AUDCHF 🇦🇺🇨🇭", "CADCHF 🇨🇦🇨🇭", "CHFJPY 🇨🇭🇯🇵", "EURUSD 🇪🇺🇺🇸", 
        "EURJPY 🇪🇺🇯🇵", "AUDUSD 🇦🇺🇺🇸", "USDCHF 🇺🇸🇨🇭", "EURAUD 🇪🇺🇦🇺", 
        "AUDJPY 🇦🇺🇯🇵", "CADJPY 🇨🇦🇯🇵", "EURCHF 🇪🇺🇨🇭", "USDJPY 🇺🇸🇯🇵", "AUDCAD 🇦🇺🇨🇦"
    ]
    # هنا الكود يأخذ اسم العملة فقط من النص (تجاهل العلم) ليعمل التحليل
    buttons = [types.InlineKeyboardButton(text=t, callback_data=t.split()[0]) for t in buttons_text]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "🚀 اختر سوقاً للتحليل اللحظي:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    signal = get_analysis(call.data)
    text = f"📊 {call.data}\n⏰ {get_jeddah_time()}\n⏳ 1 Minute\n🎯 {signal}"
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id)

if __name__ == "__main__":
    Thread(target=run_web).start()
    Thread(target=auto_monitor, daemon=True).start()
    bot.infinity_polling()
