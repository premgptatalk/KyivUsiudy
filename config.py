# config.py
import os
from dotenv import load_dotenv

# Завантажуємо .env у корені проєкту
load_dotenv()

# ----------------------------
# Базові параметри
# ----------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не знайдено в .env")

# ----------------------------
# Параметри погоди
# ----------------------------
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
CITY = os.getenv("CITY", "Kyiv")
LAT = float(os.getenv("LAT", "50.4501"))
LON = float(os.getenv("LON", "30.5234"))

# ----------------------------
# Новини
# ----------------------------
TSN_RSS = os.getenv("TSN_RSS", "https://kyiv.tsn.ua/rss")

# ----------------------------
# Тривоги
# ----------------------------
ALERTS_API = os.getenv("ALERTS_API", "https://api.alerts.in.ua/v1/alerts/active.json")
ALERTS_TOKEN = os.getenv("ALERTS_TOKEN", "")

# ----------------------------
# Стартове фото
# ----------------------------
START_IMG = os.getenv("START_IMG", None)

# ----------------------------
# Файл для збереження налаштувань користувачів
# ----------------------------
USERS_FILE = os.getenv("USERS_FILE", "users.json")
