#!/usr/bin/env python3
import asyncio
import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters
)
from config import Config
from handlers import user_handlers, admin_handlers, broadcast_handlers
from database import Database

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
START_MSG, START_IMAGE, BUTTON_NAME, BUTTON_URL, BUTTON_ID, EDIT_BUTTON_ID, EDIT_BUTTON_NAME, EDIT_BUTTON_URL = range(8)
PLAN_NAME, PLAN_PRICE, PLAN_DESC, PLAN_DURATION, PLAN_ORDER = range(8, 13)
UPI_ID, RECEIVER_NAME, UPI_NAME, BANK_NAME = range(13, 17)
BROADCAST_CONTENT, BROADCAST_BUTTON_NAME, BROADCAST_BUTTON_URL, BROADCAST_CONFIRM = range(17, 21)

def main():
    """Start the bot"""
    # Initialize database
    db = Database()
    logger.info("Database initialized")
    
    # Create application
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # User commands (single slash)
    application.add_handler(CommandHandler("start", user_handlers.start))
    application.add_handler(CommandHandler("help", user_handlers.help_command))
    application.add_handler(CommandHandler("premium", user_handlers.premium_command))
    application.add_handler(CommandHandler("status", user_handlers.status_command))
    
    # Admin commands (double question mark)
    application.add_handler(MessageHandler(filters.Regex(r'^\?\?setstart$'), admin_handlers.set_start_message))
    application.add_handler(MessageHandler(filters.Regex(r'^\?\?viewstart$'), admin_handlers.view_start_message))
    application.add_handler(MessageHandler(filters.Regex(r'^\?\?resetstart$'), admin_handlers.reset_start_message))
    application.add_handler(MessageHandler(filters.Regex(r'^\?\?setstartimage$'), admin_handlers.set_start_image))
    application.add_handler(MessageHandler(filters.Regex(r'^\?\?viewstartimage$'), admin_handlers.view_start_image))
    application.add_handler(MessageHandler(filters.Regex(r'^\?\?removestartimage$'), admin_handlers.remove_start_image))
    application.add_handler(MessageHandler(filters.Regex(r'^\?\?resetstartimage$'), admin_handlers.reset_start_image))
    application.add_handler(MessageHandler(filters.Regex(r'^\?\?addbutton$'), admin_handlers.add_button))
    application.add_handler(MessageHandler(filters.Regex(r'^\?\?removebutton$'), admin_handlers.remove_button))
    application.add_handler(MessageHandler(filters.Regex(r'^\?\?editbutton$'), admin_handlers.edit_button))
    application.add_handler(MessageHandler(filters.Regex(r'^\?\?buttons$'), admin_handlers.show_buttons))
    application.add_handler(MessageHandler(filters.Regex(r'^\?\?addplan$'), admin_handlers.add_plan))
    application.add_handler(MessageHandler(filters.Regex(r'^\?\?editplan$'), admin_handlers.edit_plan))
    application.add_handler(MessageHandler(filters.Regex(r'^\?\?removeplan$'), admin_handlers.remove_plan))
    application.add_handler(MessageHandler(filters.Regex(r'^\?\?plans$'), admin_handlers.list_plans))
    application.add_handler(MessageHandler(filters.Regex(r'^\?\?setupi$'), admin_handlers.setup_upi))
    application.add_handler(MessageHandler(filters.Regex(r'^\?\?setupiname$'), admin_handlers.setup_upi_name))
    application.add_handler(MessageHandler(filters.Regex(r'^\?\?setreceiver$'), admin_handlers.setup_receiver_name))
    application.add_handler(MessageHandler(filters.Regex(r'^\?\?setbankname$'), admin_handlers.set_bank_name))
    application.add_handler(MessageHandler(filters.Regex(r'^\?\?setpaymenturl$'), admin_handlers.set_payment_url))
    application.add_handler(MessageHandler(filters.Regex(r'^\?\?setpremiumchannel$'), admin_handlers.set_premium_channel))
    application.add_handler(MessageHandler(filters.Regex(r'^\?\?setdemochannel$'), admin_handlers.set_demo_channel))
    application.add_handler(MessageHandler(filters.Regex(r'^\?\?broadcast$'), broadcast_handlers.start_broadcast))
    application.add_handler(MessageHandler(filters.Regex(r'^\?\?backupusers$'), admin_handlers.backup_users))
    application.add_handler(MessageHandler(filters.Regex(r'^\?\?importusers$'), admin_handlers.import_users))
    application.add_handler(MessageHandler(filters.Regex(r'^\?\?rebuilddb$'), admin_handlers.rebuild_database))
    application.add_handler(MessageHandler(filters.Regex(r'^\?\?status$'), admin_handlers.admin_status))
    application.add_handler(MessageHandler(filters.Regex(r'^\?\?stats$'), admin_handlers.admin_stats))
    application.add_handler(MessageHandler(filters.Regex(r'^\?\?payments$'), admin_handlers.review_payments))
    application.add_handler(MessageHandler(filters.Regex(r'^\?\?help$'), admin_handlers.admin_help))
    
    # Conversation handlers
    start_msg_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r'^\?\?setstart$'), admin_handlers.set_start_message)],
        states={
            START_MSG: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.receive_start_message)],
        },
        fallbacks=[]
    )
    
    start_image_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r'^\?\?setstartimage$'), admin_handlers.set_start_image)],
        states={
            START_IMAGE: [MessageHandler(filters.PHOTO, admin_handlers.receive_start_image)],
        },
        fallbacks=[]
    )
    
    button_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r'^\?\?addbutton$'), admin_handlers.add_button)],
        states={
            BUTTON_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.receive_button_name)],
            BUTTON_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.receive_button_url)],
        },
        fallbacks=[]
    )
    
    remove_button_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r'^\?\?removebutton$'), admin_handlers.remove_button)],
        states={
            BUTTON_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.confirm_remove_button)],
        },
        fallbacks=[]
    )
    
    edit_button_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r'^\?\?editbutton$'), admin_handlers.edit_button)],
        states={
            EDIT_BUTTON_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.select_edit_button)],
            EDIT_BUTTON_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.edit_button_name)],
            EDIT_BUTTON_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.edit_button_url)],
        },
        fallbacks=[]
    )
    
    plan_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r'^\?\?addplan$'), admin_handlers.add_plan)],
        states={
            PLAN_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.receive_plan_name)],
            PLAN_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.receive_plan_price)],
            PLAN_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.receive_plan_desc)],
            PLAN_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.receive_plan_duration)],
            PLAN_ORDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.receive_plan_order)],
        },
        fallbacks=[]
    )
    
    upi_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r'^\?\?setupi$'), admin_handlers.setup_upi)],
        states={
            UPI_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.receive_upi)],
        },
        fallbacks=[]
    )
    
    upi_name_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r'^\?\?setupiname$'), admin_handlers.setup_upi_name)],
        states={
            UPI_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.receive_upi_name)],
        },
        fallbacks=[]
    )
    
    receiver_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r'^\?\?setreceiver$'), admin_handlers.setup_receiver_name)],
        states={
            RECEIVER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.receive_receiver_name)],
        },
        fallbacks=[]
    )
    
    bank_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r'^\?\?setbankname$'), admin_handlers.set_bank_name)],
        states={
            BANK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.receive_bank_name)],
        },
        fallbacks=[]
    )
    
    broadcast_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r'^\?\?broadcast$'), broadcast_handlers.start_broadcast)],
        states={
            BROADCAST_CONTENT: [MessageHandler(filters.PHOTO | filters.TEXT, broadcast_handlers.receive_broadcast_content)],
            BROADCAST_BUTTON_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_handlers.receive_button_name)],
            BROADCAST_BUTTON_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_handlers.receive_button_url)],
            BROADCAST_CONFIRM: [CallbackQueryHandler(broadcast_handlers.broadcast_button_callback)],
        },
        fallbacks=[]
    )
    
    # Add conversation handlers
    application.add_handler(start_msg_conv)
    application.add_handler(start_image_conv)
    application.add_handler(button_conv)
    application.add_handler(remove_button_conv)
    application.add_handler(edit_button_conv)
    application.add_handler(plan_conv)
    application.add_handler(upi_conv)
    application.add_handler(upi_name_conv)
    application.add_handler(receiver_conv)
    application.add_handler(bank_conv)
    application.add_handler(broadcast_conv)
    
    # Callback query handler for buttons
    application.add_handler(CallbackQueryHandler(user_handlers.button_callback, pattern="^(buy_premium|back_to_start|plan_|back_to_plans|pay_|cancel_payment|get_discount|submit_payment|generate_link|no_demo|refresh_status|plan_page_)"))
    application.add_handler(CallbackQueryHandler(broadcast_handlers.broadcast_button_callback, pattern="^(bc_|bc_)"))
    application.add_handler(CallbackQueryHandler(admin_handlers.payment_callback, pattern="^(approve_payment_|reject_payment_)"))
    
    # Payment submission handler
    application.add_handler(MessageHandler(filters.PHOTO & filters.CAPTION, user_handlers.receive_payment_details))
    
    # Start bot
    logger.info("Bot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
