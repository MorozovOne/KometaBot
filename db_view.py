import psycopg2
from psycopg2 import sql

# Конфигурация подключения к удаленному серверу PostgreSQL
DATABASE_URL = "postgresql://gen_user:Luq3I)-IGyEEzo@178.253.43.196:5432/default_db"

# Функция для подключения к базе данных
def get_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("Успешное подключение к базе данных!")
        return conn
    except Exception as e:
        print(f"Ошибка при подключении к базе данных: {e}")
        return None

# Функция для получения списка таблиц в базе данных
def get_tables():
    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor()

            # Выполняем запрос для получения списка таблиц
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
            tables = cursor.fetchall()

            conn.close()

            # Выводим список таблиц
            if tables:
                print("Список таблиц в базе данных:")
                for table in tables:
                    print(f"- {table[0]}")
            else:
                print("Таблицы не найдены.")
    except Exception as e:
        print(f"Ошибка при получении таблиц: {e}")

# Функция для просмотра содержимого таблицы
def view_table(table_name):
    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor()

            # Выполняем запрос для получения данных из таблицы
            cursor.execute(sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name)))
            rows = cursor.fetchall()

            conn.close()

            # Выводим содержимое таблицы
            if rows:
                print(f"Содержимое таблицы {table_name}:")
                for row in rows:
                    print(row)
            else:
                print(f"Таблица {table_name} пуста.")
    except Exception as e:
        print(f"Ошибка при просмотре таблицы {table_name}: {e}")

# Основной код для отображения информации о таблицах и их содержимом
def main():
    # Получить и вывести список таблиц
    get_tables()

    # Пример просмотра содержимого таблиц
    table_name = input("Введите имя таблицы для просмотра: ").strip()
    view_table(table_name)

# Вызов основной функции
if __name__ == "__main__":
    main()
