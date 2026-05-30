import logging
import pytz
from telegram import Update
from telegram.ext import ContextTypes
from database.db import SessionLocal
from database.models import User

async def set_timezone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for the /timezone command.
    Allows users to set their preferred timezone.
    """
    user_id = update.effective_user.id
    args = context.args
    
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.user_id == user_id).first()
        
        if not args:
            # Show current timezone
            current_tz = user.timezone if user else "UTC"
            await update.message.reply_text(
                f"🌍 Your current timezone is set to: **{current_tz}**\n\n"
                "To change it, use: `/timezone Region/City`\n"
                "Example: `/timezone Asia/Kolkata` or `/timezone America/New_York`",
                parse_mode='Markdown'
            )
            return

        new_tz = args[0]
        
        # Validate timezone
        try:
            pytz.timezone(new_tz)
        except pytz.exceptions.UnknownTimeZoneError:
            await update.message.reply_text(
                "❌ Sorry, that's not a valid timezone.\n"
                "Please use a valid IANA timezone name like `Europe/London` or `UTC`."
            )
            return

        # Update user record
        if user:
            user.timezone = new_tz
            session.commit()
            logging.info(f"User {user_id} updated timezone to {new_tz}")
            await update.message.reply_text(f"✅ Timezone updated to: **{new_tz}**", parse_mode='Markdown')
        else:
            # This shouldn't happen if /start was used, but safety first
            new_user = User(user_id=user_id, timezone=new_tz)
            session.add(new_user)
            session.commit()
            await update.message.reply_text(f"✅ Timezone set to: **{new_tz}**", parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Error setting timezone: {e}")
        await update.message.reply_text("❌ An error occurred while saving your timezone.")
    finally:
        session.close()

async def set_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for the /email command.
    Allows users to set their email for notifications.
    """
    user_id = update.effective_user.id
    args = context.args
    
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.user_id == user_id).first()
        
        if not args:
            current_email = user.email if user and user.email else "Not set"
            await update.message.reply_text(
                f"📧 Your notification email is: **{current_email}**\n\n"
                "To change it, use: `/email your@email.com`",
                parse_mode='Markdown'
            )
            return

        new_email = args[0]
        
        # Simple regex for basic email validation
        import re
        if not re.match(r"[^@]+@[^@]+\.[^@]+", new_email):
            await update.message.reply_text("❌ Please provide a valid email address.")
            return

        if user:
            user.email = new_email
            session.commit()
            logging.info(f"User {user_id} updated email to {new_email}")
            await update.message.reply_text(f"✅ Notification email updated to: **{new_email}**", parse_mode='Markdown')
        else:
            new_user = User(user_id=user_id, email=new_email)
            session.add(new_user)
            session.commit()
            await update.message.reply_text(f"✅ Notification email set to: **{new_email}**", parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Error setting email: {e}")
        await update.message.reply_text("❌ An error occurred while saving your email.")
    finally:
        session.close()

async def connect_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for the /connect command.
    Sends the Google authorization URL to the user.
    """
    import os
    if not os.path.exists('credentials.json'):
        await update.message.reply_text(
            "❌ Google Calendar integration is not configured on the server (missing credentials.json)."
        )
        return

    from utils.calendar_auth import get_auth_url
    auth_url = get_auth_url()
    
    message = (
        "🔗 **Connect Google Calendar**\n\n"
        "To sync your reminders with Google Calendar, please follow these steps:\n"
        f"1. [Click here to sign in with Google]({auth_url})\n"
        "2. After signing in, your browser will try to go to `localhost` and show an error (e.g., 'Site can't be reached'). **This is normal!**\n"
        "3. **Look at the URL bar** of that error page. It will look like: `http://localhost/?code=4/0Af...` \n"
        "4. **Copy the code** (everything after `code=`) and send it back using: `/auth YOUR_CODE_HERE`"
    )
    await update.message.reply_text(message, parse_mode='Markdown')

async def auth_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for the /auth command.
    Exchanges the auth code for a token and saves it.
    """
    user_id = update.effective_user.id
    args = context.args
    
    if not args:
        await update.message.reply_text("❌ Please provide the authorization code: `/auth YOUR_CODE_HERE`", parse_mode='Markdown')
        return

    auth_code = args[0]
    session = SessionLocal()
    try:
        from utils.calendar_auth import exchange_code
        token_json = exchange_code(auth_code)
        
        user = session.query(User).filter(User.user_id == user_id).first()
        if user:
            user.calendar_token = token_json
            session.commit()
            await update.message.reply_text("✅ Success! Your Google Calendar is now connected. 🗓️")
        else:
            await update.message.reply_text("❌ User not found. Please run /start first.")
            
    except Exception as e:
        logging.error(f"Error during calendar auth: {e}")
        await update.message.reply_text("❌ Failed to authorize. Please make sure the code is correct and try again.")
    finally:
        session.close()
