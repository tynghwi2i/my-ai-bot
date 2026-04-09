import os
import telebot
import threading
import psycopg2
from flask import Flask
from groq import Groq
from duckduckgo_search import DDGS

# 1. Настройка Flask для Render
app = Flask('')

@app.route('/')
def home():
    return "Бот с SQL и Поиском активен!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# 2. Инициализация API
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
bot = telebot.TeleBot(os.environ.get("BOT_TOKEN"))
DB_URL = os.environ.get("DATABASE_URL")

# 3. Работа с Базой Данных (SQL)
def init_db():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS messages 
                   (id SERIAL PRIMARY KEY, user_id BIGINT, role TEXT, content TEXT)''')
    conn.commit()
    cur.close()
    conn.close()

def save_message(user_id, role, content):
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("INSERT INTO messages (user_id, role, content) VALUES (%s, %s, %s)", (user_id, role, content))
    conn.commit()
    cur.close()
    conn.close()

def get_history(user_id, limit=10):
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("SELECT role, content FROM messages WHERE user_id = %s ORDER BY id DESC LIMIT %s", (user_id, limit))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"role": r, "content": c} for r, c in reversed(rows)]

# 4. Функция поиска в интернете
def search_internet(query):
    try:
        results = DDGS().text(query, max_results=3)
        return "\n".join([f"{r['title']}: {r['body']}" for r in results])
    except:
        return "Поиск временно недоступен."

# 5. Обработка сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    text = message.text

    # Если спрашиваешь про новости или курс - бот поищет в сети
    search_keywords = ['найди', 'новости', 'сегодня', 'курс', 'погода']
    context_info = ""
    if any(word in text.lower() for word in search_keywords):
        context_info = f"\nАктуально на сегодня: {search_internet(text)}"

    save_message(user_id, "user", text)
    history = get_history(user_id)
    
    messages = [{"role": "system", "content": f"Ты ассистент Артура. Сегодня 9 апреля 2026 года. {context_info}"}] + history

    try:
        completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
        )
        response = completion.choices[0].message.content
        bot.reply_to(message, response)
        save_message(user_id, "assistant", response)
    except Exception as e:
        bot.reply_to(message, "Ошибка в работе мозга бота.")

# 6. Запуск
if __name__ == "__main__":
    init_db()
    threading.Thread(target=run_flask).start()
    bot.remove_webhook(drop_pending_updates=True)
    bot.infinity_polling(timeout=20)
