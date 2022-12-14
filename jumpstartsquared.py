from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import os
import requests
import bs4 as BeautifulSoup
import json
import datetime
import mysql.connector
from profanity_filter import ProfanityFilter

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'quotes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    quote = db.Column(db.Text)

    def __repr__(self):
        return f'<Quote {self.id}>'

@app.route('/')
def index():
    quotes = Quote.query.all()
    return render_template('index.html', quotes = quotes)

@app.route('/quotesubmit')
def graph():
    return render_template('quotesubmit.html')

@app.route('/quotemanager')
def manager():
    quotes = Quote.query.all()
    return render_template('quotemanager.html', quotes = quotes)

@app.route('/quoteeditor', methods=['GET', 'POST'])
def editor():
    if request.form:
        for id in request.form:
            Quote.query.filter(Quote.id == id).delete()
            db.session.commit()
            
        return "deleted"
    else:
        return "No values passed"

@app.route('/quotehandler', methods=['GET', 'POST'])
def handler():

    new_quote = Quote(name = request.form.get('user_name'), quote=request.form.get('user_message'))
    db.session.add(new_quote)
    db.session.commit()
    return request.form.get(text = request.form.get('user_message'))

@app.route('/quotedatabase')
def quotes():
    quotes = Quote.query.all()
    return render_template('quotedatabase.html', quotes=quotes)
    

@app.route('/calendar')
def calendar():
    # Get Calendar Data
    length_in_days = 7
    calendar = requests.get(f'https://clients6.google.com/calendar/v3/calendars/rti648k5hv7j3ae3a3rum8potk@group.calendar.google.com/events?calendarId=rti648k5hv7j3ae3a3rum8potk@group.calendar.google.com&singleEvents=true&timeZone=America/New_York&maxAttendees=1&maxResults=2500&sanitizeHtml=true&timeMin={(datetime.datetime.now() + datetime.timedelta(days=-1)).astimezone().replace(microsecond=0).isoformat()}&timeMax={(datetime.datetime.now() + datetime.timedelta(days=length_in_days)).astimezone().replace(microsecond=0).isoformat()}&key=AIzaSyBNlYH01_9Hc5S1J9vuFmu2nUqBZJNAXxs')
    calendar.raise_for_status()

    j_calendar = json.loads(calendar.text)

    def getDateGivenDict(itemDict):
        if 'date' not in itemDict:
            return [datetime.datetime.strptime(itemDict['dateTime'], '%Y-%m-%dT%H:%M:%S%z'), 0]
        else:
            return [datetime.datetime.strptime(itemDict['date'], '%Y-%m-%d'), 1]
    
    def getFormattedDateGivenDict(itemDict):
        if 'date' not in itemDict:
            return [datetime.datetime.strptime(itemDict['dateTime'], '%Y-%m-%dT%H:%M:%S%z').strftime('%#m/%#d/%Y at %#I:%M %p'), 0]
        else:
            return [datetime.datetime.strptime(itemDict['date'], '%Y-%m-%d').strftime('%#m/%#d/%Y'), 1]   

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