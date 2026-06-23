"""ManagerBot entry point."""
import logging
import os
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    Defaults,
    InlineQueryHandler,
)

import config
from handlers import commands as cmd
from handlers.inline import inline_query
from jobs import schedule_jobs, schedule_today_prayers

load_dotenv()

logging.basicConfig(
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("managerbot")


async def _post_init(app):
    await app.bot.delete_webhook(drop_pending_updates=True)
    schedule_jobs(app)
    await schedule_today_prayers(app)
    me = await app.bot.get_me()
    log.info("Bot @%s ishga tushdi", me.username)


def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise SystemExit("BOT_TOKEN .env faylida topilmadi")

    defaults = Defaults(parse_mode=ParseMode.HTML, tzinfo=ZoneInfo(config.TIMEZONE))
    app = (
        ApplicationBuilder()
        .token(token)
        .defaults(defaults)
        .post_init(_post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", cmd.start))
    app.add_handler(CommandHandler("help", cmd.help_cmd))
    app.add_handler(CommandHandler("obhavo", cmd.obhavo))
    app.add_handler(CommandHandler("kurs", cmd.kurs))
    app.add_handler(CommandHandler(["yangilik", "yangiliklar"], cmd.yangilik))
    app.add_handler(CommandHandler("namoz", cmd.namoz))
    app.add_handler(CommandHandler("kripto", cmd.kripto))
    app.add_handler(InlineQueryHandler(inline_query))

    log.info("Polling boshlandi...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
