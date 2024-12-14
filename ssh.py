import time
from threading import Thread
from sshtunnel import SSHTunnelForwarder
import psycopg2

# Конфигурация серверов
SERVERS = [
    #{"host": "193.124.44.29", "port": 8000, "ssh_user": "root", "password": "ouUsJTvsZ"},
    {"host": "213.176.65.44", "port": 8000, "ssh_user": "root", "password": "b8tScUzXyQXV"},
    #{"host": "109.196.101.118", "port": 8000, "ssh_user": "root", "password": "onTAT+8?2Nf.*G"}
]

# Конфигурация подключения к базе данных
DATABASE_CONFIG = {
    "host": "178.253.43.196",
    "dbname": "default_db",
    "user": "gen_user",
    "password": "Luq3I)-IGyEEzo"
}


def get_connection():
    """Функция для получения подключения к PostgreSQL."""
    try:
        connection = psycopg2.connect(**DATABASE_CONFIG)
        return connection
    except psycopg2.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None


def count_users_on_server(server_id):
    """Функция для подсчета количества пользователей на сервере в базе данных PostgreSQL."""
    try:
        conn = get_connection()
        if conn is None:
            return 0

        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE server_id = %s;", (server_id,))
        count = cursor.fetchone()[0]

        cursor.close()
        conn.close()
        return count
    except Exception as e:
        print(f"Ошибка при подсчете пользователей на сервере {server_id}: {e}")
        return 0


def create_ssh_tunnel(server):
    """Функция для создания SSH туннеля с использованием sshtunnel."""
    try:
        with SSHTunnelForwarder(
            (server['host'], 22),
            ssh_username=server['ssh_user'],
            ssh_password=server['password'],
            remote_bind_address=('127.0.0.1', server['port']),
            local_bind_address=('0.0.0.0', server['port'])
        ) as tunnel:
            print(
                f"Туннель для {server['host']} создан, перенаправление порта {server['port']} -> {server['host']}:{server['port']}")

            # Ожидаем 1 час, пока туннель активен
            time.sleep(3600)
            print(f"Туннель для {server['host']} завершён.")
    except Exception as e:
        print(f"Ошибка при создании туннеля для {server['host']}: {e}")


def switch_servers(current_server_idx):
    """Функция для переключения между серверами, учитывая количество пользователей."""
    server = SERVERS[current_server_idx]

    # Получаем количество пользователей на текущем сервере из базы данных
    server_id = current_server_idx + 1  # ID сервера (например, 1 для первого, 2 для второго)
    user_count = count_users_on_server(server_id)
    print(f"Количество пользователей на сервере {server['host']}: {user_count}")

    if user_count > 15:
        print(f"На сервере {server['host']} больше 15 пользователей. Переключаемся на другой сервер...")
        current_server_idx = (current_server_idx + 1) % len(SERVERS)  # Переключаемся на другой сервер

    # Создаем SSH туннель для текущего сервера
    tunnel_thread = Thread(target=create_ssh_tunnel, args=(server,))
    tunnel_thread.start()
    return tunnel_thread, current_server_idx


if __name__ == "__main__":
    current_server_idx = 0
    while True:
        # Переключаемся на следующий сервер, создаём туннель
        tunnel_thread, current_server_idx = switch_servers(current_server_idx)
        tunnel_thread.join()  # Ожидаем завершения текущего туннеля
