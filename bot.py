import telebot
from tradingview_ta import TA_Handler, Interval, Exchange

# ضع التوكن الخاص بك هنا
TOKEN = "8977128074:AAHxKZtQbk10d9JBWU3zgrs07JH1vk6_VBs"
bot = telebot.TeleBot(TOKEN)

# هذا السطر ينهي مشكلة الـ Conflict التي كانت تظهر في السجلات
bot.remove_webhook()

# دالة لجلب الإشارات
def get_signal(chat_id, symbol, exchange, screener):
    try:
        handler = TA_Handler(
            symbol=symbol,
            screener=screener,
            exchange=exchange,
            interval=Interval.INTERVAL_1_MINUTE
        )
        analysis = handler.get_analysis()
        osc = analysis.oscillators['RECOMMENDATION']
        mov = analysis.moving_averages['RECOMMENDATION']
        
        msg = f"📊 {symbol} ({exchange})\n"
        if osc == "BUY" or mov == "BUY":
            msg += "🟢 إشارة شراء (Buy Signal)"
        elif osc == "SELL" or mov == "SELL":
            msg += "🔴 إشارة بيع (Sell Signal)"
        else:
            msg += "⚠️ السوق هادئ حالياً"
        
        bot.send_message(chat_id, msg)
    except:
        pass

# الأوامر
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك في MADTrSignal! استخدم الأوامر:\n/btc - للبيتكوين\n/gold - للذهب\n/eurusd - لليورو دولار")

@bot.message_handler(commands=['btc'])
def btc_signal(message):
    get_signal(message.chat.id, "BTCUSD", "BINANCE", "crypto")

@bot.message_handler(commands=['gold'])
def gold_signal(message):
    get_signal(message.chat.id, "XAUUSD", "FX_IDC", "forex")

@bot.message_handler(commands=['eurusd'])
def eurusd_signal(message):
    get_signal(message.chat.id, "EURUSD", "FX_IDC", "forex")

if __name__ == "__main__":
    print("MADTr AI Started...")
    bot.infinity_polling()
