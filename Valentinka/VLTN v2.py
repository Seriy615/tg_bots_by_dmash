import telebot
import json
import os
import logging

# Настраиваем logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = "7351637070:AAHoIYtqhjmXVFuQXPr946h8Xxdo_ssZJi4"  # ОБЯЗАТЕЛЬНО замените на свой токен!
bot = telebot.TeleBot(TOKEN)

waiting_valentine = {}
USER_DATA_FILE = "user_data.json"
ADMIN_IDS = [7292976610]  # Список ID админов (добавьте свои ID)


def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}


def save_user_data(data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


user_data = load_user_data()


@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.chat.id
    username = message.from_user.username
    args = message.text.split()[1:]

    user_data[user_id] = username
    save_user_data(user_data)

    if args and args[0].isdigit():
        target_user_id = int(args[0])
        waiting_valentine[user_id] = target_user_id
        bot.send_message(user_id, "💌Введите текст вашей валентинки:\n",
                         reply_markup=telebot.types.ReplyKeyboardRemove())
    else:
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton('Начать получать сообщения', callback_data='get_started'))
        bot.send_message(user_id,
                         "🩷Приветик, в этом ботике ты можешь получать и отправлять Анонимные Валентинки💌\n\n"
                         "Жми кнопочку ниже⤵️", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.message.chat.id

    if call.data == 'get_started':
        personal_link = f"https://t.me/{bot.get_me().username}?start={user_id}"
        bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id,
                              text=f"💖Ваша ссылка для получения валентинок:\n{personal_link}")
    elif call.data == 'send_valentine':
        waiting_valentine[user_id] = call.message.chat.id
        bot.send_message(user_id, "💌Введите текст вашей валентинки:\n",
                         reply_markup=telebot.types.ReplyKeyboardRemove())
    elif call.data.startswith("reply_to_"):
        target_user_id = int(call.data.split("_")[-1])
        bot.send_message(user_id, "Введите ваше послание:")
        waiting_valentine[user_id] = target_user_id


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id

    if user_id in waiting_valentine:
        target_user_id = waiting_valentine[user_id]
        sender_username = user_data.get(user_id)

        if user_id in ADMIN_IDS or target_user_id in ADMIN_IDS:
            from_user = f"@{sender_username}" if sender_username else str(user_id)
            to_user = f"@{user_data.get(target_user_id)}" if user_data.get(target_user_id) else str(target_user_id)
            admin_text = f"Сообщение от {from_user} для {to_user}:\n\n{message.text}"

            for admin_id in ADMIN_IDS:
                try:
                    bot.send_message(admin_id, admin_text)
                except telebot.apihelper.ApiTelegramException as e:
                    if "chat not found" in str(e):
                        logger.error(f"Ошибка отправки сообщения админу {admin_id}: чат не найден. "
                                     f"Проверьте список ADMIN_IDS. Ошибка: {e}")
                    else:
                        logger.error(f"Ошибка отправки сообщения админу {admin_id}: {e}")

            if user_id not in ADMIN_IDS or target_user_id not in ADMIN_IDS:  # Отправляем получателю, если это не админ-админу
                valentine_text = f"💌Получено новое анонимное сообщение:\n\n{message.text}"
                keyboard = telebot.types.InlineKeyboardMarkup()
                keyboard.add(telebot.types.InlineKeyboardButton('Ответить', callback_data=f'reply_to_{user_id}'))
                bot.send_message(target_user_id, valentine_text, reply_markup=keyboard)

        else:
            valentine_text = f"💌Получено новое анонимное сообщение:\n\n{message.text}"
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(telebot.types.InlineKeyboardButton('Ответить', callback_data=f'reply_to_{user_id}'))
            bot.send_message(target_user_id, valentine_text, reply_markup=keyboard)

        del waiting_valentine[user_id]
        bot.send_message(user_id, "Сообщение отправлено!")

        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton('Начать получать сообщения', callback_data='get_started'))
        bot.send_message(user_id,
                         "🩷Приветик, в этом ботике ты можешь получать и отправлять Анонимные Валентинки💌\n\n"
                         "Жми кнопочку ниже⤵️", reply_markup=keyboard)

    else:
        bot.send_message(user_id, "Воспользуйтесь командой /start, чтобы начать.")


bot.polling(none_stop=True)
