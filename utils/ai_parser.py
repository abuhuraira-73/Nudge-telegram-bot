import google.generativeai as genai
from config import Config
import logging
import json
from datetime import datetime
import pytz

# Configure the Gemini model
genai.configure(api_key=Config.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

# This is our upgraded "Super Prompt" for Gemini
SYSTEM_PROMPT = """
You are a highly intelligent, proactive reminder assistant. Your goal is to extract structured reminder details from user text, even if the input is messy or complex.

### CONTEXT:
- Current UTC Time: {current_utc}
- User's Local Time: {current_local}
- User's Timezone: {user_timezone}

### EXTRACTION RULES:
1. **task**: The core thing the user wants to do. Remove filler words like "remind me to".
2. **remind_at**: 
   - A DATETIME string in the USER'S LOCAL TIME (YYYY-MM-DD HH:MM:SS).
   - If relative (e.g., "in 2 hours"), calculate relative to the User's Local Time provided.
   - If ambiguous (e.g., "in the evening"), use 18:00:00 (6 PM) of the user's local day.
   - If "tonight", use 20:00:00 (8 PM) local.
   - If no time is provided, set to null.
3. **priority**: 
   - "high" if the user uses words like "urgent", "asap", "important", "must", or all-caps.
   - Otherwise, "normal".
4. **recurring**: 
   - Identify the frequency: "daily", "weekly", "monthly", "weekdays", or null.
   - If the user says "every Friday", set to "weekly".
   - If the user says "every morning", set to "daily".

### HANDLING COMPLEXITY:
- If the user corrects themselves (e.g., "at 5, no make it 6"), only extract the final intent.
- If multiple times are mentioned, pick the one that fits the reminder context best.

### OUTPUT FORMAT:
- Return ONLY a raw JSON object. No markdown, no explanation.
{{
  "task": "string",
  "remind_at": "YYYY-MM-DD HH:MM:SS",
  "priority": "high|normal",
  "recurring": "daily|weekly|monthly|weekdays|null"
}}

### EXAMPLES:
User: "urgent! buy milk tomorrow morning"
{{"task": "buy milk", "remind_at": "2026-05-31 09:00:00", "priority": "high", "recurring": null}}

User: "remind me every Monday at 8am to water plants"
{{"task": "water plants", "remind_at": "2026-06-01 08:00:00", "priority": "normal", "recurring": "weekly"}}
"""

def parse_with_ai(text: str, user_timezone: str):
    """
    Uses Gemini to parse a natural language string.
    Returns a dictionary with the structured data.
    """
    try:
        # Get Current UTC and Current Local
        now_utc = datetime.now(pytz.UTC)
        user_tz = pytz.timezone(user_timezone)
        now_local = now_utc.astimezone(user_tz)
        
        current_utc_str = now_utc.strftime('%Y-%m-%d %H:%M:%S')
        current_local_str = now_local.strftime('%Y-%m-%d %H:%M:%S')

        prompt = SYSTEM_PROMPT.format(
            current_utc=current_utc_str,
            current_local=current_local_str,
            user_timezone=user_timezone
        ) + f'\nUser: "{text}"\nJSON:'
        
        logging.info(f"AI Prompt sent for text: {text}")
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        logging.info(f"AI Raw Response: {raw_text}")
        
        # Clean up potential markdown
        cleaned_response = raw_text.replace('```json', '').replace('```', '').strip()
        
        data = json.loads(cleaned_response)
        
        if data.get('remind_at'):
            # Gemini returns LOCAL time string as requested in new prompt
            # We parse it and localize it to the user's timezone, then convert to UTC
            dt_naive = datetime.strptime(data['remind_at'], '%Y-%m-%d %H:%M:%S')
            dt_local = user_tz.localize(dt_naive)
            data['remind_at'] = dt_local.astimezone(pytz.UTC)
        
        return data

    except Exception as e:
        logging.error(f"AI parsing failed: {e}")
        return None
