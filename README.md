# ManagerBot

A private "personal manager" Telegram bot. Every day it sends its owner the
weather and official exchange rates, top news stories with images, reminders
before each of the five daily prayers, and crypto and stock prices every few
hours. It also answers a few commands on demand and converts currencies inline
in any chat (`@your_bot 100 usd uzs`). The bot only responds to a single owner,
and its interface is in Uzbek. Built with python-telegram-bot and free public APIs.

## Features

| Feature | When | Source |
|---|---|---|
| Weather (Fergana by default) | daily at 07:00 | [Open-Meteo](https://open-meteo.com/) |
| Official exchange rates to UZS (USD, EUR, RUB) | daily at 07:00 | [Central Bank of Uzbekistan](https://cbu.uz/) |
| Top news story with image (Kun.uz, BBC World) | daily at 08:00, only if the story is new | RSS feeds |
| Prayer reminders (Bomdod, Peshin, Asr, Shom, Xufton) | 10 minutes before each prayer | [Aladhan](https://aladhan.com/prayer-times-api) |
| Crypto (top coins and meme coins) and US stocks | every 6 hours | [CoinGecko](https://www.coingecko.com/), [Finnhub](https://finnhub.io/) or Yahoo Finance |
| Inline currency conversion | any chat: `@your_bot 100 usd uzs` | [ExchangeRate-API](https://open.er-api.com/) |

- Owner-only access: commands and inline queries from anyone else are refused.
- Scheduled messages go to every chat where the owner has sent `/start`
  (stored in `subscribers.json`).
- All times are local to `Asia/Tashkent`.

## Bot commands

| Command | Description |
|---|---|
| `/start` | Subscribe this chat to scheduled messages and show the intro |
| `/help` | Show help |
| `/obhavo` | Current weather |
| `/kurs` | Official CBU exchange rates |
| `/yangilik` (`/yangiliklar`) | Latest news stories |
| `/namoz` | Today's prayer times |
| `/kripto` | Crypto and stock prices |

Inline mode: type `@your_bot <amount> <from> [to]` in any chat, e.g.
`@your_bot 100 usd uzs` or `@your_bot 50 eur usd`. The target currency defaults
to UZS.

## Tech stack

- Python 3.9+ (uses `zoneinfo`)
- [python-telegram-bot](https://python-telegram-bot.org/) 22+ with JobQueue (long polling)
- httpx, feedparser, BeautifulSoup 4, python-dotenv
- JSON file storage (`subscribers.json`) for subscribers and last-posted news

## Getting started

### Prerequisites

- Python 3 with `venv`
- A bot token from [@BotFather](https://t.me/BotFather) (`/newbot`)
- Inline mode enabled for the bot: @BotFather → `/setinline` → choose the bot →
  set a placeholder such as `100 usd uzs`. Without this, inline queries never arrive.

### Install

```bash
git clone https://github.com/Viltrumlik/telegram_managerbot.git
cd telegram_managerbot
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

### Configure

Secrets live in `.env` (gitignored):

```bash
cp .env.example .env
```

| Variable | Required | Description |
|---|---|---|
| `BOT_TOKEN` | yes | Token from @BotFather |
| `COINGECKO_DEMO_KEY` | no | Free CoinGecko Demo key, improves reliability |
| `FINNHUB_KEY` | no | Free Finnhub key; without it stocks come from keyless Yahoo Finance |

Everything else is in [`config.py`](config.py):

- `OWNER_USERNAME` / `OWNER_ID` — **set these to your own Telegram account**;
  only this user can use the bot
- `CITY_NAME`, `LAT`, `LON`, `TIMEZONE` — location for weather and prayer times
- `WEATHER_TIME`, `NEWS_TIME`, `PRAYER_REMINDER_LEAD_MIN`, `CRYPTO_INTERVAL_HOURS` — schedule
- `DIGEST_CURRENCIES`, `DEFAULT_INLINE_TARGET` — currencies
- `ALADHAN_METHOD`, `ALADHAN_SCHOOL` — prayer time calculation (defaults: method 14, Hanafi)
- `NEWS_FEEDS`, `TOP_COINS`, `MEME_COINS`, `STOCKS` — content lists

### Run

```bash
venv/bin/python bot.py
```

Then open the bot in Telegram and send `/start` to subscribe your chat.

Each data source can be checked on its own:

```bash
venv/bin/python -m services.weather
venv/bin/python -m services.currency
venv/bin/python -m services.news
venv/bin/python -m services.prayer
venv/bin/python -m services.crypto
venv/bin/python -m services.stocks
```

### Deploy

The bot runs 24/7 under systemd on a VPS. See [deploy/DEPLOY.md](deploy/DEPLOY.md)
for the step-by-step guide and [deploy/managerbot.service](deploy/managerbot.service)
for the unit file — adjust `User`, `WorkingDirectory` and `ExecStart` to the
paths on your server.

## Project structure

```
bot.py              entry point: handlers, JobQueue, long polling
config.py           static settings (owner, location, schedule, coins, stocks)
auth.py             owner-only access check
jobs.py             scheduled jobs and prayer reminder scheduling
messages.py         builds the messages shared by commands and jobs
storage.py          JSON store for subscribers and last-seen news
utils.py            formatting helpers
handlers/
  commands.py       /start /help /obhavo /kurs /yangilik /namoz /kripto
  inline.py         inline currency conversion
services/
  weather.py        Open-Meteo
  currency.py       CBU rates and ExchangeRate-API conversion
  news.py           RSS parsing and image extraction
  prayer.py         Aladhan prayer times
  crypto.py         CoinGecko
  stocks.py         Finnhub / Yahoo Finance
deploy/
  DEPLOY.md         VPS deployment guide
  managerbot.service systemd unit
```

## License

Released under the [MIT License](LICENSE).
