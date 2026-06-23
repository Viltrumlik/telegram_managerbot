"""Crypto prices via CoinGecko (free Demo API)."""
import httpx

import config
from utils import fmt_price, pct

COINGECKO = "https://api.coingecko.com/api/v3/simple/price"


async def get_prices(demo_key=None):
    ids = ",".join(config.COINS.values())
    params = {"ids": ids, "vs_currencies": "usd", "include_24hr_change": "true"}
    headers = {"x-cg-demo-api-key": demo_key} if demo_key else {}
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(COINGECKO, params=params, headers=headers)
        r.raise_for_status()
        data = r.json()
    out = {}
    for ticker, cgid in config.COINS.items():
        row = data.get(cgid)
        if row:
            out[ticker] = {"price": row.get("usd"), "change": row.get("usd_24h_change")}
    return out


def _line(ticker, d):
    return f"{ticker}: <b>${fmt_price(d['price'])}</b>{pct(d.get('change'))}"


def format_crypto(prices):
    lines = ["💰 <b>Kripto narxlari</b> <i>(24 soat)</i>\n"]
    for t in config.TOP_COINS:
        if t in prices:
            lines.append(_line(t, prices[t]))
    meme = [t for t in config.MEME_COINS if t in prices]
    if meme:
        lines.append("\n🐶 <b>Meme coinlar</b>")
        for t in meme:
            lines.append(_line(t, prices[t]))
    return "\n".join(lines)


if __name__ == "__main__":
    import asyncio
    import os

    print(format_crypto(asyncio.run(get_prices(os.getenv("COINGECKO_DEMO_KEY") or None))))
