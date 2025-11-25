# handlers/afisha.py
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ContextTypes
from keyboards.menus import back_button


TIMEOUT = 7
UA_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


# ===============================
# HELPERS
# ===============================
def fetch_html(url: str):
    try:
        r = requests.get(url, headers=UA_HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        return r.text
    except:
        return None


def clean(text: str) -> str:
    if not text:
        return ""
    return " ".join(text.replace("\n", " ").split())


def first_n(items, n=3):
    return items[:n]


# ===============================
# CONCERTS — concert.ua
# ===============================
def load_concerts(limit=3):
    base = "https://concert.ua"
    url = f"{base}/uk/kyiv?sort=soon"
    html = fetch_html(url)

    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    cards = soup.select("[data-qa='event-card']") or soup.select(".event-card")

    events = []
    for card in cards:
        title = card.select_one("[data-qa='title'], .title")
        date = card.select_one("[data-qa='date'], .date")
        place = card.select_one("[data-qa='place'], .place")

        t = clean(title.get_text()) if title else ""
        d = clean(date.get_text()) if date else ""
        p = clean(place.get_text()) if place else ""

        if t:
            events.append((t, d, p))

        if len(events) >= limit:
            break

    return first_n(events, limit)


# ===============================
# THEATRE — karabas.com
# ===============================
def load_theatre(limit=3):
    url = "https://karabas.com/ua/theatre/kyiv"
    html = fetch_html(url)

    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    cards = soup.select(".poster-card, .event-card, .event, .event-item")

    events = []
    for card in cards:
        title = card.select_one(".poster-card__title, .event-card__title, h3, a")
        info = card.select_one(".poster-card__info, .event-card__info, .date, .place")

        t = clean(title.get_text()) if title else ""
        meta = clean(info.get_text()) if info else ""

        d = ""
        p = meta

        # Витягуємо дату, якщо є
        import re
        m = re.search(r"\d{1,2}[./]\d{1,2}(?:[./]\d{2,4})?", meta)
        if m:
            d = m.group(0)
            p = meta.replace(d, "").strip(" ,.-")

        if t:
            events.append((t, d, p))

        if len(events) >= limit:
            break

    return first_n(events, limit)


# ===============================
# CINEMA — planetakino.ua
# ===============================
def load_cinema(limit=3):
    url = "https://planetakino.ua/ua/afisha/kyiv/"
    html = fetch_html(url)

    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    cards = soup.select(".movie-item, .film-item, .b-movie, .movie")

    events = []
    for card in cards:
        title = card.select_one(".movie-item__title, .film-title, h3, a")
        meta = card.select_one(".movie-item__meta, .b-movie__meta, .genre")

        t = clean(title.get_text()) if title else ""
        m = clean(meta.get_text()) if meta else ""

        if t:
            events.append((t, "", m))

        if len(events) >= limit:
            break

    return first_n(events, limit)


# ===============================
# FORMATTER
# ===============================
def format_afisha(category: str):
    category = category.lower()

    if category == "concerts":
        events = load_concerts()
        header = "🎵 *Концерти у Києві:*"
    elif category == "theatre":
        events = load_theatre()
        header = "🎭 *Театр у Києві:*"
    elif category == "cinema":
        events = load_cinema()
        header = "🎬 *Кіноафіша (Київ):*"
    else:
        return "❌ Невідома категорія афіші."

    if not events:
        return header + "\n\nНаразі немає подій або сайт тимчасово недоступний."

    text = header + "\n\n"
    for (title, date, place) in events:
        info = " — ".join(x for x in [date, place] if x)
        text += f"• {title}"
        if info:
            text += f" ({info})"
        text += "\n"

    return text.strip()


# ===============================
# CALLBACK HANDLER
# ===============================
async def handle_afisha_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data  # "afisha_concerts" / "afisha_theatre" / "afisha_cinema"

    if data == "afisha_concerts":
        text = format_afisha("concerts")
    elif data == "afisha_theatre":
        text = format_afisha("theatre")
    elif data == "afisha_cinema":
        text = format_afisha("cinema")
    else:
        text = "❌ Невідома команда афіші."

    await query.edit_message_text(
        text=text,
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=back_button()
    )
