"""Stock prices: Finnhub (if FINNHUB_KEY) else keyless Yahoo v8 chart."""
import httpx

import config
from utils import fmt_num, pct

FINNHUB = "https://finnhub.io/api/v1/quote"
YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart/{sym}"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ManagerBot/1.0"


async def _finnhub(client, sym, key):
    r = await client.get(FINNHUB, params={"symbol": sym, "token": key})
    r.raise_for_status()
    d = r.json()
    return {"price": d.get("c"), "change": d.get("dp")}


async def _yahoo(client, sym):
    r = await client.get(YAHOO.format(sym=sym))
    r.raise_for_status()
    meta = r.json()["chart"]["result"][0]["meta"]
    price = meta.get("regularMarketPrice")
    prev = meta.get("previousClose") or meta.get("chartPreviousClose")
    change = ((price - prev) / prev * 100) if (price and prev) else None
    return {"price": price, "change": change}


async def get_stocks(finnhub_key=None):
    out = {}
    async with httpx.AsyncClient(timeout=20, headers={"User-Agent": UA}) as client:
        for sym in config.STOCKS:
            try:
                if finnhub_key:
                    out[sym] = await _finnhub(client, sym, finnhub_key)
                else:
                    out[sym] = await _yahoo(client, sym)
            except Exception:
                continue
    return out


def format_stocks(stocks):
    rows = [s for s in config.STOCKS if s in stocks and stocks[s].get("price") is not None]
    if not rows:
        return ""
    lines = ["📈 <b>Aksiyalar</b>"]
    for sym in rows:
        d = stocks[sym]
        lines.append(f"{sym}: <b>${fmt_num(d['price'], 2)}</b>{pct(d.get('change'))}")
    return "\n".join(lines)


if __name__ == "__main__":
    import asyncio
    import os

    print(format_stocks(asyncio.run(get_stocks(os.getenv("FINNHUB_KEY") or None))))
