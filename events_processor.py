import events_parser
import pytz

from datetime import datetime, timedelta
from dateutil import parser

def process_events(events):
    processed_events = []
    source_tz = pytz.timezone('America/Toronto') # ET used by the CBC API response
    utc_tz = pytz.utc
    current_year = datetime.now().year # Assume current year unless specified otherwise
    for event in events:
        try:
            # Combine date and time - needs careful handling based on scraped format
            # Example: If date_str is "April 28" and time_str is "2:00 PM ET"
            # This parsing needs to be robust!
            dt_str = f"{event['date_str']} {current_year} {event['time_str'].replace(' ET', '')}"
            naive_dt = parser.parse(dt_str)

            # Localize to source timezone, then convert to UTC
            localized_dt = source_tz.localize(naive_dt)
            start_utc = localized_dt.astimezone(utc_tz)

            # Estimate end time (e.g., 2 hours later) if not available
            end_utc = start_utc + timedelta(hours=2)

            # Format for Google Calendar API (RFC3339)
            start_formatted = start_utc.isoformat()
            end_formatted = end_utc.isoformat()

            processed_events.append({
                'summary': event['title'],
                'description': f"Link: {event.get('link', 'N/A')}\nOriginally scheduled for {event['time_str']} ET.",
                'start': {'dateTime': start_formatted, 'timeZone': 'UTC'},
                'end': {'dateTime': end_formatted, 'timeZone': 'UTC'},
            })

        except Exception as e:
            print(f"Error processing date/time for event '{event['title']}': {e}")
    return processed_events

if __name__ == '__main__': # testing only
    print(process_events(events_parser.load_all_events())) 
