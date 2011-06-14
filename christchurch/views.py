from datetime import datetime, timedelta
from dateutil import tz
import pytz
import re

from django.shortcuts import render
import requests
import vobject


PREACHING_ICAL = 'http://www.google.com/calendar/ical/c3kc8arf6hr51dh146dnsiq040%40group.calendar.google.com/public/basic.ics'

MIDWEEK_ICAL = 'https://www.google.com/calendar/ical/rd8ant2lkdackckjk587kfr68g%40group.calendar.google.com/public/basic.ics'
# Some bad data like this
bad_dates = re.compile(r'CREATED:0000\d{4}T\d*Z\r\n')

local_timezone = pytz.timezone('Europe/London')

def get_calendar(url):
    data = requests.get(url).content
    data = bad_dates.sub('', data)
    return vobject.readOne(data)


class Event(object):
    def __init__(self, start, speaker):
        self.start = start
        self.speaker = speaker

    def nice_time(self):
        if self.start.hour < 11:
            return "Morning"
        elif self.start.hour >= 17:
            return "Evening"
        else:
            return "Afternoon"

    def __cmp__(self, other):
        return cmp(self.start, other.start)

def this_sunday(request):
    try:
        cal = get_calendar(PREACHING_ICAL)
    except Exception:
        cal = None

    c = {}
    if cal is not None:
        events = []
        for vevent in cal.vevent_list:
            d = vevent.dtstart.value
            if d.tzinfo is None:
                d = d.replace(tzinfo=tz.tzutc())

            d = d.astimezone(local_timezone)
            # Clock should 'tick over' to the next week at the end of Sunday,
            # not part way through, so truncate hour to zero
            today = datetime.now(local_timezone).replace(hour=0)
            if d > today and d < today + timedelta(7):
                events.append(Event(d, vevent.summary.value))
        events.sort()
        c['events'] = events
    else:
        c['message'] = "Calendar not available"

    return render(request, "christchurch/thissunday.html", c)


