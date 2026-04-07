import os
import telebot
from groq import Groq
from flask import Flask
import threading

# 1. Мини-сайт для Render
app = Flask('')
@app.route('/')
def home():
    return "Groq Bot is Live!"

def run_flask():
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))

# 2. Настройка Groq и Бота
client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Теперь я работаю на Groq. Спрашивай!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": message.text}],
            model="llama-3.3-70b-versatile",
        )
        bot.reply_to(message, chat_completion.choices[0].message.content)
    except Exception as e:
        bot.reply_to(message, f"Ошибка Groq: {str(e)[:100]}")

# 3. Запуск
# ... (весь твой предыдущий код остается выше)

# 3. Запуск всего вместе
if __name__ == "__main__":
    # Сначала запускаем сайт для Render в отдельном потоке
    threading.Thread(target=run_flask).start()
    print("Бот на Groq запущен...")
    
    # ОЧИСТКА: Удаляем старые зависшие запросы (решает ошибку 409)
    bot.remove_webhook(drop_pending_updates=True) 
    
    # ЗАПУСК: Бесконечный опрос серверов Telegram
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
