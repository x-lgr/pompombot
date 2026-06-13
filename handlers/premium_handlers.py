import random
import string
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from database import Database
from keyboards.inline_keyboards import (
    get_plan_buttons, 
    get_plan_detail_buttons, 
    get_payment_buttons,
    get_cancel_buttons,
    get_premium_panel_buttons,
    get_start_buttons
)
from utils.helpers import generate_payment_url, format_start_message
from config import Config

db = Database()

# Conversation states for payment submission
WAITING_FOR_SCREENSHOT = 1
WAITING_FOR_UTR = 2
WAITING_FOR_PAYMENT_MSG = 3

async def show_plans(query, page=0):
    """Show available plans to user"""
    plans = db.get_plans()
    
    if not plans:
        await query.edit_message_text(
            "❌ No plans available at the moment.\n\nPlease contact admin for assistance."
        )
        return
    
    text = "💎 *Choose Your Premium Plan*\n\n"
    for plan in plans:
        text += f"• *{plan[1]}* - ₹{plan[2]}\n"
        if plan[3]:
            text += f"  _{plan[3]}_\n"
        text += "\n"
    
    text += "Select a plan below to view details:"
    
    buttons = get_plan_buttons(plans, page)
    await query.edit_message_text(
        text, 
        reply_markup=buttons, 
        parse_mode=ParseMode.MARKDOWN
    )

async def show_plan_detail(query, plan_id):
    """Show detailed information about a specific plan"""
    plan = db.get_plan(plan_id)
    if not plan:
        await query.edit_message_text("❌ Plan not found.")
        return
    
    text = f"""💰 *{plan[1]} Plan Details*

━━━━━━━━━━━━━━━━━━━━
💵 *Price:* ₹{plan[2]}
━━━━━━━━━━━━━━━━━━━━

📝 *Description:*
{plan[3] if plan[3] else 'No description available.'}

⏱️ *Duration:* {plan[4] if plan[4] else 'Lifetime Access'}

✨ *Benefits:*
• Premium channel access
• Exclusive content
• Priority support
• No ads

Click Buy Now to proceed with payment."""
    
    buttons = get_plan_detail_buttons(plan_id, plan[2])
    
    # Store current plan in context for later use
    query.message.chat_id
    context.user_data['current_plan'] = {
        'id': plan_id,
        'name': plan[1],
        'price': plan[2],
        'description': plan[3],
        'duration': plan[4]
    }
    
    await query.edit_message_text(
        text, 
        reply_markup=buttons, 
        parse_mode=ParseMode.MARKDOWN
    )

async def process_payment(query, plan_id, amount):
    """Generate payment page for user"""
    user_id = query.from_user.id
    plan = db.get_plan(plan_id)
    payment_settings = db.get_payment_settings()
    
    # Check if payment system is configured
    if not payment_settings:
        await query.edit_message_text(
            "❌ Payment system is not configured.\n\nPlease contact admin for assistance."
        )
        return
    
    upi_id, receiver_name, upi_name, bank_name, payment_url = payment_settings
    
    # Validate required fields
    if not upi_name or not bank_name:
        await query.edit_message_text(
            "❌ Payment system is not properly configured.\n\nPlease contact admin for assistance."
        )
        return
    
    # Check for existing discount
    discount_info = context.user_data.get('discount', None)
    final_amount = amount
    discount_percent = 0
    discount_code = None
    
    if discount_info:
        final_amount = discount_info['discounted_amount']
        discount_percent = discount_info['discount_percent']
        discount_code = discount_info['code']
    
    # Generate payment URL
    payment_url_full = generate_payment_url(upi_name, bank_name, final_amount)
    
    # Store payment context
    context.user_data['pending_payment'] = {
        'plan_id': plan_id,
        'plan_name': plan[1],
        'original_price': amount,
        'discount_percent': discount_percent,
        'discount_code': discount_code,
        'final_amount': final_amount,
        'upi_id': upi_id,
        'receiver_name': receiver_name,
        'payment_url': payment_url_full
    }
    
    text = f"""💳 *Payment Details*

━━━━━━━━━━━━━━━━━━━━
🏦 *UPI ID:* `{upi_id}`
👤 *Receiver:* {receiver_name}
💰 *Amount:* ₹{final_amount}
━━━━━━━━━━━━━━━━━━━━

🔗 *Payment Link:*
{payment_url_full}

📱 *How to Pay:*
1️⃣ Click the payment button below
2️⃣ Complete payment using any UPI app
3️⃣ Click "I Have Paid" button
4️⃣ Upload screenshot and UTR number

⚠️ *Important:*
• Send EXACT amount: ₹{final_amount}
• Keep transaction screenshot
• Note down UTR number
• Wrong amount will not be approved

✨ *Discount Applied:* {discount_percent}% OFF
   Final Price: ₹{final_amount}
""" if discount_percent > 0 else f"""💳 *Payment Details*

━━━━━━━━━━━━━━━━━━━━
🏦 *UPI ID:* `{upi_id}`
👤 *Receiver:* {receiver_name}
💰 *Amount:* ₹{final_amount}
━━━━━━━━━━━━━━━━━━━━

🔗 *Payment Link:*
{payment_url_full}

📱 *How to Pay:*
1️⃣ Click the payment button below
2️⃣ Complete payment using any UPI app
3️⃣ Click "I Have Paid" button
4️⃣ Upload screenshot and UTR number

⚠️ *Important:*
• Send EXACT amount: ₹{final_amount}
• Keep transaction screenshot
• Note down UTR number
• Wrong amount will not be approved
"""
    
    buttons = get_payment_buttons(plan_id, final_amount)
    
    await query.edit_message_text(
        text, 
        reply_markup=buttons, 
        parse_mode=ParseMode.MARKDOWN
    )

async def show_cancel_with_discount(query):
    """Show cancellation message with discount offer"""
    text = """😅 *Maybe the price feels a little high?*

Don't worry! We have a special offer just for you! 🎁

Click the button below to get a random discount!
*1% to 25% OFF* on your purchase!

✨ *One-time offer* - Valid for this session only!"""
    
    buttons = get_cancel_buttons()
    await query.edit_message_text(
        text, 
        reply_markup=buttons, 
        parse_mode=ParseMode.MARKDOWN
    )

async def generate_discount(query):
    """Generate random discount for user"""
    user_id = query.from_user.id
    
    # Get current payment context
    payment_context = context.user_data.get('pending_payment', {})
    
    if not payment_context:
        await query.edit_message_text(
            "❌ Session expired. Please start over by clicking Buy Premium again."
        )
        return
    
    original_amount = payment_context.get('original_price', 0)
    if not original_amount:
        await query.edit_message_text(
            "❌ Invalid payment session. Please restart."
        )
        return
    
    # Generate random discount between 1% and 25%
    discount_percent = random.randint(1, 25)
    discounted_amount = int(original_amount - (original_amount * discount_percent / 100))
    
    # Generate unique discount code
    discount_code = f"DISC{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
    
    # Save discount to database
    db.save_discount(
        user_id, 
        discount_code, 
        discount_percent, 
        original_amount, 
        discounted_amount
    )
    
    # Store discount in context
    context.user_data['discount'] = {
        'code': discount_code,
        'discount_percent': discount_percent,
        'original_amount': original_amount,
        'discounted_amount': discounted_amount
    }
    
    # Update pending payment with discount
    context.user_data['pending_payment']['discount_percent'] = discount_percent
    context.user_data['pending_payment']['discount_code'] = discount_code
    context.user_data['pending_payment']['final_amount'] = discounted_amount
    
    text = f"""🎉 *Congratulations! You got a discount!*

━━━━━━━━━━━━━━━━━━━━
✨ *Discount:* {discount_percent}% OFF
🎫 *Code:* `{discount_code}`
💰 *Original:* ₹{original_amount}
💵 *New Amount:* ₹{discounted_amount}
💸 *You Save:* ₹{original_amount - discounted_amount}
━━━━━━━━━━━━━━━━━━━━

Click the payment button below with the new amount!

⚠️ *Note:* This discount is valid only for this purchase session."""
    
    # Show payment page with discounted amount
    plan_id = payment_context.get('plan_id')
    buttons = get_payment_buttons(plan_id, discounted_amount)
    
    await query.edit_message_text(
        text, 
        reply_markup=buttons, 
        parse_mode=ParseMode.MARKDOWN
    )

async def start_payment_submission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start payment submission process"""
    query = update.callback_query
    await query.answer()
    
    # Check if there's an active payment session
    if 'pending_payment' not in context.user_data:
        await query.edit_message_text(
            "❌ No active payment session found.\n\nPlease start over by clicking Buy Premium."
        )
        return
    
    await query.edit_message_text(
        "📸 *Payment Submission*\n\n"
        "Please send:\n"
        "1. Screenshot of the payment transaction\n"
        "2. UTR Number (Transaction Reference Number)\n"
        "3. Any message (optional)\n\n"
        "Send the screenshot as a PHOTO with caption containing UTR and message.\n\n"
        "Example caption:\n"
        "`UTR: ABC123XYZ789`\n"
        "`Message: Paid for premium plan`\n\n"
        "Or send screenshot first, then I'll ask for UTR.",
        parse_mode=ParseMode.MARKDOWN
    )
    
    return WAITING_FOR_SCREENSHOT

async def receive_payment_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive payment screenshot from user"""
    if not update.message.photo:
        await update.message.reply_text(
            "❌ Please send a photo of your payment screenshot."
        )
        return WAITING_FOR_SCREENSHOT
    
    # Get highest quality photo
    photo = update.message.photo[-1]
    context.user_data['payment_screenshot'] = photo.file_id
    
    # Check if caption contains UTR
    caption = update.message.caption or ""
    
    # Try to extract UTR from caption
    import re
    utr_match = re.search(r'UTR:\s*([A-Za-z0-9]+)', caption, re.IGNORECASE)
    
    if utr_match:
        context.user_data['payment_utr'] = utr_match.group(1)
        context.user_data['payment_message'] = caption.replace(f"UTR: {utr_match.group(1)}", "").strip()
        
        # Save payment
        await save_payment_submission(update, context)
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "✅ Screenshot received!\n\n"
            "Now please send your UTR Number (Transaction Reference Number).\n\n"
            "Example: `UTR123456789`",
            parse_mode=ParseMode.MARKDOWN
        )
        return WAITING_FOR_UTR

async def receive_payment_utr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive UTR number from user"""
    utr = update.message.text.strip()
    
    if not utr:
        await update.message.reply_text(
            "❌ Please send a valid UTR number."
        )
        return WAITING_FOR_UTR
    
    context.user_data['payment_utr'] = utr
    
    await update.message.reply_text(
        "✅ UTR Number received!\n\n"
        "Now send any additional message (or send 'skip' to skip):"
    )
    return WAITING_FOR_PAYMENT_MSG

async def receive_payment_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive optional message from user"""
    message = update.message.text
    
    if message.lower() == 'skip':
        context.user_data['payment_message'] = ""
    else:
        context.user_data['payment_message'] = message
    
    # Save payment
    await save_payment_submission(update, context)
    return ConversationHandler.END

async def save_payment_submission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save payment submission to database"""
    user = update.effective_user
    payment_data = context.user_data.get('pending_payment', {})
    
    if not payment_data:
        if update.callback_query:
            await update.callback_query.edit_message_text(
                "❌ Payment session expired. Please start over."
            )
        else:
            await update.message.reply_text(
                "❌ Payment session expired. Please start over with /start"
            )
        return
    
    # Save to database
    payment_id = db.add_pending_payment(
        user_id=user.id,
        plan_name=payment_data.get('plan_name', 'Unknown'),
        original_price=payment_data.get('original_price', 0),
        discount_percent=payment_data.get('discount_percent', 0),
        final_amount=payment_data.get('final_amount', 0),
        utr_number=context.user_data.get('payment_utr', ''),
        screenshot_file_id=context.user_data.get('payment_screenshot', ''),
        user_message=context.user_data.get('payment_message', '')
    )
    
    # Notify user
    await update.message.reply_text(
        f"✅ *Payment Submitted Successfully!*\n\n"
        f"📋 *Payment ID:* `{payment_id}`\n"
        f"💰 *Amount:* ₹{payment_data.get('final_amount', 0)}\n"
        f"🔢 *UTR:* `{context.user_data.get('payment_utr', '')}`\n\n"
        f"⏳ *Status:* Pending Review\n\n"
        f"An admin will review your payment shortly.\n"
        f"You will receive a notification once approved.\n\n"
        f"Thank you for your purchase! 🙏",
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Notify all admins
    await notify_admins(update, context, payment_id, user, payment_data)
    
    # Clear payment session
    context.user_data.pop('pending_payment', None)
    context.user_data.pop('payment_screenshot', None)
    context.user_data.pop('payment_utr', None)
    context.user_data.pop('payment_message', None)

async def notify_admins(update: Update, context: ContextTypes.DEFAULT_TYPE, payment_id, user, payment_data):
    """Notify all admins about new payment submission"""
    from config import Config
    
    text = f"""🆕 *New Payment Submission*

━━━━━━━━━━━━━━━━━━━━
👤 *User:* {user.first_name}
🔹 *Username:* @{user.username if user.username else 'N/A'}
🆔 *User ID:* `{user.id}`
━━━━━━━━━━━━━━━━━━━━

📋 *Payment Details:*
🆔 *Payment ID:* `{payment_id}`
📝 *Plan:* {payment_data.get('plan_name', 'Unknown')}
💰 *Original Price:* ₹{payment_data.get('original_price', 0)}
🎁 *Discount:* {payment_data.get('discount_percent', 0)}%
💵 *Final Amount:* ₹{payment_data.get('final_amount', 0)}
🔢 *UTR:* `{context.user_data.get('payment_utr', '')}`

💬 *User Message:* 
{context.user_data.get('payment_message', 'No message')}

📸 *Screenshot:* Attached below

Use the buttons below to approve or reject this payment.
"""
    
    from keyboards.inline_keyboards import get_admin_payment_buttons
    buttons = get_admin_payment_buttons(payment_id)
    
    for admin_id in Config.ADMIN_IDS:
        try:
            if context.user_data.get('payment_screenshot'):
                await context.bot.send_photo(
                    chat_id=admin_id,
                    photo=context.user_data['payment_screenshot'],
                    caption=text,
                    reply_markup=buttons,
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=text + "\n⚠️ *No screenshot provided*",
                    reply_markup=buttons,
                    parse_mode=ParseMode.MARKDOWN
                )
        except Exception as e:
            print(f"Failed to notify admin {admin_id}: {e}")

async def generate_invite_link(query, context):
    """Generate secure invite link for premium user"""
    user_id = query.from_user.id
    user_data = db.get_user(user_id)
    
    # Check if user is premium
    if not user_data or not user_data[6]:
        await query.edit_message_text(
            "❌ *Access Denied*\n\n"
            "You are not a premium user.\n"
            "Use /start to purchase premium membership.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Get premium channel settings
    channel_settings = db.get_channel_settings()
    premium_channel_id = channel_settings[0] if channel_settings else None
    
    if not premium_channel_id:
        await query.edit_message_text(
            "❌ *Premium Channel Not Configured*\n\n"
            "Please contact admin for assistance.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    try:
        # Create one-time invite link that expires in 10 seconds
        expire_time = int(asyncio.get_event_loop().time() + Config.INVITE_LINK_EXPIRE_SECONDS)
        
        invite_link = await context.bot.create_chat_invite_link(
            chat_id=premium_channel_id,
            member_limit=1,
            expire_date=expire_time
        )
        
        text = f"""🔗 *Your Premium Access Link*

━━━━━━━━━━━━━━━━━━━━
🔐 *Link:* {invite_link.invite_link}
⏱️ *Valid For:* {Config.INVITE_LINK_EXPIRE_SECONDS} seconds
👥 *Max Uses:* 1 person
━━━━━━━━━━━━━━━━━━━━

⚠️ *Important Instructions:*
• Click the link IMMEDIATELY
• Link expires in {Config.INVITE_LINK_EXPIRE_SECONDS} seconds
• Can only be used ONCE
• After use, link becomes invalid

⚡ *Quick Action Required!*
Click the link now to join the premium channel!

_Need help? Contact admin_"""
        
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        await query.edit_message_text(
            f"❌ *Failed to generate link*\n\n"
            f"Error: {str(e)}\n\n"
            f"Please contact admin for assistance.",
            parse_mode=ParseMode.MARKDOWN
        )

async def premium_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show premium user panel"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = db.get_user(user_id)
    
    if not user_data or not user_data[6]:
        text = """⭐ *Premium Access Required*

You don't have an active premium subscription.

Use /start to purchase premium membership and unlock:
• Exclusive content
• Premium channel access
• Priority support
• And much more!"""
        
        buttons = [[InlineKeyboardButton("💎 Buy Premium", callback_data="buy_premium")]]
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Premium user panel
    text = f"""⭐ *Premium User Panel*

━━━━━━━━━━━━━━━━━━━━
👤 *User:* {query.from_user.first_name}
📝 *Plan:* {user_data[7] if user_data[7] else 'Premium'}
📅 *Purchase Date:* {user_data[8] if user_data[8] else 'N/A'}
✅ *Status:* Active
━━━━━━━━━━━━━━━━━━━━

🔧 *Available Actions:*
• Generate secure access link to premium channel
• View your subscription details
• Get support

_Thank you for being a premium member!_"""
    
    buttons = get_premium_panel_buttons()
    await query.edit_message_text(
        text,
        reply_markup=buttons,
        parse_mode=ParseMode.MARKDOWN
    )

async def check_premium_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check and return premium status for user"""
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    if user_data and user_data[6]:
        return True, user_data
    return False, None

async def auto_approve_premium(user_id, plan_name):
    """Auto approve premium user (can be called after payment verification)"""
    db.make_premium(user_id, plan_name)
    
    # Generate welcome message
    user_data = db.get_user(user_id)
    
    return True
