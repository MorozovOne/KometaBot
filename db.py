import sqlite3
import time

'''# Функция для очистки базы данных
def clear_database():
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Устанавливаем режим WAL, чтобы избежать блокировки при работе с базой
        cursor.execute("PRAGMA journal_mode=WAL")

        # Закрываем соединение перед удалением таблиц, чтобы избежать блокировки
        conn.commit()
        conn.close()

        time.sleep(1)  # Пауза перед выполнением дальнейших операций

        # Теперь открываем новое соединение для очистки базы
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Очистим таблицы (если они существуют)
        cursor.execute("DROP TABLE IF EXISTS users")
        cursor.execute("DROP TABLE IF EXISTS servers")

        conn.commit()
        conn.close()
        print("База данных очищена.")
    except sqlite3.OperationalError as e:
        print(f"Ошибка: {e}")
        time.sleep(2)  # Пауза на случай блокировки и повторная попытка

# Функция для создания таблиц
def create_tables():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Создание таблицы servers
    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS servers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT NOT NULL,
        name TEXT NOT NULL
    )
    """)

    # Создание таблицы users с добавленным полем active
    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id TEXT NOT NULL,
        username TEXT NOT NULL,
        key TEXT NOT NULL,
        server_id INTEGER NOT NULL,
        active INTEGER DEFAULT 1,  -- Добавлено поле active для состояния подписки
        FOREIGN KEY (server_id) REFERENCES servers(id)
    )
    """)

    conn.commit()
    conn.close()
    print("Таблицы созданы.")'''

# Функция для добавления сервера
def add_server(ip, name):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO servers (ip, name) VALUES (?, ?)", (ip, name))

    conn.commit()
    conn.close()
    print(f"Сервер {name} добавлен.")

# Функция для добавления пользователя с новым полем active
def add_user(telegram_id, username, key, server_id, active=1):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO users (telegram_id, username, key, server_id, active) VALUES (?, ?, ?, ?, ?)",
                   (telegram_id, username, key, server_id, active))

    conn.commit()
    conn.close()
    print(f"Пользователь {username} добавлен. Статус подписки: {'Активна' if active else 'Неактивна'}")

# Функция для подсчета количества пользователей на сервере
def count_users_on_server(server_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users WHERE server_id = ?", (server_id,))
    count = cursor.fetchone()[0]

    conn.close()
    return count

'''# Очистка базы данных и создание новой
def reset_database():
    clear_database()  # Очистить старую базу данных

    create_tables()  # Создать новую структуру базы данных

    # Добавить серверы
    add_server('193.124.44.29', 'Server 1')
    add_server('194.87.220.214', 'Server 2')

    print("База данных и сервера успешно созданы.")'''

# Функция для добавления столбца vpn_link в таблицу users
def add_column_vpn_link():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Проверяем, существует ли столбец vpn_link в таблице users
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]  # Получаем имена всех столбцов

    if "vpn_link" not in column_names:
        cursor.execute("ALTER TABLE users ADD COLUMN vpn_link TEXT")
        print("Столбец vpn_link добавлен.")
    else:
        print("Столбец vpn_link уже существует.")

    conn.commit()
    conn.close()

# Вызов функции для очистки и пересоздания базы данных
#reset_database()

# Вызов добавления столбца
add_column_vpn_link()

# Пример подсчета пользователей на сервере 1
user_count = count_users_on_server(1)
print(f"Количество пользователей на сервере 1: {user_count}")
