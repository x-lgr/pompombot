from telegram import Update
from telegram.ext import ContextTypes, CallbackContext
from telegram.constants import ParseMode
from config import Config
from database import Database
from keyboards.inline_keyboards import get_start_buttons, get_plan_buttons, get_help_buttons, get_premium_panel_buttons
from utils.user_backup import UserBackup
from utils.helpers import format_start_message, generate_payment_url
import random

db = Database()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    # Add user to database and backup
    db.add_user(user.id, user.username, user.first_name, user.last_name)
    UserBackup.add_user_to_txt(user.id)
    
    # Get start settings
    start_message = db.get_start_message()
    start_image = db.get_start_image()
    formatted_message = format_start_message(start_message, user)
    
    buttons = get_start_buttons(db)
    
    if start_image:
        # Send image with caption
        await update.message.reply_photo(
            photo=start_image,
            caption=formatted_message,
            reply_markup=buttons,
            parse_mode=ParseMode.HTML
        )
    else:
        # Send text only
        await update.message.reply_text(
            formatted_message,
            reply_markup=buttons,
            parse_mode=ParseMode.HTML
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    user = update.effective_user
    help_text = f"""📚 Help Menu - {user.first_name}

Available Commands:

/start - Start the bot
/help - Show this help menu
/premium - Access premium panel
/status - Check your account status

💎 How to Buy Premium:
1. Click "Buy Premium" button
2. Select your plan
3. Complete payment
4. Submit transaction details

📝 How to Submit Payment:
1. Make payment to provided UPI
2. Click "I Have Paid"
3. Upload screenshot and UTR number
4. Wait for admin approval

For support, contact admin.
"""
    
    buttons = get_help_buttons(db)
    await update.message.reply_text(help_text, reply_markup=buttons)

async def premium_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /premium command for premium users"""
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    if user_data and user_data[6]:  # is_premium = True
        premium_text = f"""⭐ PREMIUM USER

Plan: {user_data[7]}
Purchase Date: {user_data[8]}
Status: Active

Use the buttons below to manage your premium access."""
        buttons = get_premium_panel_buttons()
        await update.message.reply_text(premium_text, reply_markup=buttons)
    else:
        await update.message.reply_text("You are not a premium user. Use /start to purchase premium membership.")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    user = update.effective_user
    user_data = db.get_user(user.id)
    
    status_text = f"""📊 Account Status

User: {user.first_name}
Username: @{user.username if user.username else 'N/A'}
User ID: {user.id}

Account Type: {'⭐ PREMIUM USER' if user_data and user_data[6] else 'FREE USER'}"""

    if user_data and user_data[6]:
        status_text += f"""
        
Premium Details:
Plan: {user_data[7]}
Purchase Date: {user_data[8]}
Status: Active"""
    
    await update.message.reply_text(status_text)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button callbacks"""
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "buy_premium":
        await show_plans(query)
    elif data == "back_to_start":
        await back_to_start(query)
    elif data.startswith("plan_"):
        plan_id = int(data.split("_")[1])
        await show_plan_detail(query, plan_id)
    elif data == "back_to_plans":
        await show_plans(query)
    elif data.startswith("plan_page_"):
        page = int(data.split("_")[2])
        await show_plans(query, page)
    elif data.startswith("pay_"):
        parts = data.split("_")
        plan_id = int(parts[1])
        amount = int(parts[2])
        await process_payment(query, plan_id, amount)
    elif data == "cancel_payment":
        await show_cancel_with_discount(query)
    elif data == "get_discount":
        await generate_discount(query)
    elif data == "submit_payment":
        context.user_data['awaiting_payment'] = True
        await query.edit_message_text("Please send your payment details:\n\n1. Screenshot of payment\n2. UTR Number\n3. Your message")
    elif data == "generate_link":
        await generate_invite_link(query, context)
    elif data == "no_demo":
        await query.edit_message_text("Demo channel not configured yet. Please contact admin.")
    elif data == "refresh_status":
        await refresh_admin_status(query)

async def show_plans(query, page=0):
    """Show available plans"""
    plans = db.get_plans()
    
    if not plans:
        await query.edit_message_text("No plans available. Please contact admin.")
        return
    
    text = "💎 *Choose Your Plan*\n\n"
    for plan in plans:
        text += f"• *{plan[1]}* - ₹{plan[2]}\n"
        if plan[3]:
            text += f"  {plan[3]}\n"
        text += "\n"
    
    buttons = get_plan_buttons(plans, page)
    await query.edit_message_text(text, reply_markup=buttons, parse_mode=ParseMode.MARKDOWN)

async def show_plan_detail(query, plan_id):
    """Show plan details"""
    plan = db.get_plan(plan_id)
    if not plan:
        await query.edit_message_text("Plan not found.")
        return
    
    text = f"""💰 *{plan[1]}*

Price: ₹{plan[2]}

📝 *Description:*
{plan[3] if plan[3] else 'No description available.'}

⏱️ *Duration:* {plan[4] if plan[4] else 'Lifetime'}

Click Buy Now to proceed with payment."""
    
    buttons = get_plan_detail_buttons(plan_id, plan[2])
    await query.edit_message_text(text, reply_markup=buttons, parse_mode=ParseMode.MARKDOWN)

async def process_payment(query, plan_id, amount):
    """Process payment page"""
    plan = db.get_plan(plan_id)
    payment_settings = db.get_payment_settings()
    
    if not payment_settings or not payment_settings[0]:
        await query.edit_message_text("❌ Payment system not configured. Please contact admin.")
        return
    
    upi_id, receiver_name, upi_name, bank_name, payment_url = payment_settings
    
    if not upi_name or not bank_name:
        await query.edit_message_text("❌ Payment system not configured properly. Please contact admin.")
        return
    
    payment_url = generate_payment_url(upi_name, bank_name, amount)
    
    text = f"""💳 *Payment Details*

UPI ID: `{upi_id}`
Receiver: {receiver_name}
Amount: ₹{amount}

🔗 *Payment Link:*
{payment_url}

*Steps to Pay:*
1. Click the payment button below
2. Complete payment
3. Click "I Have Paid"
4. Upload screenshot and UTR number

⚠️ *Important:* Send exact amount only!"""
    
    buttons = get_payment_buttons(plan_id, amount)
    await query.edit_message_text(text, reply_markup=buttons, parse_mode=ParseMode.MARKDOWN)
    
    # Store payment context
    query.message.chat_id
    context.user_data['current_plan_id'] = plan_id
    context.user_data['current_amount'] = amount

async def show_cancel_with_discount(query):
    """Show cancel message with discount option"""
    text = "Maybe the price feels a little high 😄\n\nWould you like a discount?"
    buttons = get_cancel_buttons()
    await query.edit_message_text(text, reply_markup=buttons)

async def generate_discount(query):
    """Generate random discount for user"""
    user_id = query.from_user.id
    discount_percent = random.randint(1, 25)
    
    # Get current amount from context
    amount = context.user_data.get('current_amount', 0)
    if not amount:
        await query.edit_message_text("Session expired. Please start over.")
        return
    
    discounted_amount = int(amount - (amount * discount_percent / 100))
    discount_code = f"DISC{random.randint(1000, 9999)}{chr(random.randint(65, 90))}"
    
    # Save discount to database
    db.save_discount(user_id, discount_code, discount_percent, amount, discounted_amount)
    
    text = f"""🎉 *Congratulations!*

Discount: {discount_percent}%
Code: `{discount_code}`
Original Amount: ₹{amount}
New Amount: ₹{discounted_amount}

Use this discount code for your purchase!"""
    
    # Show payment page with discounted amount
    plan_id = context.user_data.get('current_plan_id')
    if plan_id:
        buttons = get_payment_buttons(plan_id, discounted_amount)
        await query.edit_message_text(text, reply_markup=buttons, parse_mode=ParseMode.MARKDOWN)

async def generate_invite_link(query, context):
    """Generate secure invite link for premium user"""
    user_id = query.from_user.id
    user_data = db.get_user(user_id)
    
    if not user_data or not user_data[6]:
        await query.edit_message_text("You are not a premium user!")
        return
    
    channel_settings = db.get_channel_settings()
    premium_channel_id = channel_settings[0] if channel_settings else None
    
    if not premium_channel_id:
        await query.edit_message_text("Premium channel not configured. Please contact admin.")
        return
    
    try:
        # Create one-time invite link that expires in 10 seconds
        invite_link = await context.bot.create_chat_invite_link(
            chat_id=premium_channel_id,
            member_limit=1,
            expire_date=int(asyncio.get_event_loop().time() + 10)
        )
        
        await query.edit_message_text(
            f"🔗 *Your Premium Access Link*\n\n"
            f"{invite_link.invite_link}\n\n"
            f"⚠️ *Important:*\n"
            f"• This link is valid for 10 seconds only\n"
            f"• Can be used by 1 person only\n"
            f"• Link expires after first use\n\n"
            f"Please click immediately!",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        await query.edit_message_text(f"Failed to generate link. Error: {str(e)}")

async def back_to_start(query):
    """Return to start menu"""
    user = query.from_user
    start_message = db.get_start_message()
    start_image = db.get_start_image()
    formatted_message = format_start_message(start_message, user)
    buttons = get_start_buttons(db)
    
    if start_image:
        await query.edit_message_media(
            media=telegram.InputMediaPhoto(media=start_image, caption=formatted_message),
            reply_markup=buttons
        )
    else:
        await query.edit_message_text(formatted_message, reply_markup=buttons)

async def refresh_admin_status(query):
    """Refresh admin status display"""
    # This will be handled in admin handlers
    pass

import asyncio
import telegram
