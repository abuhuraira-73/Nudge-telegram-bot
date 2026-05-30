from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from database.db import SessionLocal
from database.models import Reminder, User
from utils.ai_parser import parse_with_ai
from notifications.calendar import add_to_calendar
import logging
import pytz
from datetime import datetime, timedelta

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Main handler for all text messages.
    Uses AI to parse the reminder and save it.
    """
    text = update.message.text
    user_id = update.effective_user.id
    logging.info(f"Received message from {user_id}: {text}")
    
    # Show "typing" indicator while Gemini thinks
    await context.bot.send_chat_action(chat_id=user_id, action="typing")
    
    # 1. Fetch user data
    session = SessionLocal()
    user_tz_str = "UTC"
    has_calendar = False
    try:
        user = session.query(User).filter(User.user_id == user_id).first()
        if user:
            if user.timezone:
                user_tz_str = user.timezone
            if user.calendar_token:
                has_calendar = True
    except Exception as e:
        logging.error(f"Error fetching user data: {e}")
    
    # 2. Parse with AI
    parsed_data = parse_with_ai(text, user_tz_str)
    
    if not parsed_data or not parsed_data.get('remind_at'):
        logging.warning(f"AI could not parse a valid time from: {text}")
        await update.message.reply_text("🤔 I couldn't quite catch the time for that. Please be more specific (e.g., 'tomorrow at 10am', 'in 5 minutes').")
        session.close()
        return

    # 3. Save to database
    try:
        new_reminder = Reminder(
            user_id=user_id,
            message=parsed_data['task'],
            remind_at=parsed_data['remind_at'],
            priority=parsed_data.get('priority', 'normal')
        )
        session.add(new_reminder)
        session.commit()
        
        # 4. Sync with Google Calendar if connected
        if has_calendar:
            add_to_calendar(user_id, parsed_data['task'], parsed_data['remind_at'])

        # 5. Rich Success Summary Card
        local_tz = pytz.timezone(user_tz_str)
        local_time = parsed_data['remind_at'].astimezone(local_tz)
        
        date_str = local_time.strftime("%A, %b %d")
        time_str = local_time.strftime("%I:%M %p")
        
        priority_emoji = "🔴" if parsed_data.get('priority') == 'high' else "🔵"
        recurring_info = f"\n🔄 **Repeat:** {parsed_data['recurring'].capitalize()}" if parsed_data.get('recurring') else ""

        reply_msg = (
            f"🎯 **Reminder Set!**\n\n"
            f"📝 **Task:** {parsed_data['task']}\n"
            f"📅 **Date:** {date_str}\n"
            f"⏰ **Time:** {time_str} ({user_tz_str})\n"
            f"{priority_emoji} **Priority:** {parsed_data['priority'].capitalize()}"
            f"{recurring_info}\n\n"
        )
        
        if has_calendar:
            reply_msg += "🗓️ *Synced with Google Calendar*"
            
        await update.message.reply_text(reply_msg, parse_mode='Markdown')
        
    except Exception as e:
        logging.error(f"Error saving reminder: {e}")
        await update.message.reply_text("❌ Sorry, I had trouble saving that reminder.")
    finally:
        session.close()

async def list_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Shows a list of active reminders for the user.
    """
    user_id = update.effective_user.id
    session = SessionLocal()
    try:
        # Fetch pending reminders
        reminders = session.query(Reminder).filter(
            Reminder.user_id == user_id,
            Reminder.notification_sent == False
        ).order_by(Reminder.remind_at.asc()).all()

        if not reminders:
            await update.message.reply_text("✨ You have no active reminders! Use natural language to set one.")
            return

        # Fetch user timezone for display
        user = session.query(User).filter(User.user_id == user_id).first()
        user_tz = pytz.timezone(user.timezone if user and user.timezone else "UTC")

        msg = "📋 **Your Active Reminders:**\n\n"
        for r in reminders:
            local_time = r.remind_at.replace(tzinfo=pytz.UTC).astimezone(user_tz)
            time_str = local_time.strftime("%b %d, %I:%M %p")
            msg += f"🔹 **ID: {r.id}** | {r.message}\n   ⏰ {time_str}\n\n"
        
        msg += "🗑️ To delete one, use: `/delete ID`"
        await update.message.reply_text(msg, parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Error listing reminders: {e}")
        await update.message.reply_text("❌ Failed to fetch your reminders.")
    finally:
        session.close()

async def delete_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Deletes a specific reminder by ID.
    """
    user_id = update.effective_user.id
    args = context.args
    
    if not args:
        await update.message.reply_text("❌ Please provide the reminder ID: `/delete 5`")
        return

    try:
        reminder_id = int(args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid ID. Please provide a number.")
        return

    session = SessionLocal()
    try:
        reminder = session.query(Reminder).filter(
            Reminder.id == reminder_id,
            Reminder.user_id == user_id
        ).first()

        if not reminder:
            await update.message.reply_text("❌ Reminder not found or it doesn't belong to you.")
            return

        session.delete(reminder)
        session.commit()
        await update.message.reply_text(f"✅ Deleted reminder **#{reminder_id}**.")

    except Exception as e:
        logging.error(f"Error deleting reminder: {e}")
        await update.message.reply_text("❌ Failed to delete the reminder.")
    finally:
        session.close()

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the inline keyboard button presses.
    """
    query = update.callback_query
    await query.answer()

    action_data = query.data.split("_")
    action = action_data[0]
    reminder_id = int(action_data[1])
    
    session = SessionLocal()
    try:
        reminder = session.query(Reminder).filter(Reminder.id == reminder_id).first()
        if not reminder:
            await query.edit_message_text(text="This reminder was already handled.")
            return

        if action == "done":
            reminder.is_done = True
            session.commit()
            await query.edit_message_text(text=f"✅ Great! Marked **{reminder.message}** as done.")

        elif action == "snooze":
            # Show multi-option snooze menu
            keyboard = [
                [
                    InlineKeyboardButton("5m", callback_data=f"sz_5_{reminder_id}"),
                    InlineKeyboardButton("30m", callback_data=f"sz_30_{reminder_id}"),
                    InlineKeyboardButton("1h", callback_data=f"sz_60_{reminder_id}"),
                ],
                [InlineKeyboardButton("Tomorrow", callback_data=f"sz_1440_{reminder_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text=f"⏰ How long should I snooze **{reminder.message}**?",
                reply_markup=reply_markup
            )

        elif action == "sz":
            # Handle specific snooze duration
            minutes = int(action_data[1])
            new_time = datetime.utcnow() + timedelta(minutes=minutes)
            reminder.remind_at = new_time
            reminder.notification_sent = False
            session.commit()
            
            user = session.query(User).filter(User.user_id == reminder.user_id).first()
            user_tz = pytz.timezone(user.timezone if user and user.timezone else "UTC")
            local_time = new_time.replace(tzinfo=pytz.UTC).astimezone(user_tz)
            time_str = local_time.strftime("%I:%M %p")
            
            await query.edit_message_text(text=f"⏳ Snoozed! I'll remind you again at **{time_str}**.")

    except Exception as e:
        logging.error(f"Button callback error: {e}")
        await query.edit_message_text(text="❌ An error occurred.")
    finally:
        session.close()
