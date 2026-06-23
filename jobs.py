"""Scheduled jobs + JobQueue wiring."""
import logging
from datetime import datetime, timedelta

from telegram.constants import ParseMode

import config
import messages
import storage
from services import news as news_svc
from services import prayer

log = logging.getLogger(__name__)

PRAYER_JOB_PREFIX = "prayer_reminder_"


async def _broadcast(context, text):
    for chat_id in storage.get_subscribers():
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except Exception as e:
            log.warning("send_message to %s failed: %s", chat_id, e)


# ---------- Job callbacks ----------
async def job_weather_currency(context):
    await _broadcast(context, await messages.weather_currency_text())


async def job_crypto_stocks(context):
    await _broadcast(context, await messages.crypto_stocks_text())


async def job_news(context):
    stories = await messages.news_stories()
    subs = storage.get_subscribers()
    for s in stories:
        key = f"news_{s['lang']}"
        if storage.get_last_news(key) == s["guid"]:
            continue  # already posted this top story
        storage.set_last_news(key, s["guid"])
        caption = news_svc.format_caption(s)
        for chat_id in subs:
            try:
                if s.get("image"):
                    await context.bot.send_photo(
                        chat_id=chat_id, photo=s["image"],
                        caption=caption, parse_mode=ParseMode.HTML,
                    )
                else:
                    await context.bot.send_message(
                        chat_id=chat_id, text=caption, parse_mode=ParseMode.HTML,
                    )
            except Exception as e:
                log.warning("news photo to %s failed (%s); sending as text", chat_id, e)
                try:
                    await context.bot.send_message(
                        chat_id=chat_id, text=caption, parse_mode=ParseMode.HTML,
                    )
                except Exception:
                    pass


async def job_prayer_reminder(context):
    p = context.job.data
    uz = config.PRAYER_NAMES_UZ.get(p, p)
    text = (
        f"🕌 <b>{uz}</b> namoziga "
        f"{config.PRAYER_REMINDER_LEAD_MIN} daqiqa qoldi. Tayyorlaning."
    )
    await _broadcast(context, text)


async def job_refresh_prayers(context):
    await schedule_today_prayers(context.application)


# ---------- Scheduling ----------
async def schedule_today_prayers(app):
    """Fetch today's prayer times and arm one-shot reminders for the rest of the day."""
    jq = app.job_queue
    for job in jq.jobs():
        if job.name and job.name.startswith(PRAYER_JOB_PREFIX):
            job.schedule_removal()

    try:
        times = await prayer.get_prayer_times()
    except Exception as e:
        log.warning("prayer fetch failed: %s", e)
        return
    if not times:
        return

    now = datetime.now(config.TZ)
    for p, hhmm in times.items():
        try:
            hh, mm = map(int, hhmm.split(":"))
        except (ValueError, AttributeError):
            continue
        prayer_dt = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
        remind_dt = prayer_dt - timedelta(minutes=config.PRAYER_REMINDER_LEAD_MIN)
        if remind_dt > now:
            jq.run_once(
                job_prayer_reminder, when=remind_dt, data=p,
                name=f"{PRAYER_JOB_PREFIX}{p}",
            )
            log.info("armed %s reminder at %s", p, remind_dt.strftime("%H:%M"))


def schedule_jobs(app):
    jq = app.job_queue
    jq.run_daily(job_weather_currency, time=config.WEATHER_TIME, name="weather_currency")
    jq.run_daily(job_news, time=config.NEWS_TIME, name="news")
    jq.run_daily(job_refresh_prayers, time=config.PRAYER_REFRESH_TIME, name="prayer_refresh")
    jq.run_repeating(
        job_crypto_stocks,
        interval=timedelta(hours=config.CRYPTO_INTERVAL_HOURS),
        first=timedelta(seconds=15),
        name="crypto_stocks",
    )
    log.info("Scheduled jobs: weather/currency 07:00, news 08:00, prayers, crypto every %sh",
             config.CRYPTO_INTERVAL_HOURS)
