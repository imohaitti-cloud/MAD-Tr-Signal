import os
import telebot
from telebot import types
from tradingview_ta import TA_Handler, Interval
import time
from threading import Thread

# سحب التوكن من إعدادات Render
TOKEN = os.environ.get("API_TOKEN")
bot = telebot.TeleBot(TOKEN)

# تخزين السوق الذي اختاره المستخدم
user_market = {}

SYMBOLS = {
    "EUR/USD 🇪🇺🇺🇸": "EURUSD",
    "GBP/USD 🇬🇧🇺🇸": "GBPUSD",
    "USD/JPY 🇺🇸🇯🇵": "USDJPY",
    "AUD/USD 🇦🇺🇺🇸": "AUDUSD"
}

def monitor_market(chat_id):
    while user_market.get(chat_id):
        symbol = user_market[chat_id]
        try:
            handler = TA_Handler(symbol=symbol, screener="forex", exchange="FOREX", interval=Interval.INTERVAL_1_MINUTE)
            analysis = handler.get_analysis()
            osc = analysis.oscillators['RECOMMENDATION']
            mov = analysis.moving_averages['RECOMMENDATION']

            if osc == "BUY" and mov == "BUY":
                bot.send_message(chat_id, f"MADTrSignal 🚀\n📊 {symbol}\n🟢 STRONG BUY ⬆️")
            elif osc == "SELL" and mov == "SELL":
                bot.send_message(chat_id, f"MADTrSignal 🚀\n📊 {symbol}\n🔴 STRONG SELL ⬇️")
            
            time.sleep(60) 
        except:
            time.sleep(10)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    for name, sym in SYMBOLS.items():
        markup.add(types.InlineKeyboardButton(name, callback_data=sym))
    markup.add(types.InlineKeyboardButton("🚫 إيقاف المراقبة", callback_data="STOP"))
    bot.send_message(message.chat.id, "Welcome to MADTrSignal 📈\nاختر السوق للبدء بالمراقبة:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "STOP":
        user_market[call.message.chat.id] = None
        bot.answer_callback_query(call.id, "تم إيقاف المراقبة")
    else:
        user_market[call.message.chat.id] = call.data
        bot.answer_callback_query(call.id, f"تم تفعيل {call.data}")
        bot.send_message(call.message.chat.id, f"✅ تم تفعيل مراقبة {call.data}..")
        Thread(target=monitor_market, args=(call.message.chat.id,)).start()

bot.infinity_polling()
