<p align="center">
  <a href="https://github.com/abuhuraira-73/Nudge-telegram-bot/blob/main/LICENSE.md">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License">
  </a>
  <a href="https://github.com/abuhuraira-73/Nudge-telegram-bot/issues">
    <img src="https://img.shields.io/github/issues-pr/abuhuraira-73/Nudge-telegram-bot" alt="Pull Requests">
  </a>
  <a href="GEMINI_LOG.md">
    <img src="https://img.shields.io/badge/Gemini-Log-blueviolet" alt="Gemini Log">
  </a>
</p>

## 🚀 Project Overview

**Nudge Bot** is an intelligent, natural-language personal assistant built for Telegram. It replaces clunky, command-based reminder tools with a "human-like" interface that understands exactly what you mean. Whether it's a quick snooze or a sync to your Google Calendar, Nudge handles the complexity so you can stay focused.

**Built from the ground up by a solo founder, this project showcases the power of combining modern AI (Gemini) with robust automation workflows.**

## ✨ Features

*   **🧠 AI-Powered Brain:** Uses Google Gemini 1.5 Flash to parse messy natural language into structured data. It understands corrections, priorities, and ambiguous times like "tonight" or "in the evening."
*   **🌍 Smart Timezones:** Automatically handles IANA timezone conversions. Confirms reminders in your local time while storing them in UTC for absolute accuracy.
*   **🗓️ Google Calendar Sync:** Seamlessly creates events in your primary Google Calendar. Features an automated "Smooth Flow" OAuth 2.0 handshake—no manual code copying required.
*   **📧 Email Alerts:** Optional SMTP integration to receive reminder backups in your inbox.
*   **🎨 Rich UI Experience:** 
    *   **Onboarding Checklist:** A 1-2-3 guide for new users to set up timezones and sync calendars instantly.
    *   **Summary Cards:** Beautifully formatted confirmation messages with emojis.
    *   **Persistent Menu:** Bottom-docked buttons for quick navigation.
    *   **Dynamic Snooze:** Inline options to snooze for 5m, 30m, 1h, or "Tomorrow."
*   **⚡ Faster Scheduler:** A high-precision background engine that polls for due reminders every 30 seconds.

## 🗺️ Roadmap

### ✅ Core Features (Implemented)

*   **👤 User Timezone Management:** `/timezone` command with IANA validation.
*   **🤖 Advanced AI Parser:** Fully integrated "Super Prompt" for Gemini that handles priority and relative calculations.
*   **⌨️ Interactive UI:** Custom Reply Keyboards and Inline buttons for a "mobile app" feel.
*   **💾 Database Persistence:** Full PostgreSQL integration with SSL support for cloud stability.
*   **🗓️ OAuth 2.0 Calendar Flow:** Secure connection to Google Calendar.
*   **🔔 Reliable Notifications:** Background scheduler with timezone-aware logic and 30s precision.
*   **☁️ Cloud Deployment:** Production-ready deployment on Railway.app with persistent storage.

### 🚧 Currently Working On

*   **🔄 Recurring Reminders:** Adding logic to automatically reschedule tasks marked as "daily," "weekly," or "weekdays" once they are completed.

### 🚀 Upcoming Features

*   **🎙️ Voice Note Reminders:** Send a voice message and let the AI transcribe and set the reminder.
*   **🔗 "Remind Me About This":** Ability to forward a message from any chat to the bot to create a reminder about it.
*   **💬 Multi-Language Support:** Expanding Gemini's prompt to support reminders in non-English languages.

## 🛠️ Technology Stack

Nudge Bot leverages a modern and robust stack:

### Core & Bot Logic
*   **Python 3.10+** - <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" alt="Python" width="20" height="20"/>
*   **python-telegram-bot** - High-level asynchronous bot framework.
*   **APScheduler** - Powering the background task engine.
*   **SQLAlchemy** - Database ORM for SQLite/PostgreSQL flexibility.

### AI & Integrations
*   **Google Gemini AI** - <img src="https://img.shields.io/badge/Gemini-1.5%20Flash-blueviolet" alt="Gemini" height="20"/> - For advanced natural language understanding.
*   **Google Calendar API** - OAuth 2.0 and Event management.
*   **pytz** - Reliable timezone handling.

## 🚀 Installation & Setup

To get Nudge Bot running on your local machine:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/abuhuraira-73/Nudge-telegram-bot.git
    cd Nudge-telegram-bot
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Environment Variables:**
    Create a `.env` file in the root directory:
    ```env
    TELEGRAM_BOT_TOKEN="your_bot_token"
    GEMINI_API_KEY="your_api_key"
    DATABASE_URL="sqlite:///./nudge_bot.db" # Or your Postgres URL
    ```
4.  **Run the application:**
    ```bash
    python bot.py
    ```

## 🌐 Deployment

*   **Backend:** Hosted on **Railway.app** (via `Procfile`).
*   **Database:** **PostgreSQL** (Managed).
*   **CI/CD:** Automatic deployment via **GitHub** integration.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 📧 Contact

For questions, feedback, or collaboration inquiries, please reach out to the solo founder, **Abuhuraira Jamal**:

*   **LinkedIn:** [https://www.linkedin.com/in/abuhurairajamal/](https://www.linkedin.com/in/abuhurairajamal/)
*   **Email:** abuhuraira1514@gmail.com
