import events_parser
import json
import pytz

from datetime import datetime, timedelta
from dateutil import parser

def process_events(events): # 'events' is a list of raw event dicts from events_parser.py
    processed_events = []
    seen_event_identifiers = set() # To keep track of unique raw event identifiers

    source_tz = pytz.timezone('America/Toronto') # ET likely used by CBC schedule
    utc_tz = pytz.utc
    current_year = datetime.now().year

    print(f"Processing {len(events)} raw events for de-duplication and formatting...")
    skipped_duplicates = 0
    skipped_missing_info = 0

    for i, event in enumerate(events): # 'event' is a raw event dict
        # Ensure basic structure and get values safely, providing defaults
        raw_title = event.get('title')
        raw_date_str = event.get('date_str')
        raw_time_str = event.get('time_str')

        # Normalize and clean the components for the unique identifier
        # Convert to string and strip whitespace. Handle None by converting to empty string first.
        event_title = str(raw_title).strip() if raw_title is not None else ""
        event_date_str = str(raw_date_str).strip() if raw_date_str is not None else ""
        event_time_str = str(raw_time_str).strip() if raw_time_str is not None else ""
        
        # A unique identifier for the raw event based on its key properties
        # If any critical part is missing, we can't reliably de-duplicate or process.
        if not event_title or not event_date_str or not event_time_str:
            print(f"  [Event {i+1}/{len(events)}] Skipping event due to missing critical info: Title='{event_title}', Date='{event_date_str}', Time='{event_time_str}'")
            skipped_missing_info += 1
            continue
            
        unique_identifier = (event_title, event_date_str, event_time_str)

        # Check for duplicates based on the raw identifier
        if unique_identifier in seen_event_identifiers:
            print(f"  [Event {i+1}/{len(events)}] Skipping duplicate event: {unique_identifier}")
            skipped_duplicates += 1
            continue
        else:
            seen_event_identifiers.add(unique_identifier)

        # Proceed with processing if it's not a duplicate
        try:
            # Construct the full datetime string for parsing
            # Use the already cleaned event_date_str and event_time_str
            dt_str = f"{event_date_str} {current_year} {event_time_str.replace(' ET', '')}"
            naive_dt = parser.parse(dt_str)

            # Localize to source timezone, then convert to UTC
            localized_dt = source_tz.localize(naive_dt)
            start_utc = localized_dt.astimezone(utc_tz)

            # Estimate end time (e.g., 2 hours later)
            # You might want to make the duration configurable or smarter later
            end_utc = start_utc + timedelta(hours=2)

            start_formatted = start_utc.isoformat()
            end_formatted = end_utc.isoformat()

            # Note: The 'link' key was in a previous conceptual example.
            # Your current events_parser.py doesn't add a 'link'.
            # If you add it later, you can include it in the description.
            description = f"Originally scheduled for {event_time_str} ET on CBC."
            if 'sport' in event: # If your parser adds the sport category
                description += f"\nSport Category: {event['sport']}"


            processed_events.append({
                'summary': event_title, # Use the cleaned title
                'description': description,
                'start': {'dateTime': start_formatted, 'timeZone': 'UTC'},
                'end': {'dateTime': end_formatted, 'timeZone': 'UTC'},
            })

        except Exception as e:
            print(f"  [Event {i+1}/{len(events)}] Error processing event identified by '{unique_identifier}': {e}")
            # For more detailed debugging during development, you can uncomment the next two lines:
            # import traceback
            # traceback.print_exc()
            
    print(f"De-duplication complete. Skipped {skipped_duplicates} duplicate events.")
    print(f"Skipped {skipped_missing_info} events due to missing critical information.")
    print(f"Returning {len(processed_events)} unique, processed events.")
    return processed_events

if __name__ == '__main__': # testing only
    events = process_events(events_parser.load_all_events())
    pretty_json_string = json.dumps(events, indent=4, sort_keys=True)
    print(pretty_json_string)
    print("Processed {0} events.".format(len(events)))
