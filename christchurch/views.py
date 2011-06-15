from datetime import datetime, timedelta
from dateutil import tz, rrule
import os
import os.path
import pytz
import random
import re

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.cache import patch_cache_control, add_never_cache_headers
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
    def __init__(self, summary, start, location=None, description=None, vevent=None):
        self.start = start
        self.summary = summary
        self.location = location
        self.description = description
        self.vevent = vevent # for debugging

    def nice_time(self):
        if not hasattr(self.start, 'time'):
            return ''
        if self.start.time().hour < 11:
            return "Morning"
        elif self.start.time().hour >= 17:
            return "Evening"
        else:
            return "Afternoon"

    def __cmp__(self, other):
        if type(self.start) != type(other.start):
            # Cope with 'date' objects by converting both to 'date'
            return cmp(self.start.date if hasattr(self.start, 'date') else self.start,
                       other.start.date if hasattr(other.start, 'date') else other.start)
        else:
            return cmp(self.start, other.start)

    def __repr__(self):
        return '<Event: %s, %s, location=%s, description=%s>' % (self.summary, self.start, self.location, self.description)

def this_sunday(request):
    try:
        cal = get_calendar(PREACHING_ICAL)
    except Exception:
        cal = None

    c = {}
    if cal is not None:
        events = []
        for vevent in cal.vevent_list:
            d = vevent.dtstart.value.astimezone(local_timezone)
            # Clock should 'tick over' to the next week at the end of Sunday,
            # not part way through, so truncate hour to zero
            today = datetime.now(local_timezone).replace(hour=0)
            if d > today and d < today + timedelta(7):
                events.append(Event(vevent.summary.value, d))
        events.sort()
        c['events'] = events
    else:
        c['message'] = "Calendar not available"

    return render(request, "christchurch/thissunday.html", c)


def upcoming_midweek(request):
    try:
        cal = get_calendar(MIDWEEK_ICAL)
    except Exception:
        cal = None

    c = {}
    if cal is not None:
        today = datetime.now(local_timezone).replace(hour=0)
        events = search(cal, today, today + timedelta(60))
        c['events'] = events
    else:
        c['message'] = "Calendar not available"

    return render(request, "christchurch/midweek.html", c)


def search(calendar, start_date, end_date):
    """
    Returns a list of events in calendar betweem the specified datetime objects,
    creating recurring events as necessary.
    """
    # First, do a pre run to get all the dates we nned to exclude,
    # i.e. those that have specific instances, identified by recurrence-id

    exclusions = []
    for v in calendar.vevent_list:
        rc = v.contents.get('recurrence-id', None)
        if rc is not None:
            # rc is a list, don't know if it can ever contain more than one
            # item, but we'll deal with that anyway.
            for d in rc:
                exclusions.append(d.value)

    events = []
    def mk_event(v, startdate):
        return Event(v.summary.value if hasattr(v, 'summary') else '',
                     startdate,
                     location=v.location.value if hasattr(v, 'location') else None,
                     description=v.description.value if hasattr(v, 'description') else None,
                     vevent=v,
                     )

    for v in calendar.vevent_list:
        if not hasattr(v, 'rrule'):
            # No recurrence, just look at dtstart
            dt = v.dtstart.value
            if not hasattr(dt, 'date'):
                # A 'date', not 'datetime'
                if dt >= start_date.date() and dt <= end_date.date():
                    events.append(mk_event(v, dt))
            else:
                if dt >= start_date and dt <= end_date:
                    events.append(mk_event(v, dt))
        else:
            ruleset = rrule.rruleset()
            rule = rrule.rrulestr(v.rrule.value, dtstart=v.dtstart.value)
            ruleset.rrule(rule)
            if hasattr(v, 'exdate_list'):
                for l in v.exdate_list:
                    for d in l.value:
                        ruleset.exdate(d)
            for d in exclusions:
                ruleset.exdate(d)
            events.extend([mk_event(v, ev_date)
                           for ev_date in ruleset.between(start_date, end_date)])

    events.sort()
    return events


def photochanger(request):
    """
    Returns a redirect to a random photo in the slideshow
    """
    slideshow_dir = 'photos/slideshow'
    files = os.listdir(os.path.join(settings.MEDIA_ROOT, slideshow_dir))
    files = [f for f in files if f.endswith('.jpg')]

    choice = random.choice(files)
    print choice
    response = HttpResponseRedirect(os.path.join(settings.MEDIA_URL, slideshow_dir,
                                                 choice))

    # We want the visitor to get different photos each time,
    # so we say "No really, don't cache this"
    add_never_cache_headers(response)
    patch_cache_control(response, no_cache=True)
    patch_cache_control(response, must_revalidate=True)
    return response
