import dateparser
from datetime import datetime
import re

def parse_reminder(text: str, user_timezone: str = "UTC"):
    """
    Parses a natural language string to extract a task and a datetime.
    Example: 'remind me to buy milk tomorrow at 10am'
    Returns: (task, remind_at_datetime) or (None, None)
    """
    # 1. Clean up common prefixes
    prefixes = [
        r"remind me to\s*",
        r"remind me\s*",
        r"set a reminder for\s*",
        r"nudge me to\s*",
    ]
    
    clean_text = text.lower()
    for p in prefixes:
        clean_text = re.sub(p, "", clean_text)

    # 2. Try to split task and time using common separators
    separators = [" at ", " on ", " in ", " tomorrow", " next ", " today"]
    
    best_task = clean_text
    best_time = None
    
    # We try to find the time part by looking for keywords
    # This is a simple heuristic-based approach
    for sep in separators:
        if sep in clean_text:
            parts = clean_text.split(sep, 1)
            task_part = parts[0].strip()
            time_part = sep + parts[1] # Keep the separator for dateparser
            
            # Use dateparser to try and find a date
            parsed_dt = dateparser.parse(
                time_part,
                settings={
                    'PREFER_DATES_FROM': 'future',
                    'TIMEZONE': user_timezone,
                    'TO_TIMEZONE': 'UTC',
                    'RETURN_AS_TIMEZONE_AWARE': True
                }
            )
            
            if parsed_dt:
                # If we found a date, ensure it's in the future
                if parsed_dt > datetime.now(parsed_dt.tzinfo):
                    best_task = task_part
                    best_time = parsed_dt
                    break

    # 3. Fallback: If no separator worked, try parsing the whole thing (e.g. "tomorrow 10am")
    if not best_time:
        parsed_dt = dateparser.parse(
            clean_text,
            settings={
                'PREFER_DATES_FROM': 'future',
                'TIMEZONE': user_timezone,
                'TO_TIMEZONE': 'UTC',
                'RETURN_AS_TIMEZONE_AWARE': True
            }
        )
        if parsed_dt and parsed_dt > datetime.now(parsed_dt.tzinfo):
            best_time = parsed_dt
            best_task = "Reminder" # Generic task

    return best_task.capitalize() if best_task else "Reminder", best_time

# Quick test logic
if __name__ == "__main__":
    test_strings = [
        "remind me to buy milk tomorrow at 10am",
        "remind me to call dad in 5 minutes",
        "submit report next Friday 9am"
    ]
    for ts in test_strings:
        task, dt = parse_reminder(ts)
        print(f"Input: {ts} -> Task: {task}, Time: {dt}")
