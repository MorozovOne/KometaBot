import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

DATABASE_URL = "postgresql://gen_user:Luq3I)-IGyEEzo@178.253.43.196:5432/default_db"

# Подключение к базе данных
def get_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None

# Проверка наличия пользователя
def user_exists(username):
    conn = get_connection()
    if not conn:
        return False
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            return bool(cursor.fetchone())
    finally:
        conn.close()

# Добавление нового пользователя
def add_user(telegram_id, username, vless_key, server_id, password, extension_access, desktop_access, balance):
    conn = get_connection()
    if not conn:
        return
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (username, telegram_id, password, vless_key, extension_access, desktop_access, balance, server_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (username) 
                DO UPDATE SET 
                    password = EXCLUDED.password,
                    vless_key = EXCLUDED.vless_key,
                    extension_access = EXCLUDED.extension_access,
                    desktop_access = EXCLUDED.desktop_access,
                    balance = EXCLUDED.balance,
                    server_id = EXCLUDED.server_id
                RETURNING id;
                """,
                (username, telegram_id, password, vless_key, extension_access, desktop_access, balance, server_id),
            )
            conn.commit()
    finally:
        conn.close()

def delete_user(username):
    conn = get_connection()
    if not conn:
        return
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE username = %s", (str(username),))  # Преобразуем vless_key в строку
            conn.commit()
    finally:
        conn.close()

# Получение VPN ссылки по telegram_id
def get_user_key(telegram_id):
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT vless_key FROM users WHERE telegram_id = %s", (telegram_id,))
            result = cursor.fetchone()
            return result["vless_key"] if result else None
    finally:
        conn.close()

# Получение списка доступных серверов
def get_available_servers():
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM servers")
            return cursor.fetchall()
    finally:
        conn.close()
