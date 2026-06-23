"""Prayer times via Aladhan API (no key). method=14 + school=1 for Uzbekistan."""
from datetime import datetime

import httpx

import config

URL = "https://api.aladhan.com/v1/timings/{date}"


async def get_prayer_times(d=None):
    d = d or datetime.now(config.TZ).date()
    date_str = d.strftime("%d-%m-%Y")
    params = {
        "latitude": config.LAT,
        "longitude": config.LON,
        "method": config.ALADHAN_METHOD,
        "school": config.ALADHAN_SCHOOL,
        "timezonestring": config.TIMEZONE,
    }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(URL.format(date=date_str), params=params)
        r.raise_for_status()
        data = r.json()
    if data.get("code") != 200:
        return None
    timings = data["data"]["timings"]
    out = {}
    for p in config.PRAYERS:
        raw = timings.get(p, "")
        out[p] = raw.split(" ")[0].strip()  # strip any " (+05)" suffix
    return out


def format_times(times):
    lines = [f"🕌 <b>Namoz vaqtlari — {config.CITY_NAME}</b>\n"]
    for p in config.PRAYERS:
        lines.append(f"{config.PRAYER_NAMES_UZ[p]}: <b>{times[p]}</b>")
    return "\n".join(lines)


if __name__ == "__main__":
    import asyncio

    print(format_times(asyncio.run(get_prayer_times())))
