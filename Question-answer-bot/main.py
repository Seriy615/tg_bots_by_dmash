import telebot
import requests
import docx
import xml.etree.ElementTree as ET

# Замените на ваш токен от BotFather
BOT_TOKEN = 'TG_API_KEY'
# Замените на ваш API-ключ DeepSeek
DEEPSEEK_API_KEY = 'DEEPSEEK/OPENAI_API_KEY'

# Инициализация бота
bot = telebot.TeleBot(BOT_TOKEN)


# Чтение файлов с информацией
def read_files():
    context = ""

    # Чтение DOCX-файла с Положением
    try:
        doc = docx.Document('regulation.docx')
        for para in doc.paragraphs:
            context += para.text + "\n"
    except Exception as e:
        print(f"Ошибка при чтении regulation.docx: {e}")

    # Чтение XML-файла с Программой
    try:
        tree = ET.parse('program.xml')
        root = tree.getroot()
        context += f"{root.find('Title').text}\n{root.find('Description').text}\n"
        for day in root.findall('Day'):
            date = day.get('Date')
            weekday = day.get('Weekday')
            context += f"\n{date} ({weekday}):\n"
            for event in day.find('Events').findall('Event'):
                time = event.find('Time').text
                desc = event.find('Description').text
                loc = event.find('Location').text
                note = event.find('Note').text or ""
                context += f"- {time}: {desc} (Место: {loc}) {note}\n"
    except Exception as e:
        print(f"Ошибка при чтении program.xml: {e}")

    return context


# Загрузка контекста один раз при запуске
CONTEXT = read_files()


# Функция для обращения к DeepSeek API
def get_deepseek_response(question):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system",
             "content": f"Ты бот, который отвечает на вопросы об Олимпиаде «ИнфоТехКвест» на основе следующей информации:\n{CONTEXT}\nОтвечай кратко, четко и только на основе предоставленных данных. Если информации недостаточно, скажи: 'Информация отсутствует в предоставленных документах.'"},
            {"role": "user", "content": question}
        ],
        "max_tokens": 1000,
        "temperature": 0.7
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        print(question)
        print(result['choices'][0]['message']['content'])
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"Произошла ошибка при обращении к API: {e}"


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
                 "Привет! Я бот Олимпиады «ИнфоТехКвест». Задавай вопросы о правилах, расписании или программе заключительного этапа, и я постараюсь ответить!")


# Обработчик текстовых сообщений
@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_question = message.text
    bot.reply_to(message, "Ищу ответ...")

    # Получаем ответ от DeepSeek
    answer = get_deepseek_response(user_question)

    # Отправляем ответ пользователю
    bot.reply_to(message, answer)


# Запуск бота
if __name__ == "__main__":
    print("Бот запущен...")
    bot.polling(none_stop=True)