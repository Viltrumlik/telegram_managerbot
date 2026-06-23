"""Static configuration (no secrets). Secrets live in .env."""
from datetime import time as dtime
from zoneinfo import ZoneInfo

# --- Access control: bot is private to a single owner ---
OWNER_USERNAME = "viltrumlik"  # Telegram username (without @), case-insensitive
OWNER_ID = None                # optional numeric user id (auto-logged on first /start)

# --- Location: Fergana (Farg'ona), Uzbekistan ---
CITY_NAME = "Farg'ona"
LAT = 40.3864
LON = 71.7864
TIMEZONE = "Asia/Tashkent"  # UTC+5, no DST
TZ = ZoneInfo(TIMEZONE)

# --- Schedule (local times, interpreted in TIMEZONE via Defaults) ---
WEATHER_TIME = dtime(7, 0)          # daily weather + currency digest
NEWS_TIME = dtime(8, 0)             # daily news cards
PRAYER_REFRESH_TIME = dtime(0, 5)   # daily: fetch today's prayer times & arm reminders
PRAYER_REMINDER_LEAD_MIN = 10       # remind this many minutes before each prayer
CRYPTO_INTERVAL_HOURS = 6           # crypto + stocks push interval

# --- Currency ---
DIGEST_CURRENCIES = ["USD", "EUR", "RUB"]  # CBU official rates -> UZS
DEFAULT_INLINE_TARGET = "UZS"              # default target for inline "100 usd"

# --- Prayer (Aladhan) ---
ALADHAN_METHOD = 14   # Spiritual Administration of Muslims of Russia (CIS standard)
ALADHAN_SCHOOL = 1    # 1 = Hanafi (correct for Uzbekistan; affects Asr time)
PRAYERS = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
PRAYER_NAMES_UZ = {
    "Fajr": "Bomdod",
    "Dhuhr": "Peshin",
    "Asr": "Asr",
    "Maghrib": "Shom",
    "Isha": "Xufton",
}

# --- News feeds (image + caption). One top story is posted per feed. ---
NEWS_FEEDS = [
    {"lang": "uz", "name": "Kun.uz", "url": "https://kun.uz/news/rss"},
    {"lang": "en", "name": "BBC World", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
]

# --- Crypto (ticker -> CoinGecko id). Edit freely. ---
TOP_COINS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "BNB": "binancecoin",
    "SOL": "solana",
    "XRP": "ripple",
    "ADA": "cardano",
    "TON": "the-open-network",
    "TRX": "tron",
    "AVAX": "avalanche-2",
    "DOT": "polkadot",
}
MEME_COINS = {
    "DOGE": "dogecoin",
    "SHIB": "shiba-inu",
    "PEPE": "pepe",
    "WIF": "dogwifcoin",
    "BONK": "bonk",
    "FLOKI": "floki",
}
COINS = {**TOP_COINS, **MEME_COINS}  # combined ticker -> id map

# --- Stocks (US tickers). Edit freely. ---
STOCKS = ["TSLA", "NVDA", "AAPL", "MSFT", "AMZN", "GOOGL"]
