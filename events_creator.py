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
            flow.redirect_uri = "http://localhost"
            # --- ADD THIS SECTION FOR DEBUGGING ---
            # Get the authorization URL that will be used.
            # This will include the exact redirect_uri the library is constructing.
            auth_url, _ = flow.authorization_url(prompt='consent')
            print("-" * 80)
            print("DEBUG: The script will attempt to open this URL:")
            print(auth_url)
            import urllib.parse
            parsed_url = urllib.parse.urlparse(auth_url)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            if 'redirect_uri' in query_params:
                print(f"DEBUG: Extracted redirect_uri being sent: {query_params['redirect_uri'][0]}")
            else:
                print("DEBUG: 'redirect_uri' not found in the authorization URL query parameters (this is unexpected).")
            print("-" * 80)
            # --- END OF DEBUGGING SECTION ---
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

    # Optional: Clear existing events first if this calendar is ONLY for CBC
    # Be careful with this! Requires listing events and deleting them.

    print(f"Adding {len(events_to_add)} events to calendar '{CALENDAR_ID}'...")
    for event_body in events_to_add:
        try:
            event = service.events().insert(calendarId=CALENDAR_ID, body=event_body).execute()
            print(f"Event created: {event.get('htmlLink')}")
        except HttpError as error:
            print(f"An error occurred adding event '{event_body.get('summary')}': {error}")

if __name__ == '__main__':
    processed_events = events_processor.process_events(events_parser.load_all_events())
    if processed_events:
         service = get_calendar_service()
         #add_events_to_calendar(service, processed_events)
    else:
         print("No events found or processed.")