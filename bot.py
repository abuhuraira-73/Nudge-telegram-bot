import logging
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from config import Config
from database.db import init_db, SessionLocal
from database.models import User
from handlers.reminder import handle_message, list_reminders, delete_reminder, button_callback
from handlers.settings import set_timezone, set_email, connect_calendar, auth_calendar
from utils.scheduler import check_reminders

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def set_commands(application):
    """
    Registers the command list with Telegram for the '/' menu.
    """
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("help", "How to use the bot"),
        BotCommand("list", "Show your active reminders"),
        BotCommand("delete", "Delete a reminder (e.g. /delete 5)"),
        BotCommand("timezone", "Set your local timezone"),
        BotCommand("email", "Set your notification email"),
        BotCommand("connect", "Connect Google Calendar"),
    ]
    await application.bot.set_my_commands(commands)
    logging.info("--- Command menu registered with Telegram ---")

from telegram import Update, BotCommand, ReplyKeyboardMarkup, KeyboardButton

...

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /start command."""
    user_data = update.effective_user
    logging.info(f"START command received from {user_data.id}")
    
    # Save user to database
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.user_id == user_data.id).first()
        if not user:
            user = User(
                user_id=user_data.id,
                username=user_data.username,
                first_name=user_data.first_name
            )
            session.add(user)
            session.commit()
            logging.info(f"New user registered: {user_data.first_name} ({user_data.id})")
    except Exception as e:
        logging.error(f"error saving user: {e}")
    finally:
        session.close()

    # Create persistent Reply Keyboard
    keyboard = [
        [KeyboardButton("📋 List Reminders"), KeyboardButton("🌍 Set Timezone")],
        [KeyboardButton("📧 Set Email"), KeyboardButton("🗓️ Connect Calendar")],
        [KeyboardButton("❓ Help")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    message = (
        f"👋 Hello {user_data.first_name}!\n\n"
        f"I'm **{Config.BOT_DISPLAY_NAME}**, your personal reminder assistant. 🔔\n\n"
        "You can send me reminders in natural language like:\n"
        "• 'remind me to call Mom at 5pm'\n"
        "• 'remind me to submit report tomorrow 9am'\n\n"
        "Use the menu below for quick actions!\n\n"
        "🌐 **Visit my creator:** [abuhuraira.in](https://www.abuhuraira.in/)"
    )
    await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /help command."""
    help_text = (
        "🤖 **Nudge Bot Help**\n\n"
        "**Basic Commands:**\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n\n"
        "**Setting Reminders:**\n"
        "Just type your reminder naturally! Examples:\n"
        "- 'remind me to buy milk in 2 hours'\n"
        "- 'water plants every morning at 8am'\n\n"
        "I'll handle the rest! 🚀"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

from aiohttp import web

...

async def handle_callback(request):
    """
    Handles the Google OAuth callback.
    Exchanges code for token and saves to database for the specific user.
    """
    code = request.query.get('code')
    user_id = request.query.get('state') # We passed this as 'state'
    
    if not code or not user_id:
        return web.Response(text="❌ Invalid callback parameters.", status=400)

    try:
        # Exchange code for token
        from utils.calendar_auth import exchange_code
        token_json = exchange_code(code)
        
        # Save to database
        session = SessionLocal()
        user = session.query(User).filter(User.user_id == int(user_id)).first()
        if user:
            user.calendar_token = token_json
            session.commit()
            session.close()
            logging.info(f"--- Automated Calendar Link Success for user {user_id} ---")
            
            # Show Success HTML
            html = """
            <div style="font-family: sans-serif; text-align: center; margin-top: 100px;">
                <h1 style="color: #4CAF50;">✅ Authentication Successful!</h1>
                <p>Your Google Calendar is now connected to Nudge Bot.</p>
                <p>You can close this window and return to Telegram.</p>
            </div>
            """
            return web.Response(text=html, content_type="text/html")
        else:
            session.close()
            return web.Response(text="User not found in database.", status=404)

    except Exception as e:
        logging.error(f"Callback error: {e}")
        return web.Response(text=f"Authentication failed: {str(e)}", status=500)

async def run_webserver():
    """Starts the aiohttp web server."""
    app = web.Application()
    app.router.add_get('/callback', handle_callback)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', Config.PORT)
    await site.start()
    logging.info(f"--- Web server started on port {Config.PORT} ---")

if __name__ == '__main__':
    # Initialize database
    init_db()

    # Initialize the bot application
    application = ApplicationBuilder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # ... rest of handlers ...

    # Add this in the main block
    import asyncio
    loop = asyncio.get_event_loop()
    loop.create_task(run_webserver())
    
    # Add command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('list', list_reminders))
    application.add_handler(CommandHandler('delete', delete_reminder))
    application.add_handler(CommandHandler('timezone', set_timezone))
    application.add_handler(CommandHandler('email', set_email))
    application.add_handler(CommandHandler('connect', connect_calendar))
    application.add_handler(CommandHandler('auth', auth_calendar))
    
    # Add handler for button callbacks
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add message handlers for Reply Keyboard buttons
    application.add_handler(MessageHandler(filters.Regex('^📋 List Reminders$'), list_reminders))
    application.add_handler(MessageHandler(filters.Regex('^🌍 Set Timezone$'), set_timezone))
    application.add_handler(MessageHandler(filters.Regex('^📧 Set Email$'), set_email))
    application.add_handler(MessageHandler(filters.Regex('^🗓️ Connect Calendar$'), connect_calendar))
    application.add_handler(MessageHandler(filters.Regex('^❓ Help$'), help_command))
    
    # Add message handler for reminders (anything that isn't a command)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Schedule the reminder check job every 30 seconds
    if application.job_queue:
        application.job_queue.run_repeating(check_reminders, interval=30, first=10)
        logging.info("--- Job Queue started (30s intervals) ---")
    else:
        logging.warning("--- Job Queue NOT available. Reminders will not be sent! ---")
    
    # Register the '/' menu commands
    application.post_init = set_commands

    print(f"--- {Config.BOT_DISPLAY_NAME} is now running! ---")
    
    # Start the bot
    application.run_polling()
