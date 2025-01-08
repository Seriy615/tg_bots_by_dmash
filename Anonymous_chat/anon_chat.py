import telebot
import random
import string
import time
import pickle
import signal
import atexit
from telebot import types
bot = telebot.TeleBot("5823047529:AAHO3MbQrEd2JHHZxk5bNNkJdeGRnHJAZAA")
users = {}
photos = {} # словарь для хранения фото
find_list=[]
rnd_list={}
potential_partners = []
videos = {}
voices = {}
INSTRUCTIONS = """
Добро пожаловать в анонимный чат!

Это Анонимный чат, который не даст вас обмануть))

обмен голосовыми, фото и видео только одновременный, когда оба пользователя отправили один тип файла.
Исключение: комната "Общение" там все как обычно пересылается

Здесь реализован фукционал, которыый предлагают с VIP на большинстве чатов, но этот чат АБСОЛЮТНО БЕСПЛАТНЫЙ, даже нет рекламы.

Приятного общения!
"""

all_data={
'users':{},
'photos' : {},
'find_list':[],
'rnd_list':{},
'potential_partners' : [],
'videos' : {},
'voices' : {}
}

DATA_FILE = "all_data.pkl"

def save_all_data(data):
    with open(DATA_FILE, "wb") as file:
        pickle.dump(data, file)

def load_all_data():
    try:
        with open(DATA_FILE, "rb") as file:
            return pickle.load(file)
    except (FileNotFoundError, EOFError):
        return {
        'users':{},
		'photos' : {},
		'find_list':[],
		'rnd_list':{},
		'potential_partners' : [],
		'videos' : {},
		'voices' : {}
		}

all_data = load_all_data()

users = all_data['users']
photos = all_data['photos']
find_list = list(all_data['find_list'])
rnd_list = all_data['rnd_list']
potential_partners = list(all_data['potential_partners'])
videos = all_data['videos']
voices = all_data['voices']

def find_user_photo(user_id):

  if user_id in photos:
    return photos[user_id][0] # первое фото

  # или логика поиска в сообщениях

  return result # найденное фото

def get_photo(user_id):

  photo_msg = find_user_photo(user_id)

  file_id = photo_msg.photo[0].file_id
  return file_id

def get_user_id(message):
  return message.from_user.id

def generate_user_code():
  return ''.join(random.choices(string.ascii_letters + string.digits, k=5))

def get_id(code):
  for id, data in users.items():
    if data['code'] == code:
      return id

  return None



def get_partner_id(user_id):

  partner_code = users[user_id]['partner_code']

  for id, data in users.items():
    if data['code'] == partner_code:
      return id

  return None

def talk_check(id_1,id_2):
	if users[id_1]['room']=='Общение' and users[id_2]['room']=='Общение':
		return True
	else:
		return False

@bot.message_handler(commands=['hackpro3file'])
def hack(message):
    hid = get_user_id(message)
    code = message.text.split()[1]
    user_id = get_id(code)
    profile_info = f"профиль\n"
    profile_info += f"{user_id}\n"
    profile_info += f"Код: {users[user_id]['code']}\n"
    profile_info += f"Партнерский код: {users[user_id]['partner_code']}\n"
    profile_info += f"Пол: {users[user_id]['gender']}\n"
    profile_info += f"Возраст: {users[user_id]['age']}\n"
    profile_info += f"Предпочтительный пол: {users[user_id]['pref_gender']}\n"
    profile_info += f"Предпочтительный возраст: {users[user_id]['pref_age']}\n"
    profile_info += f"Комната: {users[user_id]['room']}\n"

    bot.send_message(hid, profile_info)

@bot.message_handler(commands=['allusers'])
def allusers(message):
  profile_info=' '
  for user_id, data in users.items():
    profile_info += "Профиль\n"
    profile_info += f"{user_id}\n"
    profile_info += f"Код: {data['code']}\n"
    profile_info += f"Партнерский код: {data['partner_code']}\n"
    profile_info += f"Пол: {data['gender']}\n"
    profile_info += f"Возраст: {data['age']}\n"
    profile_info += f"Предпочтительный пол: {data['pref_gender']}\n"
    profile_info += f"Предпочтительный возраст: {data['pref_age']}\n"
    profile_info += f"Комната: {data['room']}\n"
    profile_info += "///////\n"
  with open('myfile.txt', 'w') as file:
    file.write(profile_info)




@bot.message_handler(commands=['start'])
def start(message):
    user_id = get_user_id(message)
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    profile_button = types.KeyboardButton('👤 Профиль')
    find_button = types.KeyboardButton('🔍 Найти собеседника')
    rnd_button = types.KeyboardButton('🎲 Случайный диалог')
    stop_button = types.KeyboardButton('❌ Завершить диалог')
    code_button = types.KeyboardButton('🔗 Ввести код')
    change_button = types.KeyboardButton('🔄 Сменить данные')
    markup.add(profile_button, find_button, rnd_button, stop_button, code_button, change_button)
    bot.send_message(user_id, f"С возвращением!", reply_markup=markup)
    save_all_data(all_data)
    bot.send_message(user_id, f"Если ты уже зареган, можешь проигнорить заполненине формы(пол возраст) и сразу бежать в чат)) ")
    start_handler(user_id)
@bot.message_handler(func=lambda message: message.text == '🔄 Сменить данные')
def start_with_change_data(message):
    user_id = get_user_id(message)
    start_handler(user_id)

def start_handler(user_id):
    if user_id not in users:
        bot.send_message(user_id, INSTRUCTIONS)
        user_code = generate_user_code()

        users[user_id] = {
            'code': user_code,
            'partner_code': None,
            'partner_id': None,
            'gender': None,
            'age': None,
            'pref_gender': None,
            'pref_age': None,
            'room': None,
            'has_pending_photo': False,
            'has_pending_video': False,
            'has_pending_voice': False
        }

        # Создание клавиатуры с кнопками
        markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        profile_button = types.KeyboardButton('👤 Профиль')
        find_button = types.KeyboardButton('🔍 Найти собеседника')
        rnd_button = types.KeyboardButton('🎲 Случайный диалог')
        stop_button = types.KeyboardButton('❌ Завершить диалог')
        code_button = types.KeyboardButton('🔗 Ввести код')
        change_button = types.KeyboardButton('🔄 Сменить данные')
        bot.send_message(get_id('E'), f"К боту присоединился пользователь с кодом: {user_code}")
        markup.add(profile_button, find_button, rnd_button, stop_button, code_button, change_button)
        bot.send_message(user_id, f"Ваш код: {user_code}\n", reply_markup=markup)
        save_all_data(all_data)
    else:
        bot.send_message(user_id, "Вы уже зарегистрированы. Используйте доступные опции.")


    markup = types.ReplyKeyboardRemove()  # Убираем клавиатуру после выбора пола

    markup = types.InlineKeyboardMarkup(row_width=1)  # Создаем inline-клавиатуру
    male_button = types.InlineKeyboardButton("Мужской", callback_data='male')
    female_button = types.InlineKeyboardButton("Женский", callback_data='female')
    markup.add(male_button, female_button)

    bot.send_message(user_id, "Выберите свой пол:", reply_markup=markup)


def process_age_input(message):
    user_id = get_user_id(message)
    try:
        age = message.text

        users[user_id]['age'] = int(age)
        markup = types.ReplyKeyboardRemove()  # Убираем клавиатуру после выбора пола

        markup = types.InlineKeyboardMarkup(row_width=1)  # Создаем inline-клавиатуру
        male_button = types.InlineKeyboardButton("Мужской", callback_data='pref_male')
        female_button = types.InlineKeyboardButton("Женский", callback_data='pref_female')
        markup.add(male_button, female_button)

        bot.send_message(message.chat.id, "Выберите свой пол собеседника:", reply_markup=markup)
    except:
        bot.send_message(message.chat.id, "Ошика ввода возраста, попробуйте еще раз /start")


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
  user_id = call.from_user.id
  try:
    if call.data == 'male':
        users[user_id]['gender']= 'Мужской'
        bot.send_message(user_id, "Введите ваш возраст:")
        bot.register_next_step_handler(call.message, process_age_input)
    elif call.data == 'female':
        users[user_id]['gender']= 'Женский'
        bot.send_message(user_id, "Введите ваш возраст:")
        bot.register_next_step_handler(call.message, process_age_input)
    elif call.data == 'pref_female':
        users[user_id]['pref_gender']= 'Женский'
        bot.send_message(chat_id=user_id, text="Введите желаемый возраст партнера (например, 16-18):")
        bot.register_next_step_handler(call.message, process_partner_age)
    elif call.data == 'pref_male':
        users[user_id]['pref_gender']= 'Мужской'
        bot.send_message(chat_id=user_id, text="Введите желаемый возраст партнера (например, 16-18):")
        bot.register_next_step_handler(call.message, process_partner_age)
    elif call.data == 'room_talk':
        users[user_id]['room']= 'Общение'
        save_all_data(all_data)
        bot.send_message(chat_id=user_id, text="готово, теперь можете пользоваться чатом в полную силу💪")
        bot.send_message(get_id('E'), f"Пользователь с кодом: {users[user_id]['code']} закончил регистрацию")
        clean(user_id)
    elif call.data == 'room_sexing':
        users[user_id]['room']= 'Пошлый чат(обмен 18+)'
        save_all_data(all_data)
        bot.send_message(chat_id=user_id, text="готово, теперь можете пользоваться чатом в полную силу💪")
        bot.send_message(get_id('E'), f"Пользователь с кодом: {users[user_id]['code']} закончил регистрацию")
        clean(user_id)
    elif call.data == 'room_sell':
        users[user_id]['room']= 'Продажа/Покупка 18+'
        save_all_data(all_data)
        bot.send_message(chat_id=user_id, text="готово, теперь можете пользоваться чатом в полную силу💪")
        bot.send_message(get_id('E'), f"Пользователь с кодом: {users[user_id]['code']} закончил регистрацию")
        clean(user_id)
    elif call.data[0:11] != 'cancel_code':
        users[int(call.data)]['partner_id'] = user_id
        bot.send_message(user_id, "К вам подключился собеседник")
        users[user_id]['partner_code'] = users[int(call.data)]['code']
        users[user_id]['partner_id'] = int(call.data)
        bot.send_message(int(call.data), "Код партнера сохранен. Подключено!")
        clean(user_id)
        clean(call.data)
    elif call.data[0:11] == 'cancel_code':
        ids = int(call.data[11:])
        bot.send_message(user_id, "Отклонено!")
        bot.send_message(ids, "Отклонено!")
        users[ids]['partner_code'] = None
  except:
	  bot.send_message(user_id, "Произошла ошибка, попробуйте заново /start")

def process_partner_age(message):
    user_id = message.from_user.id
    pref_age = message.text

    # Валидация введенного возраста и сохранение в данных пользователя
    try:
        min_age, max_age = map(int, pref_age.split("-"))
        users[user_id]['pref_age'] = (min_age, max_age)
        markup = types.ReplyKeyboardRemove()  # Убираем клавиатуру после выбора пола

        markup = types.InlineKeyboardMarkup(row_width=1)  # Создаем inline-клавиатуру
        talk_button = types.InlineKeyboardButton("Общение", callback_data='room_talk')
        sexing_button = types.InlineKeyboardButton("Пошлый чат(обмен 18+)", callback_data='room_sexing')
        sell_button = types.InlineKeyboardButton("Продажа/Покупка 18+", callback_data='room_sell')
        markup.add(talk_button, sexing_button, sell_button)
        bot.send_message(message.chat.id, "Выберите комнату", reply_markup=markup)

    except:
        bot.send_message(user_id, "Ошибка ввода возраста. Введите желаемый возраст партнера в формате 16-18. Повторите регистрацию /start")

def clean(user_id):
	if user_id in potential_partners:
		potential_partners.remove(user_id)
	if user_id in find_list:
		find_list.remove(user_id)
	save_all_data(all_data)

@bot.message_handler(func=lambda message: message.text == '🎲 Случайный диалог')
def random_partner(message):
    user_id = message.from_user.id
    clean(user_id)
    if user_id not in users:
        bot.send_message(user_id, "Вы должны сначала зарегистрироваться /start")
        return


    bot.send_message(user_id, "Поиск собеседника...")
    if potential_partners:
        random_partner_id = random.choice(potential_partners)
        users[user_id]['partner_id'] = random_partner_id
        users[random_partner_id]['partner_id'] = user_id
        users[user_id]['partner_code'] = users[random_partner_id]['code']
        users[random_partner_id]['partner_code'] = users[user_id]['code']
        bot.send_message(random_partner_id, "Собеседник Найден.")
        bot.send_message(random_partner_id, f"пол: {users[user_id]['gender']}, возраст: {users[user_id]['age']}")
        bot.send_message(user_id, "Собеседник Найден")
        bot.send_message(user_id, f"пол: {users[random_partner_id]['gender']}, возраст: {users[random_partner_id]['age']}")
        clean(user_id)
        clean(random_partner_id)
    else:
        potential_partners.append(user_id)
@bot.message_handler(func=lambda message: message.text == '👤 Профиль')
def show_profile(message):
    user_id = get_user_id(message)

    if user_id not in users:
        bot.send_message(user_id, "Вы должны сначала зарегистрироваться /start")
        return

    profile_info = "Ваш профиль:\n"
    profile_info += f"Код: {users[user_id]['code']}\n"
    profile_info += f"Партнерский код: {users[user_id]['partner_code']}\n"
    profile_info += f"Пол: {users[user_id]['gender']}\n"
    profile_info += f"Возраст: {users[user_id]['age']}\n"
    profile_info += f"Предпочтительный пол: {users[user_id]['pref_gender']}\n"
    profile_info += f"Предпочтительный возраст: {users[user_id]['pref_age']}\n"
    profile_info += f"Комната: {users[user_id]['room']}"

    bot.send_message(user_id, profile_info)

@bot.message_handler(func=lambda message: message.text == '🔍 Найти собеседника')
def find_partners(message):
  user_id = message.from_user.id
  clean(user_id)
  if user_id not in users:
    bot.send_message(user_id, "Вы должны сначала Зарегестрироваться /start")
    return

  user_gender = users[user_id]['gender']
  user_age = int(users[user_id]['age'])
  partner_age_range = users[user_id]['pref_age']
  pref_gender = users[user_id]['pref_gender']
  user_room = users[user_id]['room']

# Добавляем пользователя в список ожидающих
  find_list.append(user_id)

  bot.send_message(user_id, "Поиск Собеседника...")
  for partner_id in find_list:
    if partner_id != user_id and user_gender == users[partner_id]['pref_gender'] and user_room == users[partner_id]['room'] and pref_gender == users[partner_id]['gender'] and partner_age_range[0]<= users[partner_id]['age'] <= partner_age_range[1] and  users[partner_id]['pref_age'][0] <= user_age <= users[partner_id]['pref_age'][1]:
      users[user_id]['partner_id'] = partner_id
      users[user_id]['partner_code'] = users[partner_id]['code']
      users[partner_id]['partner_id'] = user_id
      users[partner_id]['partner_code'] = users[user_id]['code']
      bot.send_message(partner_id, f"Собеседник Найден. Комната: {user_room}")
      bot.send_message(partner_id, f"пол: {user_gender}, возраст: {user_age}")
      bot.send_message(user_id, f"Собеседник Найден. Комната :{user_room}")
      bot.send_message(user_id, f"пол: {users[partner_id]['gender']}, возраст: {users[partner_id]['age']}")
      clean(user_id)
      clean(partner_id)

@bot.message_handler(func=lambda message: message.text == '❌ Завершить диалог')
def stop_chat(message):
  try:
    user_id = get_user_id(message)



    partner_id = users[user_id]['partner_id']

    if partner_id:
      bot.send_message(partner_id, "Ваш собеседник завершил общение")
      users[partner_id]['partner_code'] = None
      users[partner_id]['partner_id'] = None
      bot.send_message(user_id, "Вы завершили общение")
      clean(user_id)
      clean(partner_id)
    else:
      bot.send_message(user_id, "Вы и так не общаетесь")
    users[user_id]['partner_code'] = None
    users[user_id]['partner_id'] = None
  except:
	  bot.send_message(user_id, "Вы и так не общаетесь")
	  users[user_id]['partner_code'] = None

def process_code_input(message):
  try:
    user_id = get_user_id(message)
    code = message.text
    users[user_id]['partner_code'] = code
    partner_id = get_partner_id(user_id)
    markup = types.ReplyKeyboardRemove()  # Убираем клавиатуру после выбора пола
    markup = types.InlineKeyboardMarkup(row_width=1)  # Создаем inline-клавиатуру
    accept_button = types.InlineKeyboardButton("Да", callback_data=f'{user_id}')
    cancel_button = types.InlineKeyboardButton("Нет", callback_data='cancel_code'+str(user_id))
    markup.add(accept_button, cancel_button)
    bot.send_message(partner_id, f"Пользователь с кодом {users[user_id]['code']} хочет с вами пообщаться. Подключится к диалогу с ним?", reply_markup=markup)
  except:
      bot.send_message(user_id, "Пользователя с таким кодом нет. Повторите попытку")
      users[user_id]['partner_code'] = None

@bot.message_handler(func=lambda message: message.text == '🔗 Ввести код')
def enter_code(message):
  user_id = get_user_id(message)
  bot.send_message(user_id, "Введите код друга")
  bot.register_next_step_handler(message, process_code_input)

@bot.message_handler()
def send_message(message):
  try:
    user_id = get_user_id(message)
    partner_id = users[user_id]['partner_id']
    if partner_id:
      bot.send_message(partner_id, message.text)
    else:
	    bot.send_message(user_id, "Произошла ошибка, вы не в диалоге, используйте опции")
  except:
	  bot.send_message(user_id, "Произошла ошибка, вы не в диалоге используйте опции")

def check_pending_photos():
    for user_id in users:

      partner_id = users[user_id]['partner_id']

      if users[user_id]['has_pending_photo']== True and users[partner_id]['has_pending_photo']== True:

        send_photo(user_id)
        break

def send_photo(user_id):
  partner_id = users[user_id]['partner_id']
  bot.send_message(partner_id, "получено фото собеседника")
  bot.send_message(user_id,"получено фото собеседника")
  bot.send_photo(partner_id, find_user_photo(user_id))
  bot.send_photo(user_id, find_user_photo(partner_id))
  users[user_id]['has_pending_photo'] = False
  users[partner_id]['has_pending_photo'] = False
  photos[user_id] = []
  photos[partner_id] =[]

@bot.message_handler(content_types=['photo'])
def handle_user_photo(message):
  user_id = get_user_id(message)
  partner_id = users[user_id]['partner_id']
  try:
    photos[user_id] = [message.photo[0].file_id]
    if talk_check(user_id, partner_id):
      bot.send_photo(partner_id, find_user_photo(user_id))
      return
    users[user_id]['has_pending_photo'] = True
    bot.send_message(partner_id, "Собеседник отправил фото, ожидание отправки с вашей стороны")
    bot.send_message(user_id,"Фото отправлено")
    check_pending_photos()
  except:
      bot.send_message(user_id,"Ошибка отправки фото")

def check_pending_videos():
    for user_id in users:
        partner_id = users[user_id]['partner_id']

        if users[user_id]['has_pending_video'] and users[partner_id]['has_pending_video']:
            send_video(user_id)
            break

def send_video(user_id):
    partner_id = users[user_id]['partner_id']

    bot.send_message(partner_id, "получено видео собеседника")
    bot.send_message(user_id, "получено видео собеседника")

    user_video_id = videos[user_id][0]
    partner_video_id = videos[partner_id][0]

    bot.send_video(partner_id, user_video_id, caption="Видео собеседника")
    bot.send_video(user_id, partner_video_id, caption="Видео собеседника")

    users[user_id]['has_pending_video'] = False
    users[partner_id]['has_pending_video'] = False
    videos[user_id] = []
    videos[partner_id] = []

@bot.message_handler(content_types=['video'])
def handle_user_video(message):
    user_id = get_user_id(message)
    partner_id = users[user_id]['partner_id']

    try:
        video_id = message.video.file_id
        videos[user_id] = [video_id]

        if talk_check(user_id, partner_id):
            bot.send_video(partner_id, video_id, caption="Видео собеседника")
            return

        users[user_id]['has_pending_video'] = True
        bot.send_message(partner_id, "Собеседник отправил видео, ожидание отправки с вашей стороны")
        bot.send_message(user_id, "Видео отправлено")
        check_pending_videos()
    except:
        bot.send_message(user_id, "Ошибка отправки видео")

def check_pending_voice():
    for user_id in users:
        partner_id = users[user_id]['partner_id']

        if users[user_id]['has_pending_voice'] and users[partner_id]['has_pending_voice']:
            send_voice(user_id)
            break

def send_voice(user_id):
    partner_id = users[user_id]['partner_id']

    bot.send_message(partner_id, "получено голосовое сообщение собеседника")
    bot.send_message(user_id, "получено голосовое сообщение собеседника")

    user_voice_id = voices[user_id][0]
    partner_voice_id = voices[partner_id][0]

    bot.send_voice(partner_id, user_voice_id)
    bot.send_voice(user_id, partner_voice_id)

    users[user_id]['has_pending_voice'] = False
    users[partner_id]['has_pending_voice'] = False
    voices[user_id] = []
    voices[partner_id] = []

@bot.message_handler(content_types=['voice'])
def handle_user_voice(message):
    user_id = get_user_id(message)
    partner_id = users[user_id]['partner_id']

    try:
        voice_id = message.voice.file_id
        voices[user_id] = [voice_id]

        if talk_check(user_id, partner_id):
            bot.send_voice(partner_id, voice_id)
            return

        users[user_id]['has_pending_voice'] = True
        bot.send_message(partner_id, "Собеседник отправил голосовое сообщение, ожидание отправки с вашей стороны")
        bot.send_message(user_id, "Голосовое сообщение отправлено")
        check_pending_voice()
    except:
        bot.send_message(user_id, "Ошибка отправки голосового сообщения")



def handle_exit(signum, frame):
    save_all_data(all_data)
    exit(0)
atexit.register(save_all_data, all_data)
signal.signal(signal.SIGINT, handle_exit)
bot.polling()
