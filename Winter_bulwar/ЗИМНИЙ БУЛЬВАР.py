import telebot
from telebot import types
import requests
import random
from bitcoin import SelectParams
from bitcoin.core import b2lx
from bitcoin.wallet import CBitcoinSecret, P2PKHBitcoinAddress
import json
import os
import atexit
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from bitcoinlib.services.services import Service
import math
admins=['6559163890']
# Инициализация бота
bot = telebot.TeleBot("6329264934:AAFJViVuj4EPpa-zjlx7jYnkxlTjCwLAZnI")
lids=[]
# Выбор сети (mainnet)
SelectParams('mainnet')
users={}
# Адрес основного кошелька магазина
SHOP_WALLET_ADDRESS = 'YOUR_SHOP_WALLET_ADDRESS'



def optimal_fee():
    # Используем bitcoinlib для получения текущей статистики сети
    service = Service("default")
    mempool_stats = service.getmempoolinfo()

    # Определяем оптимальную комиссию как 1.5x медианной комиссии
    median_fee = mempool_stats['mempool']['fee']['median']
    optimal_fee = median_fee * 1.5
    
    # Округляем комиссию до ближайшего целого значения
    optimal_fee = math.ceil(optimal_fee)

    return optimal_fee

# Выводим оптимальную комиссию
print("Оптимальная комиссия для биткойн-транзакции:", optimal_fee(), "sat/byte")

def get_key(password):
    salt = b'\xc8\xd9\xb2\xfez\x9b\x8a\xc5\x03\x07\xe5\xdfw\xc1\xac\x86'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def encrypt(data, password):
    key = get_key(password)
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data

def decrypt(encrypted_data, password):
    key = get_key(password)
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data)
    return decrypted_data.decode()

# Получение курса Bitcoin к RUB
def get_btc_price():
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=rub'
    response = requests.get(url)
    btc_data = response.json()
    return btc_data['bitcoin']['rub']

def convert_to_btc(amount_rub):
    btc_price = get_btc_price()
    btc_amount = amount_rub / btc_price
    formatted_btc_amount = '{:.8f}'.format(btc_amount)  # Форматирование до 8 знаков после запятой
    return formatted_btc_amount

# Генерация Bitcoin кошелька и сохранение в файл
def generate_and_save_wallet(password):
    secret_bytes = os.urandom(32)
    secret = CBitcoinSecret.from_secret_bytes(secret_bytes)
    address = P2PKHBitcoinAddress.from_pubkey(secret.pub)

    wallet_data = f"{str(secret)},{address}"
    encrypted_data = encrypt(wallet_data, password)

    with open("wallets.txt", "ab") as f:
        f.write(encrypted_data + b"\n")

    return secret, address

# Словарь с ценами на цветы
flowers = {
    "роза": {"1 шт.": 200, "2 шт.": 400, "3 шт.": 600},
    "гвоздика": {"1 шт.": 200, "2 шт.": 400, "3 шт.": 600},
    "тюльпан": {"1 шт." : 150, "2 шт.": 300, "3 шт.": 450},
    "розаQQQ": {"1 шт.": 200, "2 шт.": 400, "3 шт.": 600},
    "гвоздикаQQQ": {"1 шт.": 200, "2 шт.": 400, "3 шт.": 600},
    "тюльпанQQQ": {"1 шт.": 150, "2 шт.": 300, "3 шт.": 450}
}

def load_lids_from_json():
    try:
        with open("lids.json", "r") as f:
            lids = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print("Ошибка загрузки данных из файла JSON. Создается новый пустой файл.")
        lids = []
        save_lids_to_json()
    return lids

def save_lids_to_json():
    try:
        with open("lids.json", "w") as f:
            json.dump(lids, f, indent=4)
    except (IOError, ValueError) as e:
        print(f"Ошибка при записи в файл users.json: {e}")

def load_users_from_json():
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print("Ошибка загрузки данных из файла JSON. Создается новый пустой файл.")
        users = {}
        save_users_to_json()
    return users

def save_users_to_json():
    try:
        with open("users.json", "w") as f:
            json.dump(users, f, indent=4)
    except (IOError, ValueError) as e:
        print(f"Ошибка при записи в файл users.json: {e}")

def save_users_on_exit():
    save_users_to_json()

atexit.register(save_users_on_exit)

users = load_users_from_json()
lids = load_lids_from_json()

@bot.message_handler(commands=['new_lid'])
def new_lid(message):
    user_id = str(message.chat.id)
    if user_id not in admins:
        bot.send_message(user_id, "Недостаточно прав")
        return 0
    lid=str(message.text.split()[1])
    lids.append(lid)
    save_lids_to_json()

    
@bot.message_handler(commands=['wallets'])
def wallets(message):
    user_id = str(message.chat.id)
    if user_id not in admins:
        bot.send_message(user_id, "Недостаточно прав")
        return 0
    password=str(message.text.split()[1])
    with open("wallets.txt", "rb") as f:
        for line in f:
            encrypted_data = line.strip()
            wallet_data = decrypt(encrypted_data, password)
            secret, address_str = wallet_data.split(",")
            bot.send_message(user_id, 'ADRESS: \n'+address_str+'\n\n'+'SECRET: \n'+secret)
    

@bot.message_handler(commands=['fictive_pay'])
def fictive_pay(message):
    user_id = str(message.chat.id)
    if user_id not in admins:
        bot.send_message(user_id, "Недостаточно прав")
        return 0
    target_id = str(message.text.split()[1])
    if target_id in users:
        users[target_id]['fict_pay']=1
        bot.send_message(user_id, "пополнено")
        

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    if user_id not in users:
        users[user_id] = {'balance': 0, 'orders': [], 'flower': 'Не выбран', 'quantity': 'Не выбран', 'city': 'Не выбран','fict_pay': 0 }
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    profile_btn = types.KeyboardButton("Профиль")
    orders_btn = types.KeyboardButton("Заказы")
    topup_btn = types.KeyboardButton("Пополнить")
    buy_flowers_btn = types.KeyboardButton("Купить цветы")
    keyboard.add(profile_btn, orders_btn, topup_btn, buy_flowers_btn)
    bot.send_message(user_id, "Добро пожаловать в магазин цветов", reply_markup=keyboard)

# Обработчик выбора "Профиль"
@bot.message_handler(regexp="Профиль")
def show_profile(message):
    user_id = str(message.chat.id)
    if user_id not in users:
        users[user_id] = {'balance': 0, 'orders': [], 'flower': 'Не выбран', 'quantity': 'Не выбран', 'city': 'Не выбран','fict_pay': 0 }    
    balance = users[user_id]['balance']
    bot.send_message(user_id, f"Ваш баланс: {balance} рублей")

# Обработчик выбора "Заказы"
@bot.message_handler(regexp="Заказы")
def show_orders(message):
    user_id = str(message.chat.id)
    if user_id not in users:
        users[user_id] = {'balance': 0, 'orders': [], 'flower': 'Не выбран', 'quantity': 'Не выбран', 'city': 'Не выбран','fict_pay': 0 }
    orders = users[user_id]['orders']
    if not orders:
        bot.send_message(user_id, "У вас нет активных заказов.")
    else:
        order_messages = [f"Заказ {idx+1}:\n{order}" for idx, order in enumerate(orders)]
        bot.send_message(user_id, "\n\n".join(order_messages))

# Обработчик пополнения
@bot.message_handler(regexp="Пополнить")
def topup(message):
    user_id = str(message.chat.id)
    if user_id not in users:
        users[user_id] = {'balance': 0, 'orders': [], 'flower': 'Не выбран', 'quantity': 'Не выбран', 'city': 'Не выбран','fict_pay': 0 }
    bot.send_message(user_id, "Введите сумму пополнения в рублях (минимум 2000 рублей):")
    bot.register_next_step_handler(message, process_topup_amount)

def process_topup_amount(message):
    user_id = str(message.chat.id)
    try:
        amount_rub = int(message.text)
        if amount_rub < 2000:
            bot.send_message(user_id, "Минимальная сумма пополнения - 2000 рублей.")
            return

        # Генерация одноразового Bitcoin кошелька для оплаты
        secret, address = generate_and_save_wallet('3E2051$1502e3!')
        users[user_id]['wallet'] = str(address)

        btc_to_pay = float(convert_to_btc(amount_rub))  # Конвертируем в BTC
        users[user_id]['btc_to_pay'] = btc_to_pay  # Сохраняем цену в BTC в словаре пользователей

        bot.send_message(user_id, f"Сгенерированный Bitcoin кошелек для пополнения баланса: {address}\nСумма к оплате в BTC: {btc_to_pay}")

        # Добавление кнопки "Проверить оплату"
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Проверить оплату", callback_data="check_payment"))
        bot.send_message(user_id, "После оплаты нажмите кнопку ниже для проверки.", reply_markup=keyboard)

        save_users_to_json()  # Сохранение данных после изменения
    except ValueError:
        bot.send_message(user_id, "Некорректный ввод. Пожалуйста, введите целое число.")

# Обработчик выбора "Купить цветы"
@bot.message_handler(regexp="Купить цветы")
def buy_flowers(message):
    user_id = str(message.chat.id)
    if user_id not in lids:
        if user_id not in users:
            users[user_id] = {'balance': 0, 'orders': [], 'flower': 'Не выбран', 'quantity': 'Не выбран', 'city': 'Не выбран','fict_pay': 0 }
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        q=0
        for flower in flowers.keys():
            key = types.InlineKeyboardButton(text=flower, callback_data='flower_' + flower)
            keyboard.add(key)
            q+=1
            if q==3: break
        bot.send_message(user_id, "Выберите цветок", reply_markup=keyboard)
    else:
        if user_id not in users:
            users[user_id] = {'balance': 0, 'orders': [], 'flower': 'Не выбран', 'quantity': 'Не выбран', 'city': 'Не выбран','fict_pay': 0 }
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        q=0
        for flower in flowers.keys():
            if q<=2:
                q+=1
                continue
            key = types.InlineKeyboardButton(text=flower, callback_data='flower_' + flower)
            keyboard.add(key)
            q+=1
            
        bot.send_message(user_id, "Выберите цветок", reply_markup=keyboard)

    
# Обработчик выбора цветка
@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'flower')
def choose_flower(callback):
    user_id = str(callback.message.chat.id)
    if user_id not in users:
        users[user_id] = {'balance': 0, 'orders': [], 'flower': 'Не выбран', 'quantity': 'Не выбран', 'city': 'Не выбран','fict_pay': 0 }
    flower_name = callback.data.split('_')[1]
    users[user_id]['flower'] = flower_name
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for quantity, price in flowers[flower_name].items():
        key = types.InlineKeyboardButton(text=quantity + " (" + str(price) + " р.)", callback_data='quantity_' + quantity)
        keyboard.add(key)
    bot.edit_message_text(chat_id=user_id, message_id=callback.message.message_id, text="Выберите количество", reply_markup=keyboard)

# Обработчик выбора количества
@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'quantity')
def choose_quantity(callback):
    user_id = str(callback.message.chat.id)
    if user_id not in users:
        users[user_id] = {'balance': 0, 'orders': [], 'flower': 'Не выбран', 'quantity': 'Не выбран', 'city': 'Не выбран','fict_pay': 0 }
    quantity = callback.data.split('_')[1]
    users[user_id]['quantity'] = quantity
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for city in ["Санкт-Петербург", "Москва", "Казань"]:
        key = types.InlineKeyboardButton(text=city, callback_data='city_' + city)
        keyboard.add(key)
    bot.edit_message_text(chat_id=user_id, message_id=callback.message.message_id, text="Выберите город", reply_markup=keyboard)

# Обработчик выбора города
@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'city')
def choose_city(callback):
    user_id = str(callback.message.chat.id)
    city = callback.data.split('_')[1]
    users[user_id]['city'] = city
    total_price_rub = flowers[users[user_id]['flower']][users[user_id]['quantity']]
    total_price_with_commission = int(total_price_rub * 1.05)  # Добавление комиссии 5%

    if users[user_id]['balance'] >= total_price_with_commission:
        users[user_id]['balance'] -= total_price_with_commission
        order_details = f"Цветок: {users[user_id]['flower']}\nКоличество: {users[user_id]['quantity']}\nГород: {city}\nСтоимость: {total_price_with_commission} рублей (включая комиссию 5%)"
        users[user_id]['orders'].append(order_details)
        save_users_to_json()  # Сохранение данных после изменения
        bot.send_message(user_id, "Заказ принят.")
    else:
        bot.send_message(user_id, f"Недостаточно средств на балансе. Требуется {total_price_with_commission - users[user_id]['balance']} рублей.")

# Проверка оплаты через Bitcoin
def check_payment(wallet_address, expected_amount_btc):
    url = f'https://api.blockcypher.com/v1/btc/main/addrs/{wallet_address}'
    response = requests.get(url)
    wallet_data = response.json()
    balance_btc = wallet_data['balance'] / 10**8  # приведение к BTC
    return balance_btc >= expected_amount_btc

# Функция для перевода средств с одноразового кошелька на основной кошелек магазина
def transfer_funds(sender_secret, recipient_address, amount_to_send):
    sender_wallet = CBitcoinSecret(sender_secret).to_address()
    fee = 1000  # 0.00000001 BTC
    tx_id = None
    try:
        recipient_address = str(recipient_address)
        sender_secret = CBitcoinSecret(sender_secret)  # Преобразование секретного ключа в объект CBitcoinSecret
        sender_wallet = sender_secret.to_address()
        tx_id = sender_secret.send_to(recipient_address, amount_to_send, fee)
    except Exception as e:
        print("Error occurred during transaction:", e)
    return b2lx(tx_id) if tx_id else None

# Обработчик проверки оплаты
@bot.callback_query_handler(func=lambda call: call.data == 'check_payment')
def check_payment_callback(callback):
    user_id = str(callback.message.chat.id)
    btc_wallet = users[user_id]['wallet']
    total_price_btc = users[user_id]['btc_to_pay']  # Используем сохраненное значение цены в BTC
    if users[user_id]['fict_pay'] == 1:
        
        users[user_id]['balance'] += int(total_price_btc * get_btc_price())
        users[user_id]['fict_pay']= 0
        users[user_id]['btc_to_pay']= 0
        users[user_id]['wallet']=''
        save_users_to_json()
        bot.send_message(user_id, f"Оплата прошла успешно! Баланс пополнен.")
        
        return 0
    
    elif check_payment(btc_wallet, total_price_btc):
        users[user_id]['balance'] += int(total_price_btc * get_btc_price())  # Пополнение баланса в рублях
        users[user_id]['fict_pay']= 0
        users[user_id]['btc_to_pay']= 0
        users[user_id]['wallet']=''
        save_users_to_json()  # Сохранение данных после изменения

        # Перевод средств с одноразового кошелька на основной кошелек магазина
        sender_secret, sender_address = get_wallet_details(btc_wallet, '3E2051$1502e3!')
        recipient_address = SHOP_WALLET_ADDRESS
        amount_to_send = int(total_price_btc * 100000000)  # Перевод в сатоши
        tx_id = transfer_funds(sender_secret, recipient_address, amount_to_send)
        bot.send_message(user_id, f"Оплата прошла успешно! Баланс пополнен.")
    else:
        bot.send_message(user_id, "Оплата не обнаружена. Пожалуйста, оплатите и попробуйте снова.")

# Функция для получения секретного ключа и адреса кошелька из файла wallets.txt
def get_wallet_details(wallet_address, password):
    with open("wallets.txt", "rb") as f:
        for line in f:
            encrypted_data = line.strip()
            wallet_data = decrypt(encrypted_data, password)
            secret, address_str = wallet_data.split(",")
            address = P2PKHBitcoinAddress(address_str)
            
            if address == wallet_address:
                return secret, address
    return None, None


try:
    bot.polling()
except Exception as e:
    print("An error occurred:", e)
