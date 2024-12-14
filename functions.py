import requests
from database import user_exists, add_user, delete_user, get_available_servers, get_user_key

API_URL = "http://127.0.0.1:8000/api/user"
TOKEN_URL = "http://127.0.0.1:8000/api/admin/token"
HEADERS = {
    "accept": "application/json",
    "Content-Type": "application/json"
}

def refresh_token():
    global HEADERS
    try:
        response = requests.post(
            TOKEN_URL,
            headers={"accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "", "username": "admin", "password": "admin", "scope": "", "client_id": "", "client_secret": ""}
        )
        response.raise_for_status()
        HEADERS["Authorization"] = f"Bearer {response.json()['access_token']}"
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при обновлении токена: {e}")

# Проверка существующего ключа
def check_existing_key(telegram_id):
    return get_user_key(telegram_id)

# Получение ключа пользователя
def get_key(username):
    if username is None:
        raise ValueError("Username cannot be None")
    response = requests.get(f"{API_URL}/{username}", headers=HEADERS)
    response.raise_for_status()
    return response.json()["links"][0]

# Создание нового ключа
def create_key(username):
    if user_exists(username):
        return None
    payload = {
        "username": username,
        "proxies": {"vless": {"id": "35e4e39c-7d5c-4f4b-8b71-558e4f37ff53"}},
        "inbounds": {"vless": ["VLESS TCP REALITY"]},
        "expire": 0,
        "data_limit": 0,
        "data_limit_reset_strategy": "no_reset",
        "status": "active",
        "note": "",
        "on_hold_timeout": "2023-11-03T20:30:00",
        "on_hold_expired": "false"
    }
    response = requests.post(API_URL, json=payload, headers=HEADERS)
    if response.status_code == 200:
        return username
    else:
        return None

def delete_key_from_marzban(username):
    try:
        response = requests.delete(f"{API_URL}/{username}", headers=HEADERS)
        response.raise_for_status()
        if response.status_code == 200:
            return True  # Успешное удаление
        else:
            return False  # Ошибка при удалении
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при удалении ключа: {e}")
        return False
