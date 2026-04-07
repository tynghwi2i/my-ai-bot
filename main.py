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

        # Отправляем запрос в нейросеть
        @bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        print(f"Ошибка ИИ: {e}") # Это появится в логах Render
        bot.reply_to(message, f"Ошибка: {str(e)[:50]}...") 

# Запуск бота
    # Удаляем старые привязки и запускаем
if __name__ == "__main__":
    bot.remove_webhook()
    print("Бот запущен...")
    bot.polling(none_stop=True)



