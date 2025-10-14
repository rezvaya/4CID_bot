import telebot
from dotenv import load_dotenv
import os

# Загружаем переменные из .env
load_dotenv()

tg_key = os.getenv("TG_TOKEN")

# Создаем экземпляр бота
bot = telebot.TeleBot(tg_key)

# Обработчик всех входящих сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Отправляем ответ пользователю
    bot.reply_to(message, "Принято")

# Запускаем бесконечный опрос сервера Telegram
bot.polling(none_stop=True)
