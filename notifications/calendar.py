import logging
from datetime import datetime, timedelta
from database.db import SessionLocal
from database.models import User
from utils.calendar_auth import get_calendar_service

def add_to_calendar(user_id: int, task_message: str, remind_at: datetime):
    """
    Adds a reminder as an event to the user's Google Calendar.
    """
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.user_id == user_id).first()
        if not user or not user.calendar_token:
            logging.info(f"User {user_id} has not connected Google Calendar.")
            return False

        service = get_calendar_service(user.calendar_token)
        if not service:
            logging.error(f"Failed to get calendar service for user {user_id}")
            return False

        # Define event details
        # Ensure times are in UTC and formatted as clean ISO strings
        start_time = remind_at.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_time = (remind_at + timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M:%SZ')

        event = {
            'summary': f'Reminder: {task_message}',
            'description': f'Automated reminder from {user.first_name if user.first_name else "Nudge Bot"}',
            'start': {
                'dateTime': start_time,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'UTC',
            },
            'reminders': {
                'useDefault': True,
            },
        }

        logging.info(f"Adding event to Google Calendar for user {user_id}: {task_message}")
        event = service.events().insert(calendarId='primary', body=event).execute()
        logging.info(f"Event created: {event.get('htmlLink')}")
        return True

    except Exception as e:
        logging.error(f"Error adding event to Google Calendar: {e}")
        return False
    finally:
        session.close()
