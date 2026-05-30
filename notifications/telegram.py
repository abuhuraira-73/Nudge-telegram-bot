import logging
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from config import Config

async def send_reminder_notification(application, user_id: int, reminder_id: int, task_message: str):
    """
    Sends a telegram message with inline buttons.
    """
    try:
        logging.info(f"Sending notification for reminder {reminder_id} to {user_id}")
        
        keyboard = [
            [
                InlineKeyboardButton("Done ✅", callback_data=f"done_{reminder_id}"),
                InlineKeyboardButton("Snooze 10m ⏳", callback_data=f"snooze_{reminder_id}"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await application.bot.send_message(
            chat_id=user_id,
            text=f"🔔 **REMINDER**\n\nDon't forget to: **{task_message}**",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return True
    except Exception as e:
        logging.error(f"Failed to send telegram notification: {e}")
        return False
