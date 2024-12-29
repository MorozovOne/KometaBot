from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_instruction_buttons():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Инструкция для IOS/MacOS", callback_data="instruction_ios"))
    markup.add(InlineKeyboardButton("Инструкция для Android", callback_data="instruction_android"))
    return markup

def get_main_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Создать ключ / Аккаунт", callback_data="generate_key"))
    markup.add(InlineKeyboardButton("Удалить ключ / Аккаунт", callback_data="delete_key"))
    markup.add(InlineKeyboardButton("Инструкция", callback_data="show_instructions"))
    markup.add(InlineKeyboardButton("Скачать приложение", callback_data="show_app"))
    return markup
