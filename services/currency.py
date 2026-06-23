"""Currency: CBU official UZS rates + open.er-api.com for inline conversion."""
import re
import time as _time

import httpx

import config
from utils import fmt_num

CBU_URL = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/{code}/"
ERAPI_URL = "https://open.er-api.com/v6/latest/{base}"

# In-memory rate cache for inline conversion (rates refresh ~once/24h).
_rate_cache = {}  # base -> (timestamp, rates_dict)
_CACHE_TTL = 3600  # seconds

CURRENCY_ALIASES = {
    "$": "USD", "ДОЛЛАР": "USD",
    "€": "EUR",
    "СУМ": "UZS", "SUM": "UZS", "SO'M": "UZS", "SOM": "UZS", "СЎМ": "UZS",
    "РУБ": "RUB", "₽": "RUB",
    "£": "GBP",
    "₸": "KZT",
}


# ---------- CBU official rates ----------
async def get_cbu_rate(code):
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(CBU_URL.format(code=code))
        r.raise_for_status()
        arr = r.json()
    if not arr:
        return None
    item = arr[0]
    try:
        rate = float(item["Rate"])
        nominal = float(item.get("Nominal") or "1")
    except (KeyError, ValueError):
        return None
    return {
        "code": item.get("Ccy", code),
        "rate": rate / nominal,  # UZS per 1 unit
        "diff": item.get("Diff"),
        "date": item.get("Date"),
        "name": item.get("CcyNm_UZ") or item.get("CcyNm_EN"),
    }


async def get_official_rates(codes=None):
    codes = codes or config.DIGEST_CURRENCIES
    out = []
    for c in codes:
        try:
            res = await get_cbu_rate(c)
            if res:
                out.append(res)
        except Exception:
            continue
    return out


def format_rates(rates):
    if not rates:
        return "💱 Valyuta kurslarini olishda xatolik."
    header = "💱 <b>CBU rasmiy kurslari</b>"
    if rates[0].get("date"):
        header += f"  <i>({rates[0]['date']})</i>"
    lines = [header]
    for r in rates:
        diff = ""
        try:
            d = float(r.get("diff") or 0)
            if d > 0:
                diff = f"  🔺{fmt_num(d, 2)}"
            elif d < 0:
                diff = f"  🔻{fmt_num(abs(d), 2)}"
        except (TypeError, ValueError):
            pass
        lines.append(f"1 {r['code']} = <b>{fmt_num(r['rate'], 2)}</b> so'm{diff}")
    return "\n".join(lines)


# ---------- Inline conversion ----------
_QUERY_RE = re.compile(
    r"^\s*([\d.,\s]+?)\s*"
    r"([a-zA-Z$€£₽₸]{1,4}|сум|so'?m|сўм|руб|доллар)\s*"
    r"(?:to|in|->|=|в|ga|ни)?\s*"
    r"([a-zA-Z$€£₽₸]{1,4}|сум|so'?m|сўм|руб|доллар)?\s*$",
    re.IGNORECASE,
)


def _norm_cur(s):
    if not s:
        return None
    key = s.strip().upper().replace("`", "'").replace("’", "'")
    if key in CURRENCY_ALIASES:
        return CURRENCY_ALIASES[key]
    if len(key) == 3 and key.isalpha():
        return key
    return None


def _parse_amount(s):
    s = s.strip().replace(" ", "")
    if "," in s and "." in s:
        s = s.replace(",", "")
    elif "," in s:
        # single comma with non-3-digit tail => decimal separator
        if s.count(",") == 1 and len(s.split(",")[1]) != 3:
            s = s.replace(",", ".")
        else:
            s = s.replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def parse_query(q):
    m = _QUERY_RE.match(q.strip())
    if not m:
        return None
    amt_raw, src_raw, dst_raw = m.groups()
    amt = _parse_amount(amt_raw)
    src = _norm_cur(src_raw)
    dst = _norm_cur(dst_raw) if dst_raw else config.DEFAULT_INLINE_TARGET
    if amt is None or not src or not dst or src == dst:
        if src and dst and src == dst and amt is not None:
            return amt, src, dst  # allow same->same (returns amount)
        return None
    return amt, src, dst


async def _get_rates(base):
    now = _time.time()
    cached = _rate_cache.get(base)
    if cached and now - cached[0] < _CACHE_TTL:
        return cached[1]
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(ERAPI_URL.format(base=base))
        r.raise_for_status()
        data = r.json()
    if data.get("result") != "success":
        return None
    rates = data.get("rates", {})
    _rate_cache[base] = (now, rates)
    return rates


async def convert(amount, src, dst):
    if src == dst:
        return amount
    rates = await _get_rates(src)
    if not rates or dst not in rates:
        return None
    return amount * rates[dst]


if __name__ == "__main__":
    import asyncio

    async def _demo():
        print(format_rates(await get_official_rates()))
        for q in ["100 usd uzs", "100 usd", "50 eur usd", "1000000 uzs usd"]:
            parsed = parse_query(q)
            if parsed:
                amt, src, dst = parsed
                res = await convert(amt, src, dst)
                print(f"{q!r:22} -> {amt} {src} = {res} {dst}")
            else:
                print(f"{q!r:22} -> parse error")

    asyncio.run(_demo())
