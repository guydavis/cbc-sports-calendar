import requests
import traceback

from bs4 import BeautifulSoup

URL = "https://www.cbc.ca/sports/streaming-schedule?sport="
SPORTS = ['Volleyball', 'Volleyball-Beach'] # Check CBC page, drop-down chooser, to get the list of Sports
headers = {'User-Agent': 'Mozilla/5.0'} # Pretend to be a browser

def load_events(sport):
    response = requests.get("{0}{1}".format(URL, sport), headers=headers)
    response.raise_for_status() # Raise an error for bad status codes (4xx or 5xx)
    soup = BeautifulSoup(response.text, 'html.parser')

    # --- Scraping Logic ---
    # This is highly dependent on the HTML structure found in Step 1.
    # Example (Conceptual - you MUST adapt this based on inspection):
    events = []
    schedule = soup.find('div', attrs={'data-cy': 'olympicsBroadcastSchedule'}) 
    for event in schedule.find_all('tr'):
        try:
            if 'class' in event.attrs and 'a11y' in event.attrs['class']: 
                #print("Skipping {0}".format(event))
                continue # skip header table row
        except:
            traceback.print_exc()
        try:
            start_date = event.find('th', attrs={'data-cy': 'status'}).text.strip() 
            #print(start_date)
        except:
            print("Failed on start_date with {0}".format(event))
            continue
        try:
            start = event.find('td', attrs={'data-cy': 'startTime'})
            #print(start)
        except:
            print("Failed on start with {0}".format(start))
            continue
        try:
            start_time = start.find(string=True, recursive=False)
            #print(start_time)
        except:
            print("Failed on time with {0}".format(start))
        try:
            title = event.find('td', attrs={'data-cy': 'title'}).text.strip()
            #print(title)
        except: 
            print("Failed on title {0}".format(event))
        events.append({
            'title': title,
            'date_str': start_date,
            'time_str': start_time,
        })
    return events

def load_all_events():
    events = []
    for sport in SPORTS:
        events.extend(load_events(sport))
    return events

if __name__ == '__main__': # testing only
    print(load_all_events()) # For debugging
