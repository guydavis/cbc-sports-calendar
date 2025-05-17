import events_parser
import events_processor 
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']
# Consider creating a dedicated calendar in Google Calendar first and using its ID
CALENDAR_ID = 'c200ba2ea12eac34b7fa0170adeb988cc5d56841f1bcd218561d35d7eae73ea0@group.calendar.google.com' 

def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        service = build('calendar', 'v3', credentials=creds)
        return service
    except HttpError as error:
        print(f'An error occurred building the service: {error}')
        return None

def add_events_to_calendar(service, events_to_add):
    if not service:
        print("Calendar service not available.")
        return

    print(f"Target calendar: '{CALENDAR_ID}'")
    # 1. List all existing events in the calendar
    print("Fetching existing events to delete...")
    all_event_ids = []
    page_token = None
    while True:
        try:
            events_result = service.events().list(
                calendarId=CALENDAR_ID,
                pageToken=page_token,
                singleEvents=False # Get single events and master recurring events
            ).execute()
            
            current_events = events_result.get('items', [])
            for event_item in current_events:
                all_event_ids.append(event_item['id'])
            
            page_token = events_result.get('nextPageToken')
            if not page_token:
                break
        except HttpError as error:
            print(f"An error occurred while listing events: {error}")
            return # Stop if we can't list events

    if not all_event_ids:
        print("No existing events found to delete.")
    else:
        print(f"Found {len(all_event_ids)} events to delete. Deleting now...")
        deleted_count = 0
        for event_id in all_event_ids:
            try:
                service.events().delete(
                    calendarId=CALENDAR_ID,
                    eventId=event_id
                ).execute()
                deleted_count += 1
                # Optional: print a dot for progress
                print(".", end="", flush=True)
            except HttpError as error:
                print(f"\nAn error occurred deleting event ID {event_id}: {error}")
                # Decide if you want to continue deleting other events or stop
        print(f"\nSuccessfully deleted {deleted_count} out of {len(all_event_ids)} events.")

    # 3. Add the new events (your existing logic)
    if not events_to_add:
        print("No new events to add.")
        return
        
    print(f"\nAdding {len(events_to_add)} new events to calendar '{CALENDAR_ID}'...")
    added_count = 0
    for event_body in events_to_add:
        try:
            event = service.events().insert(
                calendarId=CALENDAR_ID,
                body=event_body
            ).execute()
            print(f"Event created: {event.get('summary')} - {event.get('htmlLink')}")
            added_count +=1
        except HttpError as error:
            print(f"An error occurred adding event '{event_body.get('summary')}': {error}")
    print(f"Successfully added {added_count} new events.")

if __name__ == '__main__':
    processed_events = events_processor.process_events(events_parser.load_all_events())
    if processed_events:
        service = get_calendar_service()
        add_events_to_calendar(service, processed_events)
        print("Created {0} events.".format(len(processed_events)))
    else:
        print("No events found or processed.")