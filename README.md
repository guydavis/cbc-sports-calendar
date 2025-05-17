# cbc-sports-calendar
Python script that scrapes the CBC sports listing for a particular sport and generates a Google Calendar.
Source to scrape: https://www.cbc.ca/sports/streaming-schedule
Generated using Google Gemini Pro 2.5 in late April of 2025.

## Dev Setup

1. Install a recent Python, along with `pip`
1. `pip install --break-system-packages beautifulsoup4 google-api-python-client google-auth-httplib2 google-auth-oauthlib pytz`


## Google Calendar

Go to Google Calendar and create a new Calendar, just for Sports Events on CBC.  Then to interact with Google Calendar API:

1. Go to the Google Cloud Console.
1. Create a new project (or use an existing one).
1. Enable the "Google Calendar API".
1. Go to "Credentials", create "OAuth 2.0 Client ID", choose "Desktop app" (or "Web application" if running this server-side).
1. Download the credentials JSON file and save it as credentials.json in the same directory as your script.
1. Click the 'Audience' section and scroll to 'Test Users'.  Add your own email address as the only authorized user.
1. Authorize and Create Events: Use the Google API client library. The first time you run the script, it will open a browser window asking you to log in and grant permission. It will save a token.json file for future runs.

