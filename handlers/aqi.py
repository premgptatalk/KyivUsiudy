# handlers/aqi.py
import requests
from telegram import Update
from telegram.ext import ContextTypes
from config import OPENWEATHER_API_KEY, LAT, LON
from keyboards.menus import back_button


TIMEOUT = 7


# ---------------------------
# Основна функція AQI
# ---------------------------
def get_aqi_text() -> str:
    if not OPENWEATHER_API_KEY:
        return (
            "❗ Якість повітря недоступна, бо не задано ключ OpenWeather.\n"
            "Додай у .env:\nOPENWEATHER_API_KEY=тут_твій_ключ"
        )

    url = (
        f"https://api.openweathermap.org/data/2.5/air_pollution?"
        f"lat={LAT}&lon={LON}&appid={OPENWEATHER_API_KEY}"
    )

    try:
        resp = requests.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        aqi = data.get("list", [{}])[0].get("main", {}).get("aqi", None)
    except requests.HTTPError as e:
        code = e.response.status_code if e.response else "?"
        if code == 401:
            return "❗ Ключ OpenWeather для AQI некоректний або відсутній (HTTP 401)."
        return f"❌ Помилка OpenWeather AQI: HTTP {code}"
    except Exception:
        return "❌ Не вдалося завантажити якість повітря."

    labels = {
        1: "1 — Дуже добре 😊 (чисте повітря)",
        2: "2 — Добре 🙂 (нормально)",
        3: "3 — Задовільне 😐 (можливий дискомфорт у чутливих груп)",
        4: "4 — Погане 😷 (ризик для здоров‘я)",
        5: "5 — Дуже погане 🤢 (шкідливо для всіх)",
    }

    status = labels.get(aqi, "Невідоме значення AQI")
    return f"💨 *Якість повітря в Києві:*\n{status}"


# ---------------------------
# Callback handler — AQI
# ---------------------------
async def handle_aqi_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = get_aqi_text()

    await query.edit_message_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=back_button()
    )
