from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from config import Config
from database import Database
from keyboards.inline_keyboards import get_admin_payment_buttons, get_status_refresh_buttons
from utils.decorators import admin_only
from utils.helpers import validate_url, validate_image_file
from utils.user_backup import UserBackup

db = Database()

# Conversation states
START_MSG, START_IMAGE, BUTTON_NAME, BUTTON_URL, BUTTON_ID, EDIT_BUTTON_ID, EDIT_BUTTON_NAME, EDIT_BUTTON_URL = range(8)
PLAN_NAME, PLAN_PRICE, PLAN_DESC, PLAN_DURATION, PLAN_ORDER = range(8, 13)
UPI_ID, RECEIVER_NAME, UPI_NAME, BANK_NAME = range(13, 17)
BROADCAST_CONTENT, BROADCAST_BUTTON_NAME, BROADCAST_BUTTON_URL = range(17, 20)

# Start message management
@admin_only
async def set_start_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start conversation to set start message"""
    await update.message.reply_text("Please send the new start message.\n\nYou can use:\n• Text\n• Emojis\n• HTML/Markdown formatting\n• Placeholders: {first_name}, {last_name}, {username}, {user_id}")
    return START_MSG

@admin_only
async def receive_start_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and save start message"""
    message = update.message.text
    db.set_start_message(message)
    await update.message.reply_text("✅ Start message saved successfully!")
    return ConversationHandler.END

@admin_only
async def view_start_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View current start message"""
    message = db.get_start_message()
    await update.message.reply_text(f"📝 *Current Start Message:*\n\n{message}", parse_mode=ParseMode.HTML)

@admin_only
async def reset_start_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset to default start message"""
    db.reset_start_message()
    await update.message.reply_text("✅ Start message reset to default!")

# Start image management
@admin_only
async def set_start_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start conversation to set start image"""
    await update.message.reply_text("Please send the image to use as start image.\n\nSupported formats: JPG, PNG")
    return START_IMAGE

@admin_only
async def receive_start_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and save start image"""
    if update.message.photo:
        photo = update.message.photo[-1]  # Get highest quality
        file_id = photo.file_id
        db.set_start_image(file_id)
        await update.message.reply_text("✅ Start image saved successfully!")
    else:
        await update.message.reply_text("❌ Please send a valid photo.")
    return ConversationHandler.END

@admin_only
async def view_start_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Preview current start image"""
    image = db.get_start_image()
    if image:
        await update.message.reply_photo(photo=image, caption="📸 Current start image")
    else:
        await update.message.reply_text("No start image configured.")

@admin_only
async def remove_start_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove current start image"""
    db.remove_start_image()
    await update.message.reply_text("✅ Start image removed!")

@admin_only
async def reset_start_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset to default start image"""
    db.set_start_image(Config.DEFAULT_START_IMAGE)
    await update.message.reply_text("✅ Start image reset to default!")

# Button management
@admin_only
async def add_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start conversation to add button"""
    await update.message.reply_text("Please send the button name:")
    return BUTTON_NAME

@admin_only
async def receive_button_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive button name"""
    context.user_data['button_name'] = update.message.text
    await update.message.reply_text("Please send the button URL:")
    return BUTTON_URL

@admin_only
async def receive_button_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive button URL and save button"""
    button_url = update.message.text
    if not validate_url(button_url):
        await update.message.reply_text("❌ Invalid URL. Please send a valid URL starting with http://, https://, or t.me/")
        return BUTTON_URL
    
    button_name = context.user_data['button_name']
    button_id = f"btn_{db.get_button_count() + 1}"
    position = db.get_button_count() + 1
    
    db.add_button(button_id, button_name, button_url, position)
    await update.message.reply_text(f"✅ Button '{button_name}' added successfully!")
    return ConversationHandler.END

@admin_only
async def remove_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show buttons for removal"""
    buttons = db.get_buttons()
    if not buttons:
        await update.message.reply_text("No buttons configured.")
        return ConversationHandler.END
    
    button_list = "Select button to remove:\n\n"
    for btn in buttons:
        button_list += f"ID: {btn[1]} - {btn[2]}\n"
    
    await update.message.reply_text(button_list)
    await update.message.reply_text("Send the button ID to remove:")
    return BUTTON_ID

@admin_only
async def confirm_remove_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove selected button"""
    button_id = update.message.text
    button = db.get_button(button_id)
    
    if button:
        db.delete_button(button_id)
        await update.message.reply_text(f"✅ Button '{button[2]}' removed successfully!")
    else:
        await update.message.reply_text("❌ Button not found.")
    
    return ConversationHandler.END

@admin_only
async def edit_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show buttons for editing"""
    buttons = db.get_buttons()
    if not buttons:
        await update.message.reply_text("No buttons configured.")
        return ConversationHandler.END
    
    button_list = "Select button to edit:\n\n"
    for btn in buttons:
        button_list += f"ID: {btn[1]} - {btn[2]}\n"
    
    await update.message.reply_text(button_list)
    await update.message.reply_text("Send the button ID to edit:")
    return EDIT_BUTTON_ID

@admin_only
async def select_edit_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Select button to edit"""
    button_id = update.message.text
    button = db.get_button(button_id)
    
    if button:
        context.user_data['edit_button_id'] = button_id
        await update.message.reply_text(f"Editing button: {button[2]}\n\nSend new button name (or send 'skip' to keep current):")
        return EDIT_BUTTON_NAME
    else:
        await update.message.reply_text("❌ Button not found.")
        return ConversationHandler.END

@admin_only
async def edit_button_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Edit button name"""
    new_name = update.message.text
    if new_name.lower() != 'skip':
        db.update_button(context.user_data['edit_button_id'], button_name=new_name)
    
    await update.message.reply_text("Send new button URL (or send 'skip' to keep current):")
    return EDIT_BUTTON_URL

@admin_only
async def edit_button_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Edit button URL"""
    new_url = update.message.text
    if new_url.lower() != 'skip':
        if validate_url(new_url):
            db.update_button(context.user_data['edit_button_id'], button_url=new_url)
            await update.message.reply_text("✅ Button updated successfully!")
        else:
            await update.message.reply_text("❌ Invalid URL. Button not updated.")
    
    return ConversationHandler.END

@admin_only
async def show_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all configured buttons"""
    buttons = db.get_buttons()
    if not buttons:
        await update.message.reply_text("No buttons configured.")
        return
    
    button_list = "📋 *Configured Buttons:*\n\n"
    for btn in buttons:
        button_list += f"🆔 ID: `{btn[1]}`\n"
        button_list += f"📝 Name: {btn[2]}\n"
        button_list += f"🔗 URL: {btn[3]}\n"
        button_list += f"📌 Position: {btn[4]}\n\n"
    
    await update.message.reply_text(button_list, parse_mode=ParseMode.MARKDOWN)

# Plan management
@admin_only
async def add_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start conversation to add plan"""
    await update.message.reply_text("Send plan name:")
    return PLAN_NAME

@admin_only
async def receive_plan_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive plan name"""
    context.user_data['plan_name'] = update.message.text
    await update.message.reply_text("Send plan price (in rupees):")
    return PLAN_PRICE

@admin_only
async def receive_plan_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive plan price"""
    try:
        price = int(update.message.text)
        context.user_data['plan_price'] = price
        await update.message.reply_text("Send plan description:")
        return PLAN_DESC
    except ValueError:
        await update.message.reply_text("❌ Please send a valid number for price.")
        return PLAN_PRICE

@admin_only
async def receive_plan_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive plan description"""
    context.user_data['plan_desc'] = update.message.text
    await update.message.reply_text("Send plan duration (e.g., '30 days', 'Lifetime', or send 'skip'):")
    return PLAN_DURATION

@admin_only
async def receive_plan_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive plan duration"""
    duration = update.message.text if update.message.text.lower() != 'skip' else None
    context.user_data['plan_duration'] = duration
    await update.message.reply_text("Send sort order (number, lower numbers appear first):")
    return PLAN_ORDER

@admin_only
async def receive_plan_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive sort order and save plan"""
    try:
        sort_order = int(update.message.text)
        db.add_plan(
            context.user_data['plan_name'],
            context.user_data['plan_price'],
            context.user_data['plan_desc'],
            context.user_data['plan_duration'],
            sort_order
        )
        await update.message.reply_text("✅ Plan added successfully!")
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("❌ Please send a valid number for sort order.")
        return PLAN_ORDER

@admin_only
async def edit_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show plans for editing"""
    plans = db.get_plans()
    if not plans:
        await update.message.reply_text("No plans configured.")
        return
    
    plan_list = "Select plan to edit:\n\n"
    for plan in plans:
        plan_list += f"ID: {plan[0]} - {plan[1]} (₹{plan[2]})\n"
    
    await update.message.reply_text(plan_list)
    await update.message.reply_text("Send plan ID to edit:")
    return PLAN_ORDER + 1  # Unique state

@admin_only
async def remove_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show plans for removal"""
    plans = db.get_plans()
    if not plans:
        await update.message.reply_text("No plans configured.")
        return
    
    plan_list = "Select plan to remove:\n\n"
    for plan in plans:
        plan_list += f"ID: {plan[0]} - {plan[1]} (₹{plan[2]})\n"
    
    await update.message.reply_text(plan_list)
    await update.message.reply_text("Send plan ID to remove:")
    return PLAN_ORDER + 2

@admin_only
async def list_plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all plans"""
    plans = db.get_plans()
    if not plans:
        await update.message.reply_text("No plans configured.")
        return
    
    plan_list = "📋 *Available Plans:*\n\n"
    for plan in plans:
        plan_list += f"🆔 ID: {plan[0]}\n"
        plan_list += f"📝 Name: *{plan[1]}*\n"
        plan_list += f"💰 Price: ₹{plan[2]}\n"
        plan_list += f"📝 Description: {plan[3]}\n"
        plan_list += f"⏱️ Duration: {plan[4] if plan[4] else 'Lifetime'}\n"
        plan_list += f"📌 Order: {plan[5]}\n\n"
    
    await update.message.reply_text(plan_list, parse_mode=ParseMode.MARKDOWN)

# Payment settings
@admin_only
async def setup_upi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set UPI ID"""
    await update.message.reply_text("Send UPI ID (e.g., example@upi):")
    return UPI_ID

@admin_only
async def receive_upi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive UPI ID"""
    db.set_upi_id(update.message.text)
    await update.message.reply_text("✅ UPI ID saved!")
    return ConversationHandler.END

@admin_only
async def setup_upi_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set UPI name for payment URL"""
    await update.message.reply_text("Send UPI Name (e.g., xlgr):")
    return UPI_NAME

@admin_only
async def receive_upi_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive UPI name"""
    db.set_upi_name(update.message.text)
    await update.message.reply_text("✅ UPI Name saved!")
    return ConversationHandler.END

@admin_only
async def setup_receiver_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set receiver name"""
    await update.message.reply_text("Send receiver name:")
    return RECEIVER_NAME

@admin_only
async def receive_receiver_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive receiver name"""
    db.set_receiver_name(update.message.text)
    await update.message.reply_text("✅ Receiver name saved!")
    return ConversationHandler.END

@admin_only
async def set_bank_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set bank name for payment URL"""
    await update.message.reply_text("Send bank name (e.g., ptyes):")
    return BANK_NAME

@admin_only
async def receive_bank_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive bank name"""
    db.set_bank_name(update.message.text)
    await update.message.reply_text("✅ Bank name saved!")
    return ConversationHandler.END

@admin_only
async def set_payment_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set custom payment URL"""
    await update.message.reply_text("Send payment URL template (use {amount} for amount placeholder):")
    return BANK_NAME + 1

@admin_only
async def receive_payment_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive payment URL"""
    db.set_payment_url(update.message.text)
    await update.message.reply_text("✅ Payment URL saved!")
    return ConversationHandler.END

# Channel settings
@admin_only
async def set_premium_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set premium channel ID"""
    await update.message.reply_text("Send premium channel ID (e.g., @channel or -100123456789):")
    return

@admin_only
async def set_demo_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set demo channel URL"""
    await update.message.reply_text("Send demo channel URL:")
    return

# Admin status and stats
@admin_only
async def admin_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot status for admin"""
    user_count = db.get_user_count()
    premium_count = len(db.get_premium_users())
    pending_count = db.get_pending_count()
    
    # Check configurations
    payment_settings = db.get_payment_settings()
    channel_settings = db.get_channel_settings()
    
    status_text = f"""🤖 *Bot Status*

Bot: Online ✅

📊 *Statistics:*
Users: {user_count}
Premium Users: {premium_count}
Pending Payments: {pending_count}

⚙️ *Configuration:*
Demo Channel: {'✅ Configured' if channel_settings[1] else '❌ Not Configured'}
Premium Channel: {'✅ Configured' if channel_settings[0] else '❌ Not Configured'}
UPI: {'✅ Configured' if payment_settings[0] else '❌ Not Configureed'}
Payment URL: {'✅ Configured' if payment_settings[4] else '⚠️ Using Default'}

🔧 *Database:* Connected ✅
"""
    
    buttons = get_status_refresh_buttons()
    await update.message.reply_text(status_text, parse_mode=ParseMode.MARKDOWN, reply_markup=buttons)

@admin_only
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show advanced statistics"""
    user_count = db.get_user_count()
    today_users = db.get_today_users_count()
    week_users = db.get_week_users_count()
    premium_count = len(db.get_premium_users())
    approved = db.get_approved_payments_count()
    rejected = db.get_rejected_payments_count()
    pending = db.get_pending_count()
    discounts = db.get_discounts_count()
    plans_count = len(db.get_plans())
    
    stats_text = f"""📈 *Advanced Statistics*

👥 *Users:*
Total Users: {user_count}
Today's New: {today_users}
Weekly New: {week_users}
Premium Users: {premium_count}

💰 *Payments:*
Approved: {approved}
Rejected: {rejected}
Pending: {pending}

🎁 *Discounts Generated:* {discounts}
📋 *Active Plans:* {plans_count}
"""
    
    await update.message.reply_text(stats_text, parse_mode=ParseMode.MARKDOWN)

# User backup commands
@admin_only
async def backup_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send users.txt file"""
    import os
    from config import Config
    
    if os.path.exists(Config.USERS_TXT_FILE):
        with open(Config.USERS_TXT_FILE, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename="users.txt",
                caption="📋 User backup file"
            )
    else:
        await update.message.reply_text("No backup file found.")

@admin_only
async def import_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Import users from uploaded file"""
    await update.message.reply_text("Please upload the users.txt file to import users.")
    return

@admin_only
async def rebuild_database(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Rebuild database from users.txt"""
    imported = UserBackup.rebuild_database_from_txt(db)
    await update.message.reply_text(f"✅ Database rebuilt!\nImported: {imported} users")

# Payment review
@admin_only
async def review_payments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show pending payments for review"""
    pending = db.get_pending_payments()
    
    if not pending:
        await update.message.reply_text("No pending payments to review.")
        return
    
    for payment in pending:
        payment_id, user_id, plan_name, original_price, discount_percent, final_amount, utr, screenshot, user_msg, status, created_at = payment
        
        user = db.get_user(user_id)
        user_name = f"@{user[1]}" if user and user[1] else f"ID: {user_id}"
        
        text = f"""📋 *Payment Review*

User: {user_name}
User ID: `{user_id}`

Plan: {plan_name}
Original Price: ₹{original_price}
Discount: {discount_percent}%
Final Amount: ₹{final_amount}

UTR: `{utr}`
User Message: {user_msg}

Status: ⏳ Pending
Submitted: {created_at}
"""
        
        buttons = get_admin_payment_buttons(payment_id)
        
        if screenshot:
            await update.message.reply_photo(photo=screenshot, caption=text, reply_markup=buttons, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text(text, reply_markup=buttons, parse_mode=ParseMode.MARKDOWN)

# Admin help
@admin_only
async def admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin commands"""
    help_text = """🔧 *Admin Commands*

*Start Message:*
??setstart - Set custom start message
??viewstart - View current start message
??resetstart - Reset to default

*Start Image:*
??setstartimage - Set start image
??viewstartimage - View current image
??removestartimage - Remove image
??resetstartimage - Reset to default

*Buttons:*
??addbutton - Add new button
??removebutton - Remove button
??editbutton - Edit button
??buttons - List all buttons

*Plans:*
??addplan - Add premium plan
??editplan - Edit plan
??removeplan - Remove plan
??plans - List all plans

*Payment Settings:*
??setupi - Set UPI ID
??setupiname - Set UPI name
??setreceiver - Set receiver name
??setbankname - Set bank name
??setpaymenturl - Set payment URL

*Channels:*
??setpremiumchannel - Set premium channel
??setdemochannel - Set demo channel

*Broadcast:*
??broadcast - Send broadcast message

*Users:*
??backupusers - Get users.txt backup
??importusers - Import users from file
??rebuilddb - Rebuild database from backup

*Status:*
??status - Bot status
??stats - Advanced statistics
??payments - Review pending payments

*System:*
??help - Show this help
"""
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
