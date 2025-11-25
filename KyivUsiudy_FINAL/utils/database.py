# utils/database.py
import json
import os
from config import USERS_FILE


# ---------------------------
# Завантаження всіх користувачів
# ---------------------------
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}

    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


# ---------------------------
# Зберегти словник користувачів у файл
# ---------------------------
def save_users(data: dict):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ---------------------------
# Чи підписаний користувач
# (старий режим "digest" — опціонально)
# ---------------------------
def is_subscribed(user_id: str) -> bool:
    users = load_users()
    return user_id in users


# ---------------------------
# Відписатися
# ---------------------------
def unsubscribe(user_id: str) -> bool:
    users = load_users()

    if user_id in users:
        del users[user_id]
        save_users(users)
        return True

    return False
