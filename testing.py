import requests
import bs4 as BeautifulSoup
import json
import datetime

calendar = requests.get('https://clients6.google.com/calendar/v3/calendars/rti648k5hv7j3ae3a3rum8potk@group.calendar.google.com/events?calendarId=rti648k5hv7j3ae3a3rum8potk%40group.calendar.google.com&singleEvents=true&timeZone=America%2FNew_York&maxAttendees=1&maxResults=250&sanitizeHtml=true&timeMin=2022-07-31T00%3A00%3A00-04%3A00&timeMax=2022-09-04T00%3A00%3A00-04%3A00&key=AIzaSyBNlYH01_9Hc5S1J9vuFmu2nUqBZJNAXxs')
calendar.raise_for_status()

j_calendar = json.loads(calendar.text)

def getDateGivenDict(itemDict):
    if 'date' not in itemDict:
        return datetime.datetime.strptime(itemDict['dateTime'], '%Y-%m-%dT%H:%M:%S%z')
    else:
        return datetime.datetime.strptime(itemDict['date'], '%Y-%m-%d')

def getDeltaDate(DateTime):
    first_time = datetime.datetime.now()
    later_time = DateTime.replace(tzinfo=None)

    return later_time - first_time

def formatDeltaDatetime(DateTime):
    delta_time_in_days = getDeltaDate(DateTime).days
    delta_time_in_hours = getDeltaDate(DateTime).total_seconds() // 3600
    delta_time_in_minutes = getDeltaDate(DateTime).total_seconds() // 60

    if delta_time_in_hours >= 48:
        return str(delta_time_in_days) + " days" + " from now"
    if delta_time_in_hours >= 24:
        return str(delta_time_in_days) + " day" + " from now"
    if delta_time_in_hours >= 2:
        return str(delta_time_in_hours) + " hours" + " from now"
    if delta_time_in_hours >= 1:
        return str(delta_time_in_hours) + " hour" + " from now"
    return str(int(delta_time_in_minutes)) + " minute(s)" + " from now"

events = []

for item in j_calendar['items']:
    events.append({
        "event_name": item['summary'],
        "event_start": getDateGivenDict(item['start']),
        "event_delta_formatted": formatDeltaDatetime(getDateGivenDict(item['start'])),
        "event_delta": getDeltaDate(getDateGivenDict(item['start']))

    })
    print(item['summary'])
    print(getDateGivenDict(item['start']))
    print(formatDeltaDatetime(getDateGivenDict(item['start'])))
    print(getDeltaDate(getDateGivenDict(item['start'])))


