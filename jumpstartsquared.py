from flask import Flask, render_template, request
import requests
import bs4 as BeautifulSoup
import json
import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/graph')
def graph():
    return "NYI"
    
@app.route('/calendar')
def calendar():
    # Get Calendar Data
    calendar = requests.get('https://clients6.google.com/calendar/v3/calendars/rti648k5hv7j3ae3a3rum8potk@group.calendar.google.com/events?calendarId=rti648k5hv7j3ae3a3rum8potk%40group.calendar.google.com&singleEvents=true&timeZone=America%2FNew_York&maxAttendees=1&maxResults=250&sanitizeHtml=true&timeMin=2022-07-31T00%3A00%3A00-04%3A00&timeMax=2022-09-04T00%3A00%3A00-04%3A00&key=AIzaSyBNlYH01_9Hc5S1J9vuFmu2nUqBZJNAXxs')
    calendar.raise_for_status()

    j_calendar = json.loads(calendar.text)

    def getDateGivenDict(itemDict):
        if 'date' not in itemDict:
            return [datetime.datetime.strptime(itemDict['dateTime'], '%Y-%m-%dT%H:%M:%S%z'), 0]
        else:
            return [datetime.datetime.strptime(itemDict['date'], '%Y-%m-%d'), 1]
    
    def getFormattedDateGivenDict(itemDict):
        if 'date' not in itemDict:
            return [datetime.datetime.strptime(itemDict['dateTime'], '%Y-%m-%dT%H:%M:%S%z').strftime('%m/%d/%Y at %I:%M %p'), 0]
        else:
            return [datetime.datetime.strptime(itemDict['date'], '%Y-%m-%d').strftime('%m/%d/%Y'), 1]   

    def getDeltaDate(DateTime):
        first_time = datetime.datetime.now()
        later_time = DateTime[0].replace(tzinfo=None)

        return later_time - first_time
        

    def formatDeltaDatetime(DateTime):
        delta_time_in_days = getDeltaDate(DateTime).days
        delta_time_in_hours = getDeltaDate(DateTime).total_seconds() // 3600
        delta_time_in_minutes = getDeltaDate(DateTime).total_seconds() // 60

        if DateTime[1] == 0:
            if delta_time_in_hours >= 48:
                return str(delta_time_in_days) + " days" + " from now"
            if delta_time_in_hours >= 24:
                return str(delta_time_in_days) + " day" + " from now"
            if delta_time_in_hours >= 2:
                return str(int(delta_time_in_hours)) + " hours" + " from now"
            if delta_time_in_hours >= 1:
                return str(int(delta_time_in_hours)) + " hour" + " from now"
            return str(int(delta_time_in_minutes)) + " minute(s)" + " from now"

        if delta_time_in_hours > 24:
            return str(delta_time_in_days) + " days" + " from now"
        if delta_time_in_hours > 0:
            return "Tomorrow"
        return "Today"

    events = []

    for item in j_calendar['items']:
        if getDeltaDate(getDateGivenDict(item['start'])).total_seconds() > 0 or (getDateGivenDict(item['start'])[1] == 1 and getDeltaDate(getDateGivenDict(item['start'])).total_seconds() > 86399) :
            events.append({
                "event_name": item['summary'],
                "event_start": getFormattedDateGivenDict(item['start'])[0],
                "event_delta_formatted": formatDeltaDatetime(getDateGivenDict(item['start'])),
                "event_delta": getDeltaDate(getDateGivenDict(item['start'])),
                "event_delta_seconds": getDeltaDate(getDateGivenDict(item['start'])).total_seconds()
            })
    
    events.sort(key = lambda e: e['event_delta_seconds'])

    events_html_string = ""

    for event in events:
        events_html_string += f"""<div class="news-ticker-event"><p class="news-ticker-event-name">{event['event_name']}</p><p class="news-ticker-event-time">{event['event_start']}</p><p class="news-ticker-event-time-delta">{event['event_delta_formatted']}</p></div>"""

    events_html_string = events_html_string * 4
    return {"data": events_html_string}

app.run(host="0.0.0.0", port='5000')