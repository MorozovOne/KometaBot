import sqlite3
import time
from threading import Thread
from sshtunnel import SSHTunnelForwarder

# Конфигурация серверов
SERVERS = [
    {"host": "193.124.44.29", "port": 8000, "ssh_user": "root", "password": "ouUsJTvsZ"},
    {"host": "194.87.220.214", "port": 8000, "ssh_user": "root", "password": "j6WSp7.6yp*Kk8"}
]


# Функция для подсчета количества пользователей на сервере в базе данных
def count_users_on_server(server_id):
    """Функция для подсчета количества пользователей на сервере по базе данных."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users WHERE server_id = ?", (server_id,))
    count = cursor.fetchone()[0]

    conn.close()
    return count


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

            # Ожидаем 5 минут, пока туннель активен
            time.sleep(3600)  # Можно заменить на более подходящее время
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
        print(f"На сервере {server['host']} больше 5 пользователей. Переключаемся на другой сервер...")
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
