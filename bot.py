from telegram.ext import ApplicationBuilder
from handlers.start import start
from handlers.menus import menu_callback
from handlers.digest_fsm import digest_fsm

from handlers.weather import handle_weather_callback
from handlers.news import handle_news_callback
from handlers.alerts import handle_alerts_callback
from handlers.aqi import handle_aqi_callback
from handlers.rates import handle_rates_callback
from handlers.discounts import handle_discounts_callback
from handlers.afisha import handle_afisha_callback

from config import BOT_TOKEN


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # команда /start
    app.add_handler(start)

    # FSM
    app.add_handler(digest_fsm)

    # меню
    app.add_handler(menu_callback)

    # інші обробники
    app.add_handler(handle_weather_callback)
    app.add_handler(handle_news_callback)
    app.add_handler(handle_alerts_callback)
    app.add_handler(handle_aqi_callback)
    app.add_handler(handle_rates_callback)
    app.add_handler(handle_discounts_callback)
    app.add_handler(handle_afisha_callback)

    # запуск
    app.run_polling()


if __name__ == "__main__":
    main()
