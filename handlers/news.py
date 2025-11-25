# handlers/news.py
import feedparser
from telegram import Update
from telegram.ext import ContextTypes
from config import TSN_RSS
from keyboards.menus import back_button


# ---------------------------
# Отримання останніх новин
# ---------------------------
def get_latest_news(limit: int = 5) -> str:
    feed = feedparser.parse(TSN_RSS)

    if not feed.entries:
        return "❌ Новини недоступні."

    text = "📰 *Останні новини:*\n\n"

    for entry in feed.entries[:limit]:
        title = entry.title
        link = entry.link
        text += f"• [{title}]({link})\n"

    return text


# ---------------------------
# CallbackHandler — меню новин
# ---------------------------
async def handle_news_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = get_latest_news(limit=5)

    await query.edit_message_text(
        text=text,
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=back_button()
    )
