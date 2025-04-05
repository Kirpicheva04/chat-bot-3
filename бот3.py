import re
import random
import datetime
import webbrowser
import urllib.parse
import http.client  
import json  
import os
import spacy
from textblob import TextBlob  
from translate import Translator

API_KEY = "49c50c72eb3d82477d076bc9d0f8e5fc"  

# Загрузка модели Spacy
nlp = spacy.load("ru_core_news_sm")

# Простейший переводчик
def translate_to_english(text):
    translator = Translator(to_lang="en", from_lang="ru")
    try:
        return translator.translate(text).lower()
    except Exception as e:
        print(f"Ошибка перевода: {e}")
        return text

# Функция для анализа тональности
def analyze_sentiment(text):
    translated_text = translate_to_english(text).strip()  
    analysis = TextBlob(translated_text) 
    sentiment = analysis.sentiment.polarity  
    print(f"Тональность: {sentiment}") 
    if sentiment > 0:
        return "positive"
    elif sentiment < 0:
        return "negative"
    else:
        return "neutral"

def process_text(text):
    doc = nlp(text)
    return [token.lemma_ for token in doc if not token.is_punct and not token.is_space]

responses = {
    r"\bпривет\b": [
        "Привет!",
        "Здравствуйте!",
    ],
    r"\bдело\b|\bновый\b": [
        "Всё в порядке, спасибо, что спросил!",
        "Чудесно!",
    ],
    r"\bуметь\b": [
        "Я умею отвечать на вопросы, рассказывать анекдоты, считать несложные выражения. Могу найти всё, что тебе нужно!",
    ],
    r"\bспасибо\b|\bблагодарить\b": [
        "Рад помочь!",
        "Всегда пожалуйста!",
    ],
    r"\bпока\b|\bсвидание\b": [
        "До встречи!",
        "Пока!",
    ],
    r"\bанекдот\b": [
        "Знаешь почему у людоеда нет друзей? Потому что он сыт по горло.",
        "А знаешь как слепые преодолевают препятствия? Не смотря ни на что.",
        "Как называется место на кладбище, где сидит охранник? Живой уголок.",
        "Как называется обувь отца? Батинки.",
        "Шел как-то Бог по раю, видит, два сада горит. На грушевый вообще всё равно, а яблочный спас.",
        "Почему компьютер замерз? У него было открыто слишком много окон."
    ],
    
    r"\bвремя\b|\bчас\b": lambda _: datetime.datetime.now().strftime("Сейчас %H:%M."),
    r"\bчисло\b|\bдата\b": lambda _: datetime.datetime.now().strftime("Сегодня %d.%m.%Y."),
    r"\bдень\b.*\bнеделя\b": lambda _: f"Сегодня {DAYS_RU[datetime.datetime.now().strftime('%A')]}.",
    r"\bпогода\b.*\bв\b\s+(\w+)": lambda m: get_weather(m.group(1)), 
    r"\bнайди\b\s+(.+)": lambda m: search_web(m.group(1)),
}

def tell_joke():
    return random.choice(jokes)

def calculate(match):
    try:
        num1 = int(match.group(1))
        operator = match.group(2)
        num2 = int(match.group(3))

        if operator == '+':
            result = num1 + num2
        elif operator == '-':
            result = num1 - num2
        elif operator == '*':
            result = num1 * num2
        elif operator == '/':
            if num2 == 0:
                return "На ноль делить нельзя!"
            result = num1 / num2
        else:
            return "Не могу вычислить данное выражение("

        return str(result)
    except ValueError:
        return "Некорректный ввод чисел."

def get_weather(city):
    global API_KEY
    conn = http.client.HTTPSConnection("api.openweathermap.org")
    encoded_city = urllib.parse.quote(city) 
    url = f"/data/2.5/weather?q={encoded_city}&appid={API_KEY}&units=metric&lang=ru"
    conn.request("GET", url)
    response = conn.getresponse()
    data = response.read().decode("utf-8")
    conn.close()

    try:
        data = json.loads(data)
        temp = data["main"]["temp"]
        weather_desc = data["weather"][0]["description"]
        return f"В {city} сейчас {weather_desc}, температура {temp}°C."
    except (KeyError, json.JSONDecodeError):
        return "Не удалось получить информацию о погоде."

def search_web(query):
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://www.google.com/search?q={encoded_query}"
    webbrowser.open(url)
    return f"Ищу {query}"

def chatbot_response(text):
    # Анализируем тональность сообщения
    sentiment = analyze_sentiment(text)

    # Проверяем содержимое сообщения
    processed_text = process_text(text)  
    text_lower = ' '.join(processed_text).lower()

    for pattern, response_type in responses.items():
        match = re.search(pattern, text_lower)
        if match:
            if callable(response_type): 
                return response_type(match)  
            elif isinstance(response_type, list):
                return random.choice(response_type)
            else:
                return response_type

    # Возвращаем различные ответы в зависимости от тональности
    if sentiment == "positive":
        return "Я вижу у тебя хорошее настроение!"
    elif sentiment == "negative":
        return "Ты не в настроении. Чем могу помочь?"
    else:  # neutral
        return "Нейтральный настрой." + " " + random.choice(["Я не понял, попробуй переформулировать.", "Попробуй что-то другое."])

    return random.choice(["Я не понял, попробуй переформулировать "]) + sentiment

def log_message(user_message, bot_response):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] User: {user_message}\n[{timestamp}] Bot: {bot_response}\n"
    with open("chat_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(log_entry)

if __name__ == "__main__":
    print("Привет, я - чат Бот!\nТы можешь спросить меня следующие вопросы:\nкак дела?\nчто ты умеешь?\nкакая погода в городе\nсколько сейчас времени?\nкакая сейчас дата?\nнайди (что нужно найти)\nрасскажи анекдот\nВычислить несложный пример(2*3)\nВведите 'выход' для завершения работы.")

    if not os.path.exists("chat_log.txt"):
        with open("chat_log.txt", "w", encoding="utf-8") as f:
            f.write("Начало диалога\n")

    while True:
        user_input = input("Вы: ")
        response = chatbot_response(user_input)
        print("Бот:", response)

        log_message(user_input, response) 

        if user_input.lower() == "выход":
            break
