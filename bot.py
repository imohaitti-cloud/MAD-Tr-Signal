import os
import telebot
from flask import Flask, request
from tradingview_ta import TA_Handler, Interval

TOKEN = os.environ.get("API_TOKEN")
# رابط موقعك على Render (يجب أن ينتهي بـ .onrender.com)
WEBHOOK_URL = os.environ.get("WEBHOOK_URL") 

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# [هنا تضع دالة get_signal التي كتبناها سابقاً]
def get_signal(chat_id, symbol):
    try:
        handler = TA_Handler(symbol=symbol, screener="forex", exchange="FX_IDC", interval=Interval.INTERVAL_1_MINUTE)
        analysis = handler.get_analysis()
        osc = analysis.oscillators['RECOMMENDATION']
        mov = analysis.moving_averages['RECOMMENDATION']
        if osc == "BUY" or mov == "BUY":
            bot.send_message(chat_id, f"MADTrSignal 🚀\n📊 {symbol}\n🟢 إشارة شراء (Buy Signal)")
        elif osc == "SELL" or mov == "SELL":
            bot.send_message(chat_id, f"MADTrSignal 🚀\n📊 {symbol}\n🔴 إشارة بيع (Sell Signal)")
        else:
            bot.send_message(chat_id, f"📊 {symbol}\n⚠️ السوق هادئ جداً حالياً.")
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ خطأ: {str(e)[:50]}")

# معالجة الطلبات
@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '!', 200

# إعداد الويب هوك (يتم تشغيله مرة واحدة)
@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + '/' + TOKEN)
    return "Webhook set!", 200

@app.route('/')
def home():
    return "Bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
