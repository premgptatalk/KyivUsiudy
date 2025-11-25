# handlers/discounts.py
from telegram import Update
from telegram.ext import ContextTypes
from keyboards.menus import back_button


def get_discounts_text() -> str:
    return (
        "🛍 *Знижки в супермаркетах Києва:*\n\n"
        "• [АТБ](https://www.atbmarket.com/)\n"
        "• [Сільпо](https://silpo.ua/offers)\n"
        "• [Фора](https://fora.ua/all-offers)\n"
    )


async def handle_discounts_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = get_discounts_text()

    await query.edit_message_text(
        text=text,
        parse_mode="Markdown",
        disable_web_page_preview=False,
        reply_markup=back_button()
    )
