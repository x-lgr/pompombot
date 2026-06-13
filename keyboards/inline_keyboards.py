
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_start_buttons(db):
    """Get start menu buttons from database"""
    buttons = db.get_buttons()
    keyboard = []
    
    for button in buttons:
        keyboard.append([InlineKeyboardButton(button[2], url=button[3])])
    
    # Add premium and demo buttons
    settings = db.get_channel_settings()
    demo_url = settings[1] if settings else ""
    
    keyboard.append([
        InlineKeyboardButton("💎 Buy Premium", callback_data="buy_premium"),
        InlineKeyboardButton("🎬 Watch Demo", url=demo_url) if demo_url else InlineKeyboardButton("🎬 Watch Demo", callback_data="no_demo")
    ])
    
    return InlineKeyboardMarkup(keyboard)

def get_plan_buttons(plans, page=0, items_per_page=3):
    """Get plan selection buttons"""
    keyboard = []
    start = page * items_per_page
    end = start + items_per_page
    page_plans = plans[start:end]
    
    row = []
    for plan in page_plans:
        row.append(InlineKeyboardButton(plan[1], callback_data=f"plan_{plan[0]}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    # Navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Previous", callback_data=f"plan_page_{page-1}"))
    if end < len(plans):
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"plan_page_{page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton("🔴 Back", callback_data="back_to_start")])
    
    return InlineKeyboardMarkup(keyboard)

def get_plan_detail_buttons(plan_id, amount):
    """Get plan detail page buttons"""
    keyboard = [
        [InlineKeyboardButton(f"🟢 Pay ₹{amount} via UPI", callback_data=f"pay_{plan_id}_{amount}")],
        [InlineKeyboardButton("🔴 Back", callback_data="back_to_plans")],
        [InlineKeyboardButton("I Have Paid", callback_data="submit_payment")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_payment_buttons(plan_id, amount):
    """Get payment page buttons"""
    keyboard = [
        [InlineKeyboardButton(f"🟢 Pay ₹{amount} via UPI", callback_data=f"process_payment_{plan_id}_{amount}")],
        [InlineKeyboardButton("🔴 Cancel", callback_data="cancel_payment")],
        [InlineKeyboardButton("I Have Paid", callback_data="submit_payment")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_cancel_buttons():
    """Get cancel/back buttons"""
    keyboard = [
        [InlineKeyboardButton("🔴 Cancel", callback_data="cancel_payment")],
        [InlineKeyboardButton("🎁 Get Discount", callback_data="get_discount")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_payment_buttons(payment_id):
    """Get admin payment review buttons"""
    keyboard = [
        [
            InlineKeyboardButton("🟢 Approve", callback_data=f"approve_payment_{payment_id}"),
            InlineKeyboardButton("🔴 Reject", callback_data=f"reject_payment_{payment_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_premium_panel_buttons():
    """Get premium user panel buttons"""
    keyboard = [
        [InlineKeyboardButton("🔗 Generate Access Link", callback_data="generate_link")],
        [InlineKeyboardButton("🔴 Back to Start", callback_data="back_to_start")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_broadcast_confirmation_buttons():
    """Get broadcast confirmation buttons"""
    keyboard = [
        [
            InlineKeyboardButton("🟢 Confirm & Send", callback_data="broadcast_confirm"),
            InlineKeyboardButton("🔴 Cancel", callback_data="broadcast_cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_broadcast_button_prompt():
    """Get broadcast button prompt"""
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="broadcast_add_button"),
            InlineKeyboardButton("No", callback_data="broadcast_no_button")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_help_buttons(db):
    """Get help menu buttons"""
    settings = db.get_channel_settings()
    demo_url = settings[1] if settings else ""
    
    keyboard = [
        [
            InlineKeyboardButton("💎 Buy Premium", callback_data="buy_premium"),
            InlineKeyboardButton("🎬 Watch Demo", url=demo_url) if demo_url else InlineKeyboardButton("🎬 Watch Demo", callback_data="no_demo")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_status_refresh_buttons():
    """Get status refresh button for admin"""
    keyboard = [[InlineKeyboardButton("🔄 Refresh", callback_data="refresh_status")]]
    return InlineKeyboardMarkup(keyboard)
