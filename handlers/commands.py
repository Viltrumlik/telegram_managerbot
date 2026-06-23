"""Command handlers: /start /help /obhavo /kurs /yangilik /namoz /kripto."""
import logging

from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import ContextTypes

import messages
import storage
from auth import owner_only
from services import news as news_svc

START_TEXT = (
    "👋 <b>Salom! Men sizning shaxsiy menejeringizman.</b>\n\n"
    "Men avtomatik ravishda quyidagilarni yuborib turaman:\n"
    "☀️ Har kuni 07:00 — ob-havo va valyuta kurslari\n"
    "📰 Har kuni 08:00 — dunyo yangiliklari (rasm bilan)\n"
    "🕌 Har namozdan 10 daqiqa oldin — eslatma\n"
    "💰 Har 6 soatda — kripto va aksiya narxlari\n\n"
    "<b>Buyruqlar:</b>\n"
    "/obhavo — hozirgi ob-havo\n"
    "/kurs — valyuta kurslari\n"
    "/yangilik — so'nggi yangilik\n"
    "/namoz — bugungi namoz vaqtlari\n"
    "/kripto — kripto va aksiyalar\n"
    "/help — yordam\n\n"
    "💱 <b>Boshqa chatlarda konvertatsiya:</b>\n"
    "<code>@bot_username 100 usd uzs</code> deb yozing."
)

HELP_TEXT = (
    "ℹ️ <b>Yordam</b>\n\n"
    "/obhavo — ob-havo (Farg'ona)\n"
    "/kurs — CBU rasmiy valyuta kurslari\n"
    "/yangilik — so'nggi yangiliklar\n"
    "/namoz — namoz vaqtlari\n"
    "/kripto — kripto va aksiya narxlari\n\n"
    "💱 Inline konvertatsiya (istalgan chatda):\n"
    "<code>@bot_username 100 usd uzs</code>\n"
    "<code>@bot_username 50 eur usd</code>\n\n"
    "<i>Valyuta manbalari: CBU (cbu.uz) va exchangerate-api.com.\n"
    "Kurslar ma'lumot uchun, bank/dokon kursidan farq qilishi mumkin.</i>"
)


async def _typing(update):
    try:
        await update.effective_chat.send_action(ChatAction.TYPING)
    except Exception:
        pass


@owner_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    storage.add_subscriber(update.effective_chat.id)
    logging.getLogger("managerbot").info(
        "Owner registered: @%s (id %s)",
        update.effective_user.username, update.effective_user.id,
    )
    await update.message.reply_text(
        START_TEXT, parse_mode=ParseMode.HTML, disable_web_page_preview=True
    )


@owner_only
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        HELP_TEXT, parse_mode=ParseMode.HTML, disable_web_page_preview=True
    )


@owner_only
async def obhavo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _typing(update)
    await update.message.reply_text(
        await messages.weather_text(), parse_mode=ParseMode.HTML
    )


@owner_only
async def kurs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _typing(update)
    await update.message.reply_text(
        await messages.currency_text(), parse_mode=ParseMode.HTML
    )


@owner_only
async def namoz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _typing(update)
    await update.message.reply_text(
        await messages.prayer_text(), parse_mode=ParseMode.HTML
    )


@owner_only
async def kripto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _typing(update)
    await update.message.reply_text(
        await messages.crypto_stocks_text(), parse_mode=ParseMode.HTML
    )


@owner_only
async def yangilik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _typing(update)
    stories = await messages.news_stories()
    if not stories:
        await update.message.reply_text("⚠️ Yangiliklarni olishda xatolik.")
        return
    for s in stories:
        caption = news_svc.format_caption(s)
        try:
            if s.get("image"):
                await update.message.reply_photo(
                    photo=s["image"], caption=caption, parse_mode=ParseMode.HTML
                )
            else:
                await update.message.reply_text(caption, parse_mode=ParseMode.HTML)
        except Exception:
            await update.message.reply_text(caption, parse_mode=ParseMode.HTML)
