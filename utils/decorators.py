from functools import wraps
from config import Config

def admin_only(func):
    """Decorator to restrict commands to admins only"""
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in Config.ADMIN_IDS:
            await update.message.reply_text("❌ Access Denied")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def check_private_chat(func):
    """Decorator to ensure command is used in private chat"""
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        if update.effective_chat.type != 'private':
            await update.message.reply_text("This command is only available in private chat.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper
