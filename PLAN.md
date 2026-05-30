# Nudge Bot - Comprehensive Project State

## 🚀 OVERVIEW
Nudge Bot is a smart personal assistant on Telegram designed to handle natural language reminders and sync them across multiple platforms (Email, Google Calendar).

---

## ✅ IMPLEMENTED FEATURES (DONE)

### 1. Core Bot Engine
- **Telegram Integration**: Fully functional bot using `python-telegram-bot`.
- **Background Scheduler**: Uses `JobQueue` to poll the database every 60 seconds and deliver reminders.
- **SQLite Database**: Persistent storage for users and reminders (`nudge_bot.db`).

### 2. Timezone Management
- **Command**: `/timezone <Region/City>` (e.g., `/timezone Asia/Kolkata`).
- **Feature**: Reminders are parsed and stored in UTC but confirmed and listed in the user's local time.
- **Smart Parsing**: Relative times like "tomorrow 9am" are calculated based on the user's timezone.

### 3. Notification Channels
- **Telegram**: Direct message with interactive buttons.
- **Email**: Sends reminder notifications via SMTP (Gmail integration ready).
- **Google Calendar**: Full OAuth 2.0 integration. Reminders are automatically created as events on the user's primary calendar.

### 4. UI & Management
- **Command Menu**: Register with Telegram's `/` menu for easy discovery.
- **Management Commands**:
    - `/list`: Displays all active, pending reminders with IDs.
    - `/delete <ID>`: Allows users to remove specific reminders.
- **Interactive Notifications**: Reminders arrive with `[Done ✅]` and `[Snooze 10m ⏳]` buttons.

---

## 🛠️ ONGOING WORK (IN PROGRESS)

### Advanced Brain Integration (Gemini AI)
- **Goal**: Replace the basic pattern-based parser with Gemini Flash 1.5.
- **Status**: 
    - `google-generativeai` installed.
    - API Key stored in `.env`.
    - `utils/ai_parser.py` created with complex prompt logic.
    - **Current Block**: Finalizing the parsing of Gemini's JSON output and ensuring robust relative time calculation.

---

## ⏳ REMAINING STEPS (TODO)

### 1. Cloud Deployment (The Finale)
- **Database Migration**: Switch from SQLite to PostgreSQL (required for production).
- **Hosting**: Move the bot to **Railway.app** or a similar service.
- **Environment Cleanup**: Ensure all keys are moved to production environment variables.

---

## 📝 TECHNICAL NOTES
- **Local Machine Dependencies**: `python-telegram-bot`, `apscheduler`, `google-generativeai`, `google-auth-oauthlib`, `pytz`, `sqlalchemy`.
- **Database Schema**:
    - `users`: `user_id`, `username`, `first_name`, `email`, `timezone`, `calendar_token`.
    - `reminders`: `id`, `user_id`, `message`, `remind_at`, `priority`, `is_done`, `notification_sent`.
