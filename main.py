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

API_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    
# === Универсальная функция для обращения к Yandex LLM ===
def call_yandex_llm(prompt: str, user_text: str) -> str:
    """
    Отправляет текст и промпт в Yandex LLM и возвращает сгенерированный ответ.
    """
    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "modelUri": f"gpt://{folder_id}/yandexgpt-lite/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.3,
            "maxTokens": 500,
        },
        "messages": [
            {"role": "system", "text": prompt},
            {"role": "user", "text": user_text},
        ],
    }

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(data))
        result = response.json()
        answer_text = result["result"]["alternatives"][0]["message"]["text"].strip()
        return answer_text
    except Exception as e:
        print("Ошибка при обращении к Yandex API:", e)
        return "Ошибка: не удалось получить ответ от модели."


# === Проверка сообщения пользователя ===
def check_message(user_text: str) -> bool:
    """
    Проверяет сообщение пользователя на связность и допустимость.
    Возвращает True, если сообщение валидно, иначе False.
    """
    prompt = (
        "Действуй по шагам. "
        "Оцени сообщение от пользователя. Проверь на связность, наличие оскорблений, мат, "
        "непристойные и недопустимые темы. "
        "Если сообщение связное, состоит более чем из одного предложения и не содержит запрещенных тем, "
        "напиши в результате True. В ином случае напиши в результате False."
    )

    result = call_yandex_llm(prompt, user_text)
    return "true" in result.lower()


# === Валидация программы по фреймворку 4C/ID ===
def fourcid_validator(program_text: str) -> str:
    """
    Анализирует образовательную программу по модели 4C/ID.
    Возвращает рекомендации и аудит структуры.
    """
    prompt = (
        "Действуй как опытный методист и learning experience designer. "
        "У тебя огромный опыт в проектировании образовательных программ по фреймворку 4C/ID. "
        "Ты досканально знаешь и умеешь применять на практике приемы и советы из книги "
        "«Десять шагов комплексного обучения. Четырехкомпонентная модель дизайна обучения». "
        "Проведи аудит программы и дай рекомендации в формате: что соответствует модели 4C/ID, "
        "чего не хватает. Структурируй информацию, полученную от пользователя, "
        "по всем стандартам модели, подсветив недостающие пробелы. Обязательно оценивай соответсвие прогаммы цели обучения." 
        "В конце дай общую оценку программе по шкале от 1 до 10, где 10 - полностью соответствует модели 4C/ID."
    )

    result = call_yandex_llm(prompt, program_text)
    return result


# === Обработчик сообщений пользователя ===
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_text = message.text

    bot.send_message(message.chat.id, "Проверяю сообщение...")

    # Проверяем сообщение на допустимость
    if check_message(user_text):
        bot.send_message(message.chat.id, "Сообщение принято. Выполняю анализ по модели 4C/ID...")
        result = fourcid_validator(user_text)
        bot.send_message(message.chat.id, result)
    else:
        bot.send_message(message.chat.id, "Извините, что-то пошло не так. Ваше сообщение отклонено.")


# Запускаем бесконечный опрос сервера Telegram
bot.polling(none_stop=True)
