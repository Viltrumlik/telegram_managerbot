"""Access control — this bot is private to a single owner."""
import functools

import config


def is_owner(user):
    """True only for the configured owner (by numeric id or username)."""
    if user is None:
        return False
    if config.OWNER_ID is not None and user.id == config.OWNER_ID:
        return True
    if config.OWNER_USERNAME and user.username:
        return user.username.lower() == config.OWNER_USERNAME.lower().lstrip("@")
    return False


def owner_only(handler):
    """Decorator: reject command updates from anyone but the owner."""
    @functools.wraps(handler)
    async def wrapper(update, context):
        if not is_owner(update.effective_user):
            if update.message:
                await update.message.reply_text("⛔ Bu shaxsiy bot.")
            return
        return await handler(update, context)

    return wrapper
