# handlers/start.py
from telegram import Update, InputFile
from telegram.ext import ContextTypes
from config import START_IMG
from keyboards.menus import main_menu


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    caption = (
        "👋 Привіт! Я інформаційний бот *КиївУсюди*.\n"
        "Оберіть опцію нижче:"
    )

    # Якщо є стартове фото — надсилаємо його
    if START_IMG and START_IMG.strip() != "":
        try:
            with open(START_IMG, "rb") as img:
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=InputFile(img),
                    caption=caption,
                    parse_mode="Markdown",
                    reply_markup=main_menu()
                )
                return
        except Exception:
            pass

    # Якщо фото немає — надсилаємо текст
    await context.bot.send_message(
        chat_id=chat_id,
        text=caption,
        parse_mode="Markdown",
        reply_markup=main_menu()
    )
