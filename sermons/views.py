from datetime import date, time
import os

from django.conf import settings
from django.shortcuts import render

class Sermon(object):
    def __init__(self, filename):
        # yyyy-mm-dd HHMM speaker - title.mp3
        stem = filename.rsplit(".", 1)[0]
        bits = stem.split(" ", 2)
        bits2 = bits[2].split("-", 1)
        self.date_preached = date(*map(int, bits[0].split("-")))
        self.time_preached = time(int(bits[1][0:2]), int(bits[1][2:4]))
        self.filename = filename
        self.speaker = bits2[0]
        self.title = bits2[1] if len(bits2) > 1 else ''

    def nice_time(self):
        if self.time_preached <= time(11):
            return "Morning service"
        elif self.time_preached >= time(17):
            return "Evening service"
        else:
            return "Afternoon service"

    @property
    def url(self):
        return settings.MEDIA_URL + "downloads/sermons/" + self.filename

    def __cmp__(self, other):
        c1 = cmp(self.date_preached, other.date_preached)
        if c1 != 0:
            # Descending by date
            return -c1
        else:
            # Then ascending by time
            return cmp(self.time_preached, other.time_preached)

def index(request):
    sermons = []
    for f in os.listdir(os.path.join(settings.MEDIA_ROOT, "downloads", "sermons")):
        if f.endswith(".mp3"):
            sermons.append(Sermon(f))

    sermons.sort()

    return render(request, "sermons/index.html", {'sermons': sermons})

