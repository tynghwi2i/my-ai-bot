import os
import telebot
import google.generativeai as genai

# Эти ключи мы добавим позже в настройках хостинга
BOT_TOKEN = os.environ.get('BOT_TOKEN')
AI_KEY = os.environ.get('AI_KEY')

# Настройка ИИ Gemini
genai.configure(api_key=AI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Настройка бота
bot = telebot.TeleBot(BOT_TOKEN)

# Ответ на команду /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я твой умный ИИ помощник. Спрашивай что угодно!")

# Ответ на любые текстовые сообщения
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # Отправляем запрос в нейросеть
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "Произошла ошибка, попробуй позже.")

# Запуск бота
if __name__ == "__main__":
    bot.remove_webhook()
bot.polling(none_stop=True)


