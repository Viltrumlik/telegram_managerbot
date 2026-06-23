"""Weather via Open-Meteo (no API key)."""
import httpx

import config
from utils import weather_desc

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


async def get_weather():
    params = {
        "latitude": config.LAT,
        "longitude": config.LON,
        "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,weather_code",
        "timezone": config.TIMEZONE,
        "forecast_days": 1,
    }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(FORECAST_URL, params=params)
        r.raise_for_status()
        data = r.json()
    cur = data["current"]
    daily = data["daily"]
    return {
        "temp": cur["temperature_2m"],
        "humidity": cur["relative_humidity_2m"],
        "wind": cur["wind_speed_10m"],
        "code": cur["weather_code"],
        "tmax": daily["temperature_2m_max"][0],
        "tmin": daily["temperature_2m_min"][0],
        "precip_sum": daily["precipitation_sum"][0],
        "precip_prob": daily["precipitation_probability_max"][0],
    }


def format_weather(w):
    emoji, desc = weather_desc(w["code"])
    return (
        f"{emoji} <b>{config.CITY_NAME} — ob-havo</b>\n\n"
        f"Hozir: <b>{round(w['temp'])}°C</b>, {desc}\n"
        f"Bugun: ⬆️ {round(w['tmax'])}°C / ⬇️ {round(w['tmin'])}°C\n"
        f"💧 Namlik: {w['humidity']}%   💨 Shamol: {round(w['wind'])} km/soat\n"
        f"🌧 Yog'in ehtimoli: {w['precip_prob']}% ({w['precip_sum']} mm)"
    )


if __name__ == "__main__":
    import asyncio

    print(format_weather(asyncio.run(get_weather())))
