import psycopg2
from psycopg2 import sql

# Конфигурация подключения
DATABASE_URL = "postgresql://gen_user:Luq3I)-IGyEEzo@178.253.43.196:5432/default_db"

# Функция для подключения к базе данных
def get_connection():
    return psycopg2.connect(DATABASE_URL)

# Функция для добавления столбца vpn_link в таблицу users
def add_column_vpn_link():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Проверяем, существует ли столбец vpn_link
        cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='users' AND column_name='vpn_link';
        """)
        result = cursor.fetchone()

        if not result:
            cursor.execute("ALTER TABLE users ADD COLUMN vpn_link TEXT;")
            print("Столбец vpn_link добавлен.")
        else:
            print("Столбец vpn_link уже существует.")

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Ошибка при добавлении столбца: {e}")

# Функция для добавления сервера
def add_server(ip, name):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO servers (address, name) VALUES (%s, %s) RETURNING id;", (ip, name))
        server_id = cursor.fetchone()[0]

        conn.commit()
        conn.close()
        print(f"Сервер {name} добавлен с ID {server_id}.")
    except Exception as e:
        print(f"Ошибка при добавлении сервера: {e}")

# Функция для добавления пользователя
def add_user(telegram_id, username, key, server_id, active=True):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO users (telegram_id, username, key, server_id, active)
        VALUES (%s, %s, %s, %s, %s) RETURNING id;
        """, (telegram_id, username, key, server_id, active))
        user_id = cursor.fetchone()[0]

        conn.commit()
        conn.close()
        print(f"Пользователь {username} добавлен с ID {user_id}. Статус подписки: {'Активна' if active else 'Неактивна'}.")
    except Exception as e:
        print(f"Ошибка при добавлении пользователя: {e}")

# Функция для подсчета количества пользователей на сервере
def count_users_on_server(server_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM users WHERE server_id = %s;", (server_id,))
        count = cursor.fetchone()[0]

        conn.close()
        return count
    except Exception as e:
        print(f"Ошибка при подсчете пользователей: {e}")
        return 0

# Пример вызова функций
if __name__ == "__main__":
    # Добавление столбца vpn_link
    add_column_vpn_link()

    # Пример добавления сервера
    add_server('103.249.134.150', 'Server 1')
    #add_server('213.176.65.44', 'Server 2')

    # Пример добавления пользователя
    add_user(
        telegram_id='123456789',
        username='test_user',
        key='vless-test-key',
        server_id=1,
        active=True
    )

    # Пример подсчета пользователей на сервере
    user_count = count_users_on_server(1)
    print(f"Количество пользователей на сервере 1: {user_count}")
