# handlers/alerts.py
import requests
from telegram import Update
from telegram.ext import ContextTypes
from config import ALERTS_API, ALERTS_TOKEN
from keyboards.menus import back_button


TIMEOUT = 7


# ---------------------------
# Завантаження тривог
# ---------------------------
def _fetch_alerts():
    headers = {"Authorization": f"Bearer {ALERTS_TOKEN}"} if ALERTS_TOKEN else {}

    try:
        r = requests.get(ALERTS_API, headers=headers, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        return data.get("alerts", []), None
    except requests.HTTPError as e:
        code = e.response.status_code if e.response else "?"
        if code == 401:
            return None, (
                "❗ Дані про тривоги недоступні.\n"
                "ALERTS_TOKEN у .env некоректний або відсутній."
            )
        return None, f"❌ Помилка alerts.in.ua: HTTP {code}"
    except Exception:
        return None, "❌ Не вдалося отримати дані про тривоги."


# ---------------------------
# Нормалізація тексту
# ---------------------------
def _norm(s: str) -> str:
    s = (s or "").replace("\u00A0", " ")  # нерозривний пробіл → звичайний
    for sym in [",", ".", "  "]:
        s = s.replace(sym, " ")
    return " ".join(s.lower().strip().split())


# ---------------------------
# Визначення Києва (місто)
# ---------------------------
def _is_kyiv_city(title: str, loc_type: str | None) -> bool:
    t = _norm(title)
    if loc_type and loc_type.lower() == "city":
        return "київ" in t or "kyiv" in t

    # альтернативні форми
    return any(k in t for k in ["м київ", "місто київ", "kyiv city"]) and "област" not in t


# ---------------------------
# Визначення Київської області
# ---------------------------
def _is_kyiv_region(title: str, loc_type: str | None) -> bool:
    t = _norm(title)
    if loc_type and loc_type.lower() == "oblast":
        return "київ" in t or "kyiv" in t

    return ("київ" in t or "kyiv" in t) and ("област" in t or "oblast" in t)


# ---------------------------
# Формування статусу
# ---------------------------
def _status(active: bool) -> str:
    return "🔴 Активна" if active else "🟢 Немає"


# ---------------------------
# Головна функція тривог
# ---------------------------
def get_alerts_summary() -> str:
    alerts, err = _fetch_alerts()
    if err:
        return err

    kyiv_city = False
    kyiv_region = False

    for a in alerts:
        title = a.get("location_title") or ""
        loc_type = a.get("location_type")

        if _is_kyiv_city(title, loc_type):
            kyiv_city = True

        if _is_kyiv_region(title, loc_type):
            kyiv_region = True

    return (
        "🚨 *Стан повітряних тривог:*\n\n"
        f"🏙 *Київ (місто):* {_status(kyiv_city)}\n"
        f"🛡 *Київська область:* {_status(kyiv_region)}"
    )


# ---------------------------
# Callback handler
# ---------------------------
async def handle_alerts_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = get_alerts_summary()

    await query.edit_message_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=back_button()
    )
