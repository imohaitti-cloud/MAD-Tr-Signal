import os
from flask import Flask
from threading import Thread
import telebot

# إعداد خادم ويب بسيط لإبقاء البوت نشطاً
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# تشغيل خادم الويب
keep_alive()

# إعداد البوت
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "البوت يعمل الآن بنجاح!")

# تشغيل البوت
bot.polling()
