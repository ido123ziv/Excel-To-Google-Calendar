from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import party
import json

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']


# explanation of the code:
"""
list longer than 15,
working in 15 days period
need to give value to each name
if name was last week it will get a low val
wasn't in the last period? will get a lot
all the others will get a medium score

the program will save in DB the last period
each new period the program will take the high values and randomly pick the mediums.
high 9
med 5
low 1
"""

# $$$$$$$$$$$$$$$$$$ Authenticate $$$$$$$$$$$$$$$$$$

creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

# create a calendar connection using cred
service = build('calendar', 'v3', credentials=creds)


# print the next 10 events in calendar
def printEvents():
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])


def create_event_in_calendar(name, date, email):
    text = "אל תשכח להתקשר ל" + name
    my_event = {
        'summary': name,
        'description': text,
        'start': {
            'date': date,
        },
        'end': {
            'date': date,
        },
        'attendees': [
            {'email': email}
        ]
    }

    # add event to calendar
    event = service.events().insert(calendarId='primary', body=my_event).execute()
    print('Event created: %s' % (event.get('htmlLink')))


with open('conf.json') as conf_file:
    conf = json.load(conf_file)
get_email = conf["service_email"]
events_list = party.main()



# add a notification to update the xlsx file
last = events_list[-1:][0]
up_date = datetime.datetime.strptime(last["date"], '%Y-%m-%d') + datetime.timedelta(days=2)
up_date = up_date.date().isoformat()
create_event_in_calendar("לעדכן את הרשימות", up_date, get_email)

printEvents()
"""
# example of an event
my_event = {
  'summary': 'שרון',
  'description': text,
  'start': {
    'date': tomorrow,
  },
  'end': {
    'date': tomorrow,
  },
  'colorID': c1,
  'attendees': [
    {'email': 'idoshziv@gmail.com'}
  ]
}



# add event to calendar
# event = service.events().insert(calendarId='primary', body=my_event).execute()
# print('Event created: %s' % (event.get('htmlLink')))

