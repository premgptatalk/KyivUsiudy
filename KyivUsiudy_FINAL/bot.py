import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
)

from config import BOT_TOKEN

# handlers
from handlers.start import start
from handlers.digest_fsm import digest_fsm
from handlers.weather import handle_weather_callback
from handlers.news import handle_news_callback
from handlers.alerts import handle_alerts_callback
from handlers.aqi import handle_aqi_callback
from handlers.rates import handle_rates_callback
from handlers.discounts import handle_discounts_callback
from handlers.afisha import handle_afisha_callback

# menu
from keyboards.menus import menu_callback


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    # FSM
    app.add_handler(digest_fsm)

    # Меню
    app.add_handler(CallbackQueryHandler(menu_callback, pattern="^menu_"))

    # Погода
    app.add_handler(CallbackQueryHandler(handle_weather_callback, pattern="^weather_"))

    # Новини
    app.add_handler(CallbackQueryHandler(handle_news_callback, pattern="^news_"))

    # Тривоги
    app.add_handler(CallbackQueryHandler(handle_alerts_callback, pattern="^alerts_"))

    # AQI
    app.add_handler(CallbackQueryHandler(handle_aqi_callback, pattern="^aqi_"))

    # Курси валют
    app.add_handler(CallbackQueryHandler(handle_rates_callback, pattern="^rates_"))

    # Знижки
    app.add_handler(CallbackQueryHandler(handle_discounts_callback, pattern="^discounts_"))

    # Афіша
    app.add_handler(CallbackQueryHandler(handle_afisha_callback, pattern="^afisha_"))

    print("🔥 Bot is running…")
    app.run_polling()


if __name__ == "__main__":
    main()
