⁵import os
import telebot
import google.generativeai as genai
from flask import Flask
import threading

# 1. Создаем мини-сайт для обмана Render
app = Flask('')

@app.route('/')
def home():
    return "I am alive!"

def run_flask():
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))

# 2. Настройка ИИ и Бота
BOT_TOKEN = os.environ.get('BOT_TOKEN')
AI_KEY = os.environ.get('AI_KEY')

genai.configure(api_key=AI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-latest')
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Я готов! Спрашивай что угодно.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)[:100]}")

# 3. Запуск всего вместе
if __name__ == "__main__":
    # Сначала запускаем сайт в отдельном потоке
    threading.Thread(target=run_flask).start()
    # Затем запускаем бота
    print("Бот запущен...")
    bot.remove_webhook()
    bot.polling(none_stop=True)
