from database.db import SessionLocal
from database.models import Reminder, User
from notifications.telegram import send_reminder_notification
from notifications.email import send_email_notification
from datetime import datetime
from telegram.ext import ContextTypes
import logging

import pytz

async def check_reminders(context: ContextTypes.DEFAULT_TYPE):
    """
    Job that runs periodically to check for due reminders.
    Uses the bot's built-in JobQueue.
    """
    application = context.application
    logging.info("--- SCHEDULER: Starting Check ---")
    
    session = SessionLocal()
    try:
        # 1. Get current time in UTC
        now = datetime.now(pytz.UTC)
        
        # 2. Fetch ALL pending reminders to manually filter (Safer for SQLite)
        pending = session.query(Reminder).filter(Reminder.notification_sent == False).all()
        
        if not pending:
            logging.info("--- SCHEDULER: No pending reminders in DB ---")
            return

        due_reminders = []
        for r in pending:
            # Ensure r.remind_at is aware for comparison
            r_time = r.remind_at
            if r_time.tzinfo is None:
                r_time = pytz.UTC.localize(r_time)
            
            if r_time <= now:
                due_reminders.append(r)
            else:
                logging.info(f"--- SCHEDULER: Reminder {r.id} ('{r.message}') is for the future: {r_time} (Now: {now})")

        if not due_reminders:
            return

        logging.info(f"--- SCHEDULER: Found {len(due_reminders)} due reminders! Sending now... ---")

        for reminder in due_reminders:
            # Send Telegram notification
            logging.info(f"--- SCHEDULER: Attempting TG send for {reminder.id} ---")
            tg_success = await send_reminder_notification(
                application, 
                reminder.user_id,
                reminder.id,
                reminder.message
            )
            
            if tg_success:
                reminder.notification_sent = True
                session.commit()
                logging.info(f"--- SCHEDULER: Success! Marked {reminder.id} as sent. ---")
            else:
                logging.error(f"--- SCHEDULER: FAILED to send TG for {reminder.id} ---")
            
            # Check for and send email notification
            user = session.query(User).filter(User.user_id == reminder.user_id).first()
            if user and user.email:
                send_email_notification(user.email, reminder.message)

    except Exception as e:
        logging.error(f"Error in check_reminders: {e}")
        session.rollback()
    finally:
        session.close()
