import smtplib
import logging
from email.message import EmailMessage
from config import Config

def send_email_notification(recipient_email: str, task_message: str):
    """
    Sends an email reminder to the user.
    """
    if not Config.EMAIL_USER or not Config.EMAIL_PASSWORD:
        logging.warning("Email credentials not set. Skipping email notification.")
        return False

    try:
        msg = EmailMessage()
        msg.set_content(f"🔔 REMINDER\n\nDon't forget to: {task_message}")
        msg['Subject'] = f"Reminder: {task_message[:30]}..."
        msg['From'] = Config.EMAIL_USER
        msg['To'] = recipient_email

        logging.info(f"Sending email notification to {recipient_email}")
        
        # Connect to server and send
        with smtplib.SMTP(Config.EMAIL_SERVER, Config.EMAIL_PORT) as server:
            server.starttls() # Secure the connection
            server.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
            server.send_message(msg)
            
        logging.info(f"Email sent successfully to {recipient_email}")
        return True
    except Exception as e:
        logging.error(f"Failed to send email notification: {e}")
        return False
