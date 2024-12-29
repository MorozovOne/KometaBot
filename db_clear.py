import psycopg2
from psycopg2 import sql

# Конфигурация подключения
DATABASE_CONFIG = {
    "host": "178.253.43.196",
    "database": "default_db",
    "user": "gen_user",
    "password": "Luq3I)-IGyEEzo"
}

# Функция для подключения к базе данных
def get_connection():
    try:
        return psycopg2.connect(**DATABASE_CONFIG)
    except Exception as e:
        print(f"Ошибка при подключении к базе данных: {e}")
        raise

# Функция для очистки базы данных
def clear_database():
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DROP TABLE IF EXISTS users CASCADE;")
                cursor.execute("DROP TABLE IF EXISTS servers CASCADE;")
                conn.commit()
        print("База данных очищена.")
    except Exception as e:
        print(f"Ошибка при очистке базы данных: {e}")

# Функция для создания таблиц
def create_tables():
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                # Создаем таблицу servers
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS servers (
                    id SERIAL PRIMARY KEY,
                    address TEXT NOT NULL,
                    user_count INTEGER DEFAULT 0
                );
                """)

                # Создаем таблицу users
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    telegram_id INTEGER NOT NULL,
                    password TEXT NOT NULL,
                    vless_key TEXT NOT NULL,
                    extension_access BOOLEAN DEFAULT FALSE,
                    desktop_access BOOLEAN DEFAULT FALSE,
                    balance NUMERIC DEFAULT 0.0,
                    server_id INTEGER REFERENCES servers(id)
                );
                """)
                conn.commit()
        print("Таблицы успешно созданы.")
    except Exception as e:
        print(f"Ошибка при создании таблиц: {e}")

# Функция для добавления сервера
def add_server(address):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO servers (address) VALUES (%s) RETURNING id;", (address,))
                server_id = cursor.fetchone()[0]
                conn.commit()
        print(f"Сервер {address} добавлен с ID {server_id}.")
        return server_id
    except Exception as e:
        print(f"Ошибка при добавлении сервера: {e}")

# Функция для добавления пользователя
def add_user(username, telegram_id, password, vless_key, server_id, extension_access=False, desktop_access=False, balance=0.0):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                INSERT INTO users (username, telegram_id, password, vless_key, extension_access, desktop_access, balance, server_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """, (username, telegram_id, password, vless_key, extension_access, desktop_access, balance, server_id))
                user_id = cursor.fetchone()[0]

                # Обновляем количество пользователей на сервере
                cursor.execute("UPDATE servers SET user_count = user_count + 1 WHERE id = %s;", (server_id,))
                conn.commit()
        print(f"Пользователь {username} добавлен с ID {user_id}.")
        return user_id
    except Exception as e:
        print(f"Ошибка при добавлении пользователя: {e}")

# Функция для подсчета пользователей на сервере
def count_users_on_server(server_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT user_count FROM servers WHERE id = %s;", (server_id,))
                count = cursor.fetchone()[0]
        return count
    except Exception as e:
        print(f"Ошибка при подсчете пользователей на сервере: {e}")
        return 0

# Функция для сброса базы данных
def reset_database():
    #clear_database()  # Очистить базу данных
    #create_tables()   # Создать таблицы

    # Добавить тестовые серверы
    #add_server('193.124.44.29')
    add_server('103.249.134.150')

    print("Сервер успешно добавлен")

# Основной блок выполнения
if __name__ == "__main__":
    reset_database()

    # Пример добавления пользователя
    user_id = add_user(
        username="test_user",
        telegram_id=123456789,
        password="securepassword",
        vless_key="vless-1234-5678",
        server_id=1,
        extension_access=True,
        desktop_access=False,
        balance=100.0
    )

    # Пример подсчета пользователей
    count = count_users_on_server(1)
    print(f"Количество пользователей на сервере 1: {count}")
