import os
import telebot
import google.generativeai as genai

# Загрузка ключей
BOT_TOKEN = os.environ.get('BOT_TOKEN')
AI_KEY = os.environ.get('AI_KEY')

# Настройка ИИ
genai.configure(api_key=AI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Я готов! Спрашивай что угодно.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # Проверка ключа перед отправкой
        if not AI_KEY:
            bot.reply_to(message, "Ошибка: Не найден AI_KEY в настройках Render!")
            return
            
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        # Бот сам напишет, в чем именно проблема
        error_text = str(e)
        if "API_KEY_INVALID" in error_text:
            bot.reply_to(message, "Ошибка: Твой ключ Gemini (AI_KEY) неверный.")
        else:
            bot.reply_to(message, f"Ошибка ИИ: {error_text[:100]}")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.polling(none_stop=True)
