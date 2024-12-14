import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import add_user, delete_user, get_available_servers, user_exists
from functions import create_key, get_key, delete_user, refresh_token, check_existing_key, delete_key_from_marzban
from buttons import get_instruction_buttons, get_main_menu

BOT_TOKEN = '7676234253:AAGRJkqR_kvJbKiHSJ1Bczm5wyCBIIghQDs'
bot = telebot.TeleBot(BOT_TOKEN)

refresh_token()

# Обработка команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    # Получаем username, если он есть, иначе используем telegram_id
    username = message.from_user.username or str(message.from_user.id)
    welcome_text = (
        f"Привет! {username}\n\nМы находимся в бета-тестировании\n"
        f"Здесь вы можете создать аккаунт для приложения Кометы\n"
        f"Вы уже можете воспользоваться нашими услугами\n\nМы пока не подключили оплату, но вы можете пока что поддержать нас рублём\n"
        f"donationalerts.com/r/vagabond939\n\nВыберите действие:"
    )

    # Создаем клавиатуру с кнопками
    start_menu = InlineKeyboardMarkup()
    start_menu.add(InlineKeyboardButton("Меню", callback_data="main_menu"))

    # Отправляем приветственное сообщение с кнопкой для основного меню
    bot.send_message(message.chat.id, welcome_text, reply_markup=start_menu)

# Обработка нажатия на кнопку "Основное меню" (после /start)
@bot.callback_query_handler(func=lambda call: call.data == "main_menu")
def show_main_menu(call):
    bot.send_message(call.message.chat.id, "Выберите действие:", reply_markup=get_main_menu())

@bot.callback_query_handler(func=lambda call: call.data == "show_app")
def show_instructions(call):
    bot.send_message(call.message.chat.id, "Скачать приложение можно по этой ссылке: kometavpn.ru")

@bot.callback_query_handler(func=lambda call: call.data == "show_instructions")
def show_instructions(call):
    bot.send_message(call.message.chat.id, "Выберите платформу:", reply_markup=get_instruction_buttons())

@bot.callback_query_handler(func=lambda call: call.data.startswith("instruction_"))
def send_instruction(call):
    platform = call.data.split("_")[1]
    instructions = {
        "ios": "1. Скачайте приложение V2Box с App Store\n"
               "2. Скопируйте ключ, который вам отправит бот\n"
               "3. Откройте приложение, нажмите на плюсик, затем выберите первую кнопку, чтобы вставить ключ из буфера обмена",

        "android": "1. Скачайте приложение v2rayNG из Google Play\n"
                   "2. Скопируйте ключ, который вам отправит бот\n"
                   "3. Откройте приложение, нажмите на плюсик, затем выберите первую кнопку, чтобы вставить ключ из буфера обмена",
    }
    bot.send_message(call.message.chat.id, instructions.get(platform, "Инструкция не найдена."))

@bot.callback_query_handler(func=lambda call: call.data == "generate_key")
def generate_key(call):
    username = call.from_user.username or str(call.from_user.id)  # Используем username, если есть
    existing_key = check_existing_key(call.from_user.id)

    if existing_key:
        bot.send_message(call.message.chat.id, "У вас уже есть аккаунт")
        #bot.send_message(call.message.chat.id, "У вас уже есть активный VPN ключ:")
        #bot.send_message(call.message.chat.id, existing_key)
    else:
        bot.send_message(call.message.chat.id, "Придумайте пароль:")
        bot.register_next_step_handler(call.message, handle_password, username)

@bot.message_handler(func=lambda message: message.text)
def handle_password(message, username):
    password = message.text
    existing_key = check_existing_key(message.from_user.id)

    # Получаем telegram_id пользователя
    telegram_id = message.from_user.id

    # Если у пользователя есть username, то используем его, иначе используем telegram_id
    username = message.from_user.username or str(telegram_id)

    if user_exists(username):
        # Обновляем ключ и сохраняем новый пароль
        new_username = create_key(username)
        vless_key = get_key(new_username)
        servers = get_available_servers()
        if servers:
            server_id = servers[0]["id"]
            # Обновляем данные пользователя в базе
            add_user(telegram_id, username, vless_key, server_id, password, True, True, 0)
            bot.send_message(
                message.chat.id,
                f"Для приложения Кометы\nЛогин: {username}\nПароль: {password}"
            )
            #bot.send_message(message.chat.id, "Ваш новый ключ:")
            #bot.send_message(message.chat.id, vless_key)
        else:
            bot.send_message(message.chat.id, "Нет доступных серверов.")
    else:
        # Создаём нового пользователя и ключ
        new_username = create_key(username)
        vless_key = get_key(new_username)
        servers = get_available_servers()
        if servers:
            server_id = servers[0]["id"]
            # Добавляем нового пользователя
            add_user(telegram_id, username, vless_key, server_id, password, True, True, 0)
            bot.send_message(
                message.chat.id,
                f"Для приложения Кометы\nЛогин: {username}\nПароль: {password}"
            )
            # bot.send_message(message.chat.id, "Ваш новый ключ:")
            # bot.send_message(message.chat.id, vless_key)
        else:
            bot.send_message(message.chat.id, "Нет доступных серверов.")

@bot.callback_query_handler(func=lambda call: call.data == "delete_key")
def delete_key_handler(call):
    username = call.from_user.username or str(call.from_user.id)  # Используем username, если есть

    # Удаление пользователя из вашей базы данных
    delete_user(username)  # Убедитесь, что эта функция удаляет пользователя из вашей базы

    # Отправка запроса на удаление ключа в Marzban
    success = delete_key_from_marzban(username)

    if success:
        bot.send_message(call.message.chat.id, "Ваш ключ был успешно удалён.")
    else:
        bot.send_message(call.message.chat.id, "Произошла ошибка при удалении ключа.")


bot.polling()
