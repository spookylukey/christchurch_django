#!/usr/bin/env python

from __future__ import unicode_literals
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'christchurch.settings'

import csv

from sermons.models import Sermon


writer = csv.writer(file("talks.csv", "w"))

writer.writerow(["Series Name", "Talk Title", "Speaker", "Date (DD/MM/YYYY)", "Description",
                 "File Name", "Bible Passage", "Bible Book", "MP3 url"])
# Revelation - Jesus Unveiled,The Perfect Kingdom,Rev Bloggs,30/01/2015,Evening Service,rev-21.mp3,Revelation 21:1-10; Revelation 22:1-5,Revelation

for sermon in Sermon.objects.all().select_related('speaker', 'series').order_by('date_delivered'):
    series = sermon.series
    if series is not None:
        series = series.name
    else:
        series = ""
    description = sermon.nice_time()
    if description in ['Morning', 'Evening']:
        description = description + " Service"
    book = sermon.get_bible_book_display()

    writer.writerow([series, sermon.title, sermon.speaker.name, sermon.date_delivered.strftime('%d/%m/%Y'), description,
                     sermon.sermon.name.rsplit('/')[-1] if sermon.sermon is not None else '',
                     sermon.passage,
                     book if book != "(Unspecified)" else "",
                     ("http://www.christchurchbradford.org.uk" + sermon.sermon.url) if sermon.sermon else "",
                     ])
