from datetime import datetime, timedelta
import os
import os.path
import random
import re

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.cache import patch_cache_control, add_never_cache_headers
import pytz
import requests
import vobject

from .calendar import search


PREACHING_ICAL = 'http://www.google.com/calendar/ical/c3kc8arf6hr51dh146dnsiq040%40group.calendar.google.com/public/basic.ics'
MIDWEEK_ICAL = 'https://www.google.com/calendar/ical/rd8ant2lkdackckjk587kfr68g%40group.calendar.google.com/public/basic.ics'
bad_dates = re.compile(r'CREATED:0000\d{4}T\d*Z\r\n')
local_timezone = pytz.timezone('Europe/London')


def get_calendar(url):
    data = requests.get(url).content
    # There is some bad CREATED data that vobject barfs on if we don't clean up.
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
            return cmp(self.start.date() if hasattr(self.start, 'date') else self.start,
                       other.start.date() if hasattr(other.start, 'date') else other.start)
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
        # Clock should 'tick over' to the next week at the end of Sunday,
        # not part way through, so truncate hour to zero.
        today = datetime.now(local_timezone).replace(hour=0)
        raw_events = search(cal, today, today + timedelta(7))
        events = [Event(vevent.summary.value, dt,
                        description=vevent.description.value
                        if hasattr(vevent, 'description') else None)
                  for (dt, vevent) in raw_events]
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
        raw_events = search(cal, today, today + timedelta(60))
        events = [Event(v.summary.value if hasattr(v, 'summary') else '',
                        startdate,
                        location=v.location.value if hasattr(v, 'location') else None,
                        description=v.description.value if hasattr(v, 'description') else None,
                        vevent=v,
                        ) for (startdate, v) in raw_events]
        events.sort()
        c['events'] = events
    else:
        c['message'] = "Calendar not available"

    return render(request, "christchurch/midweek.html", c)


# Photo cycler for front page.
# Getting it perfect is harder than it seems!
#
# == Constraints ==
#
# - we want users to get a set of random photos, which are cycled by javascript.
#
# - they should get a different set each visit
#
# - if javascript is turned off, only one image should be loaded, since only one
#   will be seen (and if CSS is missing, we don't want a bunch of photos
#   showing)
#
# - if the set of photos is to be fully random, then the first one must be, and
#   this one has to be random by a method that doesn't rely on javascript.
#
# - we don't want to make a custom view for the whole page i.e. want to be able
#   to do this just by including a snippet of HTML on the home page.
#
# - ideally we don't want to use an iframe, because that will delay the
#   appearance of the photo (requires an extra, serial HTTP request).
#
# - we want to avoid repeats within the set, especially repeating the same photo
#   twice in a row, which looks bad.
#
# - don't want to store anything in db, and don't have shared cache available
#
# - can't rely on per-process state in web server, because it can be
#   multi-process
#
# - to add new images, we want to just add them to the relevant directory,
#   so need some server-side code that will look in this dir.
#
# == Solution ==
#
# - initial image is hardcoded to src='/photochanger/'
#
# - this view:
#
#   - selects a set of photos at random, with no repeats.
#
#   - returns a redirect to the first one
#
#   - with a cookie that indicates the rest
#
#   - client side javascript can read the cookie
#     and do the rest.
#
#   - response is marked 'never cache' so they
#     get different one next time.

def photochanger(request):
    """
    Returns a redirect to a random photo in the slideshow
    """
    slideshow_dir = 'photos/slideshow'
    files = os.listdir(os.path.join(settings.MEDIA_ROOT, slideshow_dir))
    files = [f for f in files if f.endswith('.jpg')]

    chosen = []
    for i in range(0, 5):
        choice = random.choice(files)
        files.remove(choice)
        chosen.append(choice)

    response = HttpResponseRedirect(os.path.join(settings.MEDIA_URL, slideshow_dir,
                                                 chosen[0]))

    # filenames are short, so can store in a cookie
    response.set_cookie('photocycler', '|'.join(chosen[1:]))

    # We want the visitor to get different photos each time,
    # so we say "No really, don't cache this"
    add_never_cache_headers(response)
    patch_cache_control(response, no_cache=True)
    patch_cache_control(response, must_revalidate=True)
    return response
