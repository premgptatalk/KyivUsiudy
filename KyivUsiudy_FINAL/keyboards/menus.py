from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# ---------------------------
# Головне меню
# ---------------------------
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🌤 Погода", callback_data="menu_weather")],
        [InlineKeyboardButton("📰 Новини", callback_data="news_latest")],
        [InlineKeyboardButton("🚨 Тривоги", callback_data="alerts_now")],
        [InlineKeyboardButton("💨 AQI", callback_data="aqi_now")],
        [InlineKeyboardButton("💸 Курси валют", callback_data="rates_now")],
        [InlineKeyboardButton("🛍 Знижки", callback_data="discounts_now")],
        [InlineKeyboardButton("🎭 Афіша Києва", callback_data="menu_afisha")],
        [InlineKeyboardButton("📬 Персональний дайджест", callback_data="digest_fsm_start")],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Назад", callback_data="menu_back")]
    ])


# ---------------------------
# Підменю (залишаємо тільки для погоди та афіші)
# ---------------------------
def weather_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("☀️ Сьогодні", callback_data="weather_today")],
        [InlineKeyboardButton("⛅ Завтра", callback_data="weather_tomorrow")],
        [InlineKeyboardButton("📅 5 днів", callback_data="weather_week")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="menu_back")]
    ])


def afisha_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎵 Концерти", callback_data="afisha_concerts")],
        [InlineKeyboardButton("🎭 Театр", callback_data="afisha_theatre")],
        [InlineKeyboardButton("🎬 Кіно", callback_data="afisha_cinema")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="menu_back")]
    ])


# ---------------------------
# Основний callback меню
# ---------------------------
async def menu_callback(update, context):
    query = update.callback_query
    data = query.data
    await query.answer()

    # Назад
    if data == "menu_back":
        await query.edit_message_text(
            "👋 Привіт! Я інформаційний бот *КиївУсюди*.\nОберіть опцію:",
            parse_mode="Markdown",
            reply_markup=main_menu()
        )
        return

    # Погода — лишається підменю
    if data == "menu_weather":
        await query.edit_message_text("🌤 Погода — оберіть:", reply_markup=weather_menu())
        return

    # Афіша — лишається підменю
    if data == "menu_afisha":
        await query.edit_message_text("🎭 Афіша — оберіть:", reply_markup=afisha_menu())
        return
