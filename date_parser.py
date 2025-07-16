import re
from datetime import datetime, timedelta
from dateutil import parser
import calendar
from logger import logger

months = ["january", "february", "march", "april", 
        "may", "june", "july", "august", 
        "september", "october", "november", "december"]

weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

today = datetime.now()

# Helper function to add a month to a date
def add_month(date):
    month = date.month + 1 if date.month < 12 else 1
    year = date.year + 1 if date.month == 12 else date.year
    day = min(date.day, calendar.monthrange(year, month)[1])  # Handle month-end overflow
    return date.replace(year=year, month=month, day=day)

def next_weekday(day_name):
        day_name = day_name.lower()
        if day_name not in weekdays:
            return None
        today_weekday = today.weekday()  # Monday is 0, Sunday is 6
        target_weekday = weekdays.index(day_name)
        days_until = (target_weekday - today_weekday + 7) % 7
        days_until = days_until or 7  # Ensure it's at least 7 days ahead (next occurrence)
        return today + timedelta(days=days_until)

def extract_dates(user_input):
    parsed_dates = []

    # Handle relative dates like "in X days"
    relative_matches = re.findall(r"in (\d+) days", user_input, re.IGNORECASE)
    for match in relative_matches:
        days_offset = int(match)
        parsed_dates.append(today + timedelta(days=days_offset))
    # Remove the relative match phrase from the input to avoid duplicate processing
    user_input = re.sub(r"in (\d+) days", "", user_input, flags=re.IGNORECASE)
    


    # # Handle relative dates like "in X days" or "next week"
    # relative_match = re.search(r"in (\d+) days", user_input, re.IGNORECASE)
    # if relative_match:
    #     days_offset = int(relative_match.group(1))
    #     parsed_dates.append(today + timedelta(days=days_offset))
    #     # Remove the relative match phrase from the input to avoid duplicate processing
    #     user_input = re.sub(r"in (\d+) days", "", user_input, flags=re.IGNORECASE)

    # Handle specific dates and different date formattings
    date_pattern = (
        r"\b(?:the )?"                         # optional "the"
        r"(\d{1,2}(?:st|nd|rd|th)?)"           # Match day (with or without suffix- st, th, etc)
        r"(?: of)?(?: \w+)?"                   # Optionally match 'of' followed by a month
        r"|(\d{1,2}/\d{1,2}/\d{2,4})"          # Match DD/MM/YYYY format
        r"|(\w+ \d{1,2})"                      # Match Month Day (e.g., November 19)
    )
    date_matches = re.findall(date_pattern, user_input, re.IGNORECASE)

    # Handle keywords like "today" or "tomorrow"
    if "today" in user_input.lower():
        parsed_dates.append(today)

    if "tomorrow" in user_input.lower():
        parsed_dates.append(today + timedelta(days=1))

    for day in weekdays:
        if f"{day}" in user_input.lower():
            next_date = next_weekday(day)
            if next_date:
                parsed_dates.append(next_date)  # Return the date as a list for consistency

    if not date_matches:
        return parsed_dates

    for date in date_matches:
        # Extract the matched date string
        # date_str = "".join(date).strip()
        date_str = " ".join(filter(None, date)).strip()  # Join non-empty parts
        logger.debug(date_str)
        try:
            # Parse each date string into a datetime object
            parsed_date = parser.parse(date_str, fuzzy=True)
            logger.debug("parsed date = %s", parsed_date)

            # Check if the date is explicitly in the past
            if parsed_date < datetime.now():
                if any(keyword in date_str.lower() for keyword in months):
                    # Explicitly past date (e.g., "November 19th" when today is November 26th)
                    logger.debug(f"Date {date_str} has already passed.")
                    continue  # Skip adding this date
                else:
                    # Adjust implicit dates (e.g., "19th" without a month)
                    parsed_date = add_month(parsed_date)
                    logger.debug("updated date =  %s", parsed_date)

            # Add future or adjusted dates
            if parsed_date >= datetime.now():
                parsed_dates.append(parsed_date)
                logger.debug("appended date")

        except ValueError:
            print(f"Could not parse date: {date}")

    logger.debug("parsed dates - %s", parsed_dates)
    return parsed_dates