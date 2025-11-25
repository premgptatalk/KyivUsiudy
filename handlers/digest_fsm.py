# handlers/digest_fsm.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    CommandHandler
)
import json
import os
from config import USERS_FILE

# ---------------------------
# СТАНИ FSM
# ---------------------------
CHOOSE_TYPE, CHOOSE_NEWS_COUNT, CONFIRM = range(3)


# ---------------------------
# ЗАВАНТАЖЕННЯ/ЗБЕРЕЖЕННЯ JSON
# ---------------------------
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_users(data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ---------------------------
# СТАРТ FSM
# ---------------------------
async def digest_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    context.user_data["digest"] = {
        "news": False,
        "weather": False,
        "aqi": False,
        "news_count": 3,
    }

    keyboard = [
        [
            InlineKeyboardButton("📰 Новини", callback_data="toggle_news"),
            InlineKeyboardButton("🌤 Погода", callback_data="toggle_weather"),
        ],
        [
            InlineKeyboardButton("🌫 AQI", callback_data="toggle_aqi"),
        ],
        [
            InlineKeyboardButton("Готово", callback_data="done"),
            InlineKeyboardButton("Скасувати", callback_data="cancel"),
        ],
    ]

    await update.callback_query.edit_message_text(
        "📬 *Налаштування персонального дайджесту*\nОберіть категорії:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return CHOOSE_TYPE


# ---------------------------
# ВИБІР ТИПІВ ДАЙДЖЕСТУ
# ---------------------------
async def choose_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    st = context.user_data["digest"]

    # Скасування
    if data == "cancel":
        await query.edit_message_text("❌ Налаштування скасовано.")
        return ConversationHandler.END

    # Перемикачі-news/weather/aqi
    if data == "toggle_news":
        st["news"] = not st["news"]
    elif data == "toggle_weather":
        st["weather"] = not st["weather"]
    elif data == "toggle_aqi":
        st["aqi"] = not st["aqi"]

    # Якщо натиснули "Готово"
    if data == "done":
        if st["news"]:
            keyboard = [
                [InlineKeyboardButton("3 новини", callback_data="cnt_3")],
                [InlineKeyboardButton("Скасувати", callback_data="cancel")],
            ]
            await query.edit_message_text(
                "📰 Оберіть кількість новин:",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return CHOOSE_NEWS_COUNT
        else:
            return await confirm_settings(update, context)

    # Оновлення меню з чекбоксами
    keyboard = [
        [
            InlineKeyboardButton(("✅ " if st["news"] else "📰 ") + "Новини", callback_data="toggle_news"),
            InlineKeyboardButton(("✅ " if st["weather"] else "🌤 ") + "Погода", callback_data="toggle_weather"),
        ],
        [
            InlineKeyboardButton(("✅ " if st["aqi"] else "🌫 ") + "AQI", callback_data="toggle_aqi"),
        ],
        [
            InlineKeyboardButton("Готово", callback_data="done"),
            InlineKeyboardButton("Скасувати", callback_data="cancel"),
        ],
    ]

    await query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))
    return CHOOSE_TYPE


# ---------------------------
# ВИБІР КІЛЬКОСТІ НОВИН
# ---------------------------
async def choose_news_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "cancel":
        await query.edit_message_text("❌ Скасовано.")
        return ConversationHandler.END

    if query.data == "cnt_3":
        context.user_data["digest"]["news_count"] = 3

    return await confirm_settings(update, context)


# ---------------------------
# ПІДТВЕРДЖЕННЯ
# ---------------------------
async def confirm_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    st = context.user_data["digest"]

    msg = "📬 *Підтвердження налаштувань:*\n\n"

    if st["news"]:
        msg += f"📰 Новини: {st['news_count']} новини\n"
    if st["weather"]:
        msg += "🌤 Погода: Київ\n"
    if st["aqi"]:
        msg += "🌫 AQI: Київ\n"

    keyboard = [
        [InlineKeyboardButton("💾 Зберегти", callback_data="save_digest")],
        [InlineKeyboardButton("Скасувати", callback_data="cancel")],
    ]

    await query.edit_message_text(
        msg,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return CONFIRM


# ---------------------------
# ЗБЕРЕЖЕННЯ ДАЙДЖЕСТУ
# ---------------------------
async def save_digest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    data = load_users()
    data[user_id] = context.user_data["digest"]
    save_users(data)

    await query.edit_message_text("✅ Налаштування дайджесту збережено!")
    return ConversationHandler.END


# ---------------------------
# FSM HANDLER
# ---------------------------
digest_fsm = ConversationHandler(
    entry_points=[CallbackQueryHandler(digest_start, pattern="^digest_fsm_start$")],

    states={
        CHOOSE_TYPE: [CallbackQueryHandler(choose_type)],
        CHOOSE_NEWS_COUNT: [CallbackQueryHandler(choose_news_count)],
        CONFIRM: [
            CallbackQueryHandler(save_digest, pattern="save_digest"),
            CallbackQueryHandler(choose_type, pattern="cancel"),
        ],
    },

    fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
)
