import telebot
import logging
from tradingview_ta import TA_Handler, Interval

# ============================================
# MADTr Signal Bot
# ============================================

TOKEN = "8977128074:AAHxKZtQbk10d9JBWU3zgrs07JH1vk6_VBs"

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

logging.basicConfig(level=logging.INFO)

# ============================================
# تحليل السوق
# ============================================

def analyze_market(symbol, exchange, screener):
    try:

        handler = TA_Handler(
            symbol=symbol,
            exchange=exchange,
            screener=screener,
            interval=Interval.INTERVAL_1_MINUTE
        )

        analysis = handler.get_analysis()

        osc = analysis.oscillators["RECOMMENDATION"]
        ma = analysis.moving_averages["RECOMMENDATION"]
        summary = analysis.summary["RECOMMENDATION"]

        buy = analysis.summary["BUY"]
        sell = analysis.summary["SELL"]
        neutral = analysis.summary["NEUTRAL"]

        confidence = round(
            max(buy, sell) /
            (buy + sell + neutral) * 100
        )

        return {
            "summary": summary,
            "osc": osc,
            "ma": ma,
            "buy": buy,
            "sell": sell,
            "neutral": neutral,
            "confidence": confidence
        }

    except Exception as e:
        logging.error(e)
        return None

# ============================================
# إرسال الإشارة
# ============================================

def send_signal(chat_id, symbol, exchange, screener):

    result = analyze_market(symbol, exchange, screener)

    if result is None:
        return

    summary = result["summary"]
    confidence = result["confidence"]

    if summary in ["BUY", "STRONG_BUY"]:
        icon = "🟢"
        signal = "BUY"

    elif summary in ["SELL", "STRONG_SELL"]:
        icon = "🔴"
        signal = "SELL"

    else:
        icon = "🟡"
        signal = "WAIT"

    message = f"""
<b>📊 MADTr AI SIGNAL</b>

━━━━━━━━━━━━━━━

💱 <b>Market:</b> {symbol}

📈 <b>Signal:</b> {icon} {signal}

🎯 <b>Confidence:</b> {confidence}%

━━━━━━━━━━━━━━━

📊 <b>Indicators</b>

Oscillators : <b>{result['osc']}</b>

Moving Avg : <b>{result['ma']}</b>

Summary : <b>{summary}</b>

━━━━━━━━━━━━━━━

🟢 BUY : {result['buy']}
🔴 SELL : {result['sell']}
⚪ Neutral : {result['neutral']}

━━━━━━━━━━━━━━━

🤖 Powered By MADTr AI
"""

    bot.send_message(chat_id, message)

# ============================================
# Start
# ============================================

@bot.message_handler(commands=["start"])
def start(message):

    text = """
<b>🤖 Welcome to MADTr AI</b>

اختر السوق:

/btc
/gold
/eurusd
"""

    bot.send_message(message.chat.id, text)

# ============================================
# BTC
# ============================================

@bot.message_handler(commands=["btc"])
def btc(message):
    send_signal(
        message.chat.id,
        "BTCUSDT",
        "BINANCE",
        "crypto"
    )

# ============================================
# GOLD
# ============================================

@bot.message_handler(commands=["gold"])
def gold(message):
    send_signal(
        message.chat.id,
        "XAUUSD",
        "FX_IDC",
        "forex"
    )

# ============================================
# EURUSD
# ============================================

@bot.message_handler(commands=["eurusd"])
def eurusd(message):
    send_signal(
        message.chat.id,
        "EURUSD",
        "FX_IDC",
        "forex"
    )

# ============================================
# تشغيل البوت
# ============================================

print("MADTr AI Started...")

bot.infinity_polling(skip_pending=True)
