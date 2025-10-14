import telebot
from dotenv import load_dotenv
import os
import requests
import json

# Загружаем переменные из .env
load_dotenv()

tg_key = os.getenv("TG_TOKEN")
YANDEX_API_KEY = os.getenv("api_key")
MODEL_URI = os.getenv("YA_LLM_URL") 
folder_id = os.getenv("folder_id")


# Создаем экземпляр бота
bot = telebot.TeleBot(tg_key)

def check_message_with_yandex(user_text: str) -> bool:
    """
    Отправляет текст пользователя в Yandex LLM API для проверки.
    Возвращает True, если сообщение допустимо, иначе False.
    """
    prompt = (
        "Действуй по шагам. "
        "Оцени сообщение от пользователя. Проверь на связность, наличие оскорблений, мат, "
        "непристойные и недопустимые темы. "
        "Если сообщение связное, состоит более чем из одного предложения и не содержит запрещенных тем, "
        "напиши в результате True. В ином случае напиши в результате False."
    )

    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "modelUri": f"gpt://{folder_id}/yandexgpt-lite/latest",  
        "completionOptions": {
            "stream": False,
            "temperature": 0,
            "maxTokens": 100,
        },
        "messages": [
            {"role": "system", "text": prompt},
            {"role": "user", "text": user_text},
        ],
    }

    try:
        response = requests.post(MODEL_URI, headers=headers, data=json.dumps(data))
        result = response.json()

        # Извлекаем текст из ответа модели
        answer_text = result["result"]["alternatives"][0]["message"]["text"].strip()
        
        print(answer_text)
        
        # Проверяем, есть ли "True" в ответе
        return "true" in answer_text.lower()

    except Exception as e:
        print("Ошибка при обращении к Yandex API:", e)
        return False


# Обработчик сообщений пользователей
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_text = message.text

    # Проверяем сообщение через Yandex API
    is_valid = check_message_with_yandex(user_text)

    if is_valid:
        bot.send_message(message.chat.id, user_text)
    else:
        bot.send_message(message.chat.id, "Извините, что-то пошло не так. Ваше сообщение отклонено.")

# Запускаем бесконечный опрос сервера Telegram
bot.polling(none_stop=True)
