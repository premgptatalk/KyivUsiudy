# handlers/rates.py
import requests
from telegram import Update
from telegram.ext import ContextTypes
from keyboards.menus import back_button


TIMEOUT = 7


# ---------------------------
# ПриватБанк API
# ---------------------------
def get_rates_privat():
    try:
        from datetime import datetime
        date_str = datetime.now().strftime("%d.%m.%Y")

        url = f"https://api.privatbank.ua/p24api/exchange_rates?json&date={date_str}"
        r = requests.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()

        rates = data.get("exchangeRate", [])
    except Exception:
        return "❌ ПриватБанк: недоступно."

    currencies = ["USD", "EUR", "GBP", "PLN"]
    lines = []

    for code in currencies:
        entry = next((e for e in rates if e.get("currency") == code), None)
        if entry and entry.get("saleRate") and entry.get("purchaseRate"):
            buy = entry["purchaseRate"]
            sale = entry["saleRate"]
            lines.append(f"• *{code}:* Купівля — {buy:.2f}₴ | Продаж — {sale:.2f}₴")
        else:
            lines.append(f"• {code}: дані відсутні")

    return "🏦 *ПриватБанк:*\n" + "\n".join(lines)


# ---------------------------
# Монобанк API
# ---------------------------
def get_rates_mono():
    try:
        url = "https://api.monobank.ua/bank/currency"
        r = requests.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return "❌ Монобанк: недоступно."

    currency_map = {840: "USD", 978: "EUR", 826: "GBP", 985: "PLN"}

    lines = []
    for item in data:
        cA = item.get("currencyCodeA")
        cB = item.get("currencyCodeB")

        if cA in currency_map and cB == 980:
            code = currency_map[cA]
            buy = item.get("rateBuy")
            sell = item.get("rateSell")

            if buy and sell:
                lines.append(f"• *{code}:* Купівля — {buy:.2f}₴ | Продаж — {sell:.2f}₴")

    return "💳 *Монобанк:*\n" + ("\n".join(lines) if lines else "Немає даних.")


# ---------------------------
# НБУ API
# ---------------------------
def get_rates_nbu():
    try:
        url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
        r = requests.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return "❌ НБУ: недоступно."

    currencies = ["USD", "EUR", "GBP", "PLN"]
    lines = []

    for code in currencies:
        entry = next((e for e in data if e.get("cc") == code), None)
        if entry:
            lines.append(f"• *{code}:* {entry['rate']:.2f}₴")
        else:
            lines.append(f"• {code}: дані відсутні")

    return "📊 *НБУ:*\n" + "\n".join(lines)


# ---------------------------
# Callback — курси валют
# ---------------------------
async def handle_rates_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = (
        f"{get_rates_privat()}\n\n"
        f"{get_rates_mono()}\n\n"
        f"{get_rates_nbu()}"
    )

    await query.edit_message_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=back_button()
    )
