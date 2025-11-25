# handlers/weather.py
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

from config import OPENWEATHER_API_KEY, CITY
from keyboards.menus import back_button


TIMEOUT = 7


# ---------------------------
# Форматування одного запису
# ---------------------------
def _format_weather(entry):
    try:
        desc = entry["weather"][0]["description"].capitalize()
        temp = entry["main"]["temp"]
        clouds = entry["clouds"]["all"]
        wind = entry["wind"]["speed"]
        pop = int(entry.get("pop", 0) * 100)
    except Exception:
        return "❌ Дані погоди некоректні"

    return (
        f"📌 {desc}\n"
        f"🌡 Температура — *{temp:.1f}°C*\n"
        f"💦 Опади — {pop}%\n"
        f"☁️ Хмарність — {clouds}%\n"
        f"💨 Вітер — {wind:.1f} м/с"
    )


# ---------------------------
# Завантаження прогнозу
# ---------------------------
def _load_forecast():
    if not OPENWEATHER_API_KEY:
        return None, "❗ OpenWeather ключ не вказано."

    url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?q={CITY}&appid={OPENWEATHER_API_KEY}&units=metric&lang=uk"
    )

    try:
        r = requests.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        return data.get("list", []), None
    except Exception:
        return None, "❌ Не вдалося отримати прогноз погоди."


# ---------------------------
# Команда — погода сьогодні
# ---------------------------
async def weather_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lst, err = _load_forecast()
    if err:
        return err

    entry = lst[0]
    text = f"🌤 *Погода в {CITY} на сьогодні*\n\n" + _format_weather(entry)
    return text


# ---------------------------
# Команда — погода завтра
# ---------------------------
async def weather_tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lst, err = _load_forecast()
    if err:
        return err

    idx = min(8, len(lst) - 1)
    entry = lst[idx]
    text = f"⛅️ *Погода в {CITY} на завтра*\n\n" + _format_weather(entry)
    return text


# ---------------------------
# Команда — 5 днів
# ---------------------------
async def weather_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lst, err = _load_forecast()
    if err:
        return err

    by_date = {}
    for entry in lst:
        dt = datetime.utcfromtimestamp(entry["dt"])
        score = abs(dt.hour - 12)
        d = dt.date()
        if d not in by_date or score < by_date[d][0]:
            by_date[d] = (score, entry)

    uk_days = {
        "Monday": "Понеділок",
        "Tuesday": "Вівторок",
        "Wednesday": "Середа",
        "Thursday": "Четвер",
        "Friday": "Пʼятниця",
        "Saturday": "Субота",
        "Sunday": "Неділя",
    }

    lines = ["📅 *Прогноз на 5 днів*\n"]
    for i, (d, (_, entry)) in enumerate(sorted(by_date.items())):
        if i >= 5:
            break
        dn = d.strftime("%A %d.%m")
        day_name = uk_days.get(d.strftime("%A"), d.strftime("%A"))
        dn = f"{day_name} {d.strftime('%d.%m')}"
        lines.append(f"*{dn}:*\n" + _format_weather(entry) + "\n")

    return "\n".join(lines).strip()


# ---------------------------
# Головний handler погоди
# ---------------------------
async def handle_weather_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action = query.data  # "weather_today" / "weather_tomorrow" / "weather_week"

    if action == "weather_today":
        text = await weather_today(update, context)
    elif action == "weather_tomorrow":
        text = await weather_tomorrow(update, context)
    elif action == "weather_week":
        text = await weather_week(update, context)
    else:
        text = "❌ Невідома команда погоди."

    await query.edit_message_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=back_button()
    )
