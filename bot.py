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
    username = message.from_user.username or str(message.from_user.id)
    welcome_text = (
        f"Привет! {username}\n\nМы находимся в бета-тестировании\n"
        f"Здесь вы можете создать аккаунт для приложения Кометы\n"
        f"Вы уже можете воспользоваться нашими услугами\n\nМы пока не прикрутили оплату, но вы можете пока что поддержать нас рублём на свою совесть. Ключ стоит 50 рублей.\n"
        f"donationalerts.com/r/vagabond939\n\nВыберите действие:"
    )

    start_menu = InlineKeyboardMarkup()
    start_menu.add(InlineKeyboardButton("Меню", callback_data="main_menu"))
    bot.send_message(message.chat.id, welcome_text, reply_markup=start_menu)

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
    username = call.from_user.username or str(call.from_user.id)
    existing_key = check_existing_key(call.from_user.id)

    if existing_key:
        bot.send_message(call.message.chat.id, "У вас уже есть активный аккаунт и VPN ключ:")
        bot.send_message(call.message.chat.id, existing_key)
    else:
        bot.send_message(call.message.chat.id, "Придумайте пароль:")
        bot.register_next_step_handler(call.message, handle_password, username)

def handle_password(message, username):
    password = message.text
    existing_key = check_existing_key(message.from_user.id)

    telegram_id = message.from_user.id
    username = username or str(telegram_id)

    if user_exists(username):
        new_username = create_key(username)
        vless_key = get_key(new_username)
        servers = get_available_servers()
        if servers:
            server_id = servers[0]["id"]
            add_user(telegram_id, username, vless_key, server_id, password, True, True, 0)
            bot.send_message(
                message.chat.id,
                f"Для приложения Кометы\nЛогин: {username}\nПароль: {password}"
            )
            bot.send_message(message.chat.id, "Ваш новый ключ:")
            bot.send_message(message.chat.id, vless_key)
        else:
            bot.send_message(message.chat.id, "Нет доступных серверов.")
    else:
        new_username = create_key(username)
        vless_key = get_key(new_username)
        servers = get_available_servers()
        if servers:
            server_id = servers[0]["id"]
            add_user(telegram_id, username, vless_key, server_id, password, True, True, 0)
            bot.send_message(
                message.chat.id,
                f"Для приложения Кометы\nЛогин: {username}\nПароль: {password}"
            )
            bot.send_message(message.chat.id, "Ваш новый ключ:")
            bot.send_message(message.chat.id, vless_key)
        else:
            bot.send_message(message.chat.id, "Нет доступных серверов.")

@bot.callback_query_handler(func=lambda call: call.data == "delete_key")
def delete_key_handler(call):
    username = call.from_user.username or str(call.from_user.id)
    delete_user(username)
    success = delete_key_from_marzban(username)

    if success:
        bot.send_message(call.message.chat.id, "Ваш ключ был успешно удалён.")
    else:
        bot.send_message(call.message.chat.id, "Произошла ошибка при удалении ключа.")

@bot.callback_query_handler(func=lambda call: call.data == "pay_key")
def pay_key(call):
    bot.send_message(
        call.message.chat.id,
        "Оплата ключа стоит 50 рублей. Пожалуйста, поддержите нас рублём! Мы пока не прикрутили полноценную оплату, но вы можете оплатить на свою совесть, чтобы поддержать проект.\n\n"
        "Ссылка для оплаты: [Оплатить ключ](https://www.donationalerts.com/r/vagabond939)",
        parse_mode="Markdown"
    )

bot.polling()
