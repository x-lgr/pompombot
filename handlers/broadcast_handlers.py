from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from database import Database
from utils.decorators import admin_only
from utils.user_backup import UserBackup

db = Database()

# Conversation states
BROADCAST_CONTENT, BROADCAST_BUTTON_NAME, BROADCAST_BUTTON_URL, BROADCAST_CONFIRM = range(4)

@admin_only
async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start broadcast conversation"""
    await update.message.reply_text(
        "📢 *Start Broadcast*\n\n"
        "Send the message you want to broadcast.\n\n"
        "Supported:\n"
        "• Text\n"
        "• Photo with caption\n"
        "• HTML/Markdown formatting",
        parse_mode=ParseMode.MARKDOWN
    )
    return BROADCAST_CONTENT

@admin_only
async def receive_broadcast_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive broadcast content"""
    if update.message.photo:
        photo = update.message.photo[-1]
        context.user_data['broadcast_type'] = 'photo'
        context.user_data['broadcast_photo'] = photo.file_id
        context.user_data['broadcast_caption'] = update.message.caption or ""
    else:
        context.user_data['broadcast_type'] = 'text'
        context.user_data['broadcast_text'] = update.message.text
    
    # Show preview
    await show_broadcast_preview(update, context)
    
    # Ask for button
    keyboard = [[
        InlineKeyboardButton("Yes", callback_data="bc_add_btn"),
        InlineKeyboardButton("No", callback_data="bc_no_btn")
    ]]
    await update.message.reply_text(
        "Add a button to this broadcast?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return BROADCAST_CONFIRM

async def show_broadcast_preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show broadcast preview"""
    await update.message.reply_text("📋 *Preview of broadcast message:*", parse_mode=ParseMode.MARKDOWN)
    
    buttons = []
    if 'broadcast_button' in context.user_data:
        btn = context.user_data['broadcast_button']
        buttons.append([InlineKeyboardButton(btn['name'], url=btn['url'])])
    
    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
    
    if context.user_data['broadcast_type'] == 'photo':
        await update.message.reply_photo(
            photo=context.user_data['broadcast_photo'],
            caption=context.user_data.get('broadcast_caption', ''),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_text(
            context.user_data['broadcast_text'],
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

async def broadcast_button_callback(update, context):
    """Handle broadcast button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "bc_add_btn":
        await query.edit_message_text("Send button name:")
        return BROADCAST_BUTTON_NAME
    elif query.data == "bc_no_btn":
        await confirm_broadcast(update, context)
        return BROADCAST_CONFIRM
    elif query.data == "bc_confirm":
        await execute_broadcast(update, context)
        return ConversationHandler.END
    elif query.data == "bc_cancel":
        await query.edit_message_text("❌ Broadcast cancelled.")
        return ConversationHandler.END

async def receive_button_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive button name for broadcast"""
    context.user_data['temp_button_name'] = update.message.text
    await update.message.reply_text("Send button URL:")
    return BROADCAST_BUTTON_URL

async def receive_button_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive button URL and update preview"""
    context.user_data['broadcast_button'] = {
        'name': context.user_data['temp_button_name'],
        'url': update.message.text
    }
    
    # Show updated preview
    await show_broadcast_preview(update, context)
    await confirm_broadcast(update, context)
    return BROADCAST_CONFIRM

async def confirm_broadcast(update, context):
    """Ask for broadcast confirmation"""
    keyboard = [[
        InlineKeyboardButton("🟢 Confirm & Send", callback_data="bc_confirm"),
        InlineKeyboardButton("🔴 Cancel", callback_data="bc_cancel")
    ]]
    await update.message.reply_text(
        "Ready to send broadcast?\n\n"
        "⚠️ This will send to ALL users!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def execute_broadcast(update, context):
    """Execute broadcast to all users"""
    users = db.get_all_users()
    total = len(users)
    sent = 0
    failed = 0
    
    status_msg = await update.message.reply_text(f"📡 Broadcasting...\n0/{total} sent")
    
    buttons = []
    if 'broadcast_button' in context.user_data:
        btn = context.user_data['broadcast_button']
        buttons.append([InlineKeyboardButton(btn['name'], url=btn['url'])])
    
    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
    
    for i, user_id in enumerate(users):
        try:
            if context.user_data['broadcast_type'] == 'photo':
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=context.user_data['broadcast_photo'],
                    caption=context.user_data.get('broadcast_caption', ''),
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML
                )
            else:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=context.user_data['broadcast_text'],
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML
                )
            sent += 1
        except Exception:
            failed += 1
        
        # Update status every 100 users
        if (i + 1) % 100 == 0:
            await status_msg.edit_text(f"📡 Broadcasting...\n{sent}/{total} sent\n❌ Failed: {failed}")
    
    await status_msg.edit_text(f"✅ Broadcast completed!\n\n📤 Sent: {sent}\n❌ Failed: {failed}\n👥 Total: {total}")
    
    # Create backup after broadcast
    UserBackup.add_user_to_txt("backup_trigger")  # This ensures backup is maintained
