"""Inline currency conversion: @bot 100 usd uzs (works in any chat)."""
from uuid import uuid4

from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from auth import is_owner
from services import currency
from utils import fmt_num


def _article(title, description, message, html=False):
    return InlineQueryResultArticle(
        id=str(uuid4()),
        title=title,
        description=description,
        input_message_content=InputTextMessageContent(
            message, parse_mode=ParseMode.HTML if html else None
        ),
    )


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Private bot: only the owner gets inline results; everyone else sees nothing.
    if not is_owner(update.inline_query.from_user):
        await update.inline_query.answer([], cache_time=300)
        return

    q = (update.inline_query.query or "").strip()

    if not q:
        results = [
            _article(
                "💱 Valyuta konvertatsiyasi",
                "Masalan: 100 usd uzs",
                "Format: <miqdor> <valyuta> <valyuta>\nMasalan: 100 usd uzs",
            )
        ]
        await update.inline_query.answer(results, cache_time=0)
        return

    parsed = currency.parse_query(q)
    if not parsed:
        results = [
            _article(
                "❓ Noto'g'ri format",
                "Masalan: 100 usd uzs yoki 50 eur usd",
                "Format: <miqdor> <valyuta> <valyuta>\nMasalan: 100 usd uzs",
            )
        ]
        await update.inline_query.answer(results, cache_time=0)
        return

    amount, src, dst = parsed
    try:
        result = await currency.convert(amount, src, dst)
    except Exception:
        result = None

    if result is None:
        results = [
            _article(
                "⚠️ Konvertatsiya imkonsiz",
                f"{src} yoki {dst} valyutasi topilmadi",
                f"⚠️ {src} → {dst} konvertatsiyasi imkonsiz.",
            )
        ]
        await update.inline_query.answer(results, cache_time=0)
        return

    amt_str = fmt_num(amount, 2)
    res_str = fmt_num(result, 2)
    text = (
        f"💱 <b>{amt_str} {src} = {res_str} {dst}</b>\n"
        f"<i>Manba: exchangerate-api.com</i>"
    )
    results = [
        _article(
            f"{amt_str} {src} = {res_str} {dst}",
            "Bosing va natijani yuboring",
            text,
            html=True,
        )
    ]
    await update.inline_query.answer(results, cache_time=0)
