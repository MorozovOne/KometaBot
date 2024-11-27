import telebot
import requests
import sqlite3
import threading
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = '7676234253:AAGRJkqR_kvJbKiHSJ1Bczm5wyCBIIghQDs'
API_URL = "http://127.0.0.1:8000/api/user"
TOKEN_URL = "http://127.0.0.1:8000/api/admin/token"
HEADERS = {
    "accept": "application/json",
    "Content-Type": "application/json"
}

bot = telebot.TeleBot(BOT_TOKEN)
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

def refresh_token():
    global HEADERS
    try:
        response = requests.post(
            TOKEN_URL,
            headers={"accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "", "username": "admin", "password": "admin", "scope": "", "client_id": "", "client_secret": ""}
        )
        response.raise_for_status()
        HEADERS["Authorization"] = f"Bearer {response.json()['access_token']}"
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при обновлении токена: {e}")
    threading.Timer(300, refresh_token).start()

refresh_token()

def user_exists(username):
    cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        return True
    try:
        response = requests.get(f"{API_URL}/{username}", headers=HEADERS)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при проверке пользователя: {e}")
        return False

def create_key(username):
    if user_exists(username):
        return None
    payload = {
        "username": username,
        "proxies": {"vless": {"id": "35e4e39c-7d5c-4f4b-8b71-558e4f37ff53"}},
        "inbounds": {"vless": ["VLESS TCP REALITY"]},
        "expire": 1733691599,
        "data_limit": 0,
        "data_limit_reset_strategy": "no_reset",
        "status": "active",
        "note": "",
        "on_hold_timeout": "2023-11-03T20:30:00",
        "on_hold_expire_duration": 0
    }
    response = requests.post(API_URL, json=payload, headers=HEADERS)
    response.raise_for_status()
    return username

def get_key(username):
    response = requests.get(f"{API_URL}/{username}", headers=HEADERS)
    response.raise_for_status()
    return response.json()["links"][0]

def check_existing_key(telegram_id):
    cursor.execute("SELECT vpn_link FROM users WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    return result[0] if result else None

def delete_key(telegram_id, username):
    cursor.execute("DELETE FROM users WHERE telegram_id = ?", (telegram_id,))
    conn.commit()
    response = requests.delete(f"{API_URL}/{username}", headers=HEADERS)
    response.raise_for_status()

def get_available_servers():
    cursor.execute("SELECT * FROM servers")
    return cursor.fetchall()

@bot.message_handler(commands=['start'])
def handle_start(message):
    username = message.from_user.username
    welcome_text = (
        f"Привет! {username}\nВаша подписка: Не активна\n"
        f"Бесплатный пробный период: 30 дней\n Пока не подключили оплату \n\nВыберите действие:"
    )
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Выдать ключ", callback_data="generate_key"))
    markup.add(InlineKeyboardButton("Узнать потраченный трафик", callback_data="check_traffic"))
    markup.add(InlineKeyboardButton("Удалить ключ", callback_data="delete_key"))
    markup.add(InlineKeyboardButton("Инструкция", callback_data="show_instructions"))
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "show_instructions")
def show_instructions(call):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Инструкция для IOS/MacOS", callback_data="instruction_ios"))
    markup.add(InlineKeyboardButton("Инструкция для Android", callback_data="instruction_android"))
    markup.add(InlineKeyboardButton("Инструкция для Windows", callback_data="instruction_windows"))
    bot.send_message(call.message.chat.id, "Выберите платформу:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "instruction_ios")
def instruction_ios(call):
    ios_text = "Для IOS/MacOS: вставьте ключ в поле настроек VPN."
    bot.send_message(call.message.chat.id, ios_text)

@bot.callback_query_handler(func=lambda call: call.data == "instruction_android")
def instruction_android(call):
    android_text = "Для Android: вставьте ключ в поле настроек VPN."
    bot.send_message(call.message.chat.id, android_text)

@bot.callback_query_handler(func=lambda call: call.data == "instruction_windows")
def instruction_windows(call):
    windows_text = "Для Windows: вставьте ключ в поле настроек VPN."
    bot.send_message(call.message.chat.id, windows_text)


@bot.callback_query_handler(func=lambda call: call.data == "generate_key")
def button_handler(call):
    username = call.from_user.username or str(call.from_user.id)
    # Проверяем, есть ли уже ключ для пользователя
    existing_key = check_existing_key(call.from_user.id)

    if existing_key:
        # Отправляем уже существующий ключ, если он активен
        bot.send_message(call.message.chat.id, "У вас уже есть активный VPN ключ:")
        bot.send_message(call.message.chat.id, existing_key)
    else:
        try:
            # Проверяем, существует ли пользователь в базе
            if user_exists(username):
                bot.send_message(call.message.chat.id, "Пользователь уже существует.")
                return

            # Создаем новый ключ
            created_username = create_key(username)
            if created_username:
                vpn_link = get_key(created_username)
                servers = get_available_servers()
                if servers:
                    server_id = servers[0][0]
                    key = vpn_link  # предположительно, это ваш ключ

                    # Сохраняем нового пользователя с ключом в базу данных
                    cursor.execute(
                        "INSERT INTO users (telegram_id, username, vpn_link, server_id, key) VALUES (?, ?, ?, ?, ?)",
                        (call.from_user.id, username, vpn_link, server_id, key)
                    )
                    conn.commit()
                    bot.send_message(call.message.chat.id, "Ваш новый ключ:")
                    bot.send_message(call.message.chat.id, vpn_link)
                else:
                    bot.send_message(call.message.chat.id, "Нет доступных серверов.")
        except requests.exceptions.RequestException as e:
            bot.send_message(call.message.chat.id, f"Ошибка при создании ключа: {e}")
        except sqlite3.Error as e:
            bot.send_message(call.message.chat.id, f"Ошибка базы данных: {e}")


@bot.callback_query_handler(func=lambda call: call.data == "check_traffic")
def check_traffic_handler(call):
    try:
        username = call.from_user.username or str(call.from_user.id)
        response = requests.get(f"{API_URL}/{username}", headers=HEADERS)
        response.raise_for_status()
        used_traffic = response.json().get("used_traffic", 0) / (1024 * 1024)
        traffic_msg = f"{used_traffic:.2f} МБ" if used_traffic < 1024 else f"{used_traffic / 1024:.2f} ГБ"
        bot.send_message(call.message.chat.id, f"Ваш потраченный трафик: {traffic_msg}")
    except requests.exceptions.RequestException as e:
        bot.send_message(call.message.chat.id, f"Ошибка запроса: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "delete_key")
def delete_key_handler(call):
    existing_key = check_existing_key(call.from_user.id)
    if existing_key:
        try:
            delete_key(call.from_user.id, call.from_user.username or str(call.from_user.id))
            bot.send_message(call.message.chat.id, "Ваш ключ был успешно удалён.")
        except requests.exceptions.RequestException as e:
            bot.send_message(call.message.chat.id, f"Ошибка при удалении ключа: {e}")
    else:
        bot.send_message(call.message.chat.id, "У вас нет активного ключа для удаления.")

bot.polling()
