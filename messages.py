"""Builders that combine services into the final user-facing messages.

Shared by both on-demand command handlers and scheduled jobs so the output
is identical in both paths.
"""
import os

import config
from services import crypto, currency, news, prayer, stocks, weather

COINGECKO_DEMO_KEY = os.getenv("COINGECKO_DEMO_KEY") or None
FINNHUB_KEY = os.getenv("FINNHUB_KEY") or None


async def weather_text():
    try:
        w = await weather.get_weather()
        return weather.format_weather(w)
    except Exception:
        return "⚠️ Ob-havo ma'lumotini olishda xatolik."


async def currency_text():
    try:
        rates = await currency.get_official_rates()
        return currency.format_rates(rates)
    except Exception:
        return "⚠️ Valyuta kurslarini olishda xatolik."


async def weather_currency_text():
    return f"{await weather_text()}\n\n{await currency_text()}"


async def prayer_text():
    try:
        times = await prayer.get_prayer_times()
    except Exception:
        times = None
    if not times:
        return "⚠️ Namoz vaqtlarini olishda xatolik."
    return prayer.format_times(times)


async def crypto_stocks_text():
    parts = []
    try:
        prices = await crypto.get_prices(COINGECKO_DEMO_KEY)
        if prices:
            parts.append(crypto.format_crypto(prices))
    except Exception:
        parts.append("⚠️ Kripto narxlarini olishda xatolik.")
    try:
        st = await stocks.get_stocks(FINNHUB_KEY)
        block = stocks.format_stocks(st)
        if block:
            parts.append(block)
    except Exception:
        pass
    return "\n\n".join(parts) if parts else "⚠️ Narxlarni olishda xatolik."


async def news_stories():
    out = []
    for feed in config.NEWS_FEEDS:
        try:
            s = await news.get_top_story(feed)
            if s and s.get("title"):
                out.append(s)
        except Exception:
            continue
    return out
