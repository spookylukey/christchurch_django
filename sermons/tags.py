"""
Deals with reading/writing MP3 tags and metadata in sermon filename
"""
from datetime import date, time
import os
import re
import sys

from mutagen.id3 import ID3, TIT2, TDRC, TPE1, TIME, COMM

from sermons.models import BIBLE_BOOKS, BIBLE_NAME_TO_VAL, Speaker, Series, Topic


expected_filename_re = re.compile(ur'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2}) (?P<hour>\d{2})(?P<minute>\d{2}) (?P<speaker>[^-]+)( - (?P<title>.*))?\.mp3')


def set_attrs_from_filename(sermon):
    """
    Fills in the details that can be found from the filename
    """

    filename = os.path.basename(sermon.sermon.name)
    m_filename = expected_filename_re.match(filename)

    if m_filename is not None:
        d = m_filename.groupdict()
        sermon.date_delivered = date(int(d['year']), int(d['month']), int(d['day']))
        sermon.time_delivered = time(int(d['hour']), int(d['minute']))
        sermon.speaker = Speaker.objects.get_or_create(name=d['speaker'])[0]
        passage = None
        title = d['title']
        if title is None:
            title = ''

        # Now see if we can parse title to get passage info
        book = None
        poss_book = title.split(' ')[0]
        poss_book_2 = ' '.join(title.split(' ')[0:2])
        if poss_book in BIBLE_BOOKS:
            book = poss_book
        if poss_book_2 in BIBLE_BOOKS:
            book = poss_book_2

        if book is not None:
            # Assume 'title' is actually a passage
            passage = title
            title = ''
            sermon.bible_book = BIBLE_NAME_TO_VAL[book]
        elif ' - ' in title:
            title_part, passage_part = title.split(' - ', 1)

            poss_book = passage_part.split(' ')[0]
            poss_book_2 = ' '.join(passage_part.split(' ')[0:2])
            if poss_book in BIBLE_BOOKS:
                book = poss_book
            if poss_book_2 in BIBLE_BOOKS:
                book = poss_book_2
            if book is not None:
                title = title_part
                passage = passage_part
                sermon.bible_book = BIBLE_NAME_TO_VAL[book]

        sermon.title = title
        if passage is not None:
            sermon.passage = passage
        return True
    else:
        return False


def write_id3_tags(sermon):
    fname = sermon.sermon.file.name
    UTF8 = 3 # mutagen.id3 says so.
    tags = ID3(fname)
    tags.add(TIT2(encoding=UTF8, text=sermon.title))
    tags.add(TDRC(encoding=UTF8, text=
                  sermon.date_delivered.strftime('%Y-%m-%d') + ' ' +
                  sermon.time_delivered.strftime('%H:%M')))
    tags.add(TPE1(encoding=UTF8, text=sermon.speaker.name))
    if sermon.bible_book != '':
        tags.add(COMM(encoding=UTF8, lang='eng', desc='Sermon.bible_book', text=sermon.bible_book))
    if sermon.passage != '':
        tags.add(COMM(encoding=UTF8, lang='eng', desc='Sermon.passage', text=sermon.passage))
    if sermon.series is not None:
        tags.add(COMM(encoding=UTF8, lang='eng', desc='Sermon.series', text=sermon.series.name))
    topics = sermon.topics.all()
    if len(topics) > 0:
        tags.add(COMM(encoding=UTF8, lang='eng', desc='Sermon.topics', text=u','.join(
                    t.name for t in topics)))
    comment = ("""
Sermon:
 Speaker: %(speaker)s
 Bible book: %(bible_book)s
 Text: %(passage)s
 Series: %(series)s
 Topics: %(topics)s
""" % dict(speaker=sermon.speaker.name,
           bible_book=sermon.bible_book,
           passage=sermon.passage,
           series=sermon.series.name if sermon.series is not None else '',
           topics=', '.join(t.name for t in topics) if topics else ''))

    tags.add(COMM(encoding=UTF8, lang='eng', text=comment))
    tags.save()

def set_attrs_from_id3_tags(sermon):
    fname = sermon.sermon.file.name
    tags = ID3(fname)

    title = 'TIT2'
    date_delivered = 'TDRC'
    speaker = 'TPE1'
    bible_book = "COMM:Sermon.bible_book:'eng'"
    passage = "COMM:Sermon.passage:'eng'"
    series = "COMM:Sermon.series:'eng'"
    topics = "COMM:Sermon.topics:'eng'"

    has_time = False
    if title in tags:
        sermon.title = tags[title].text[0]
    if date_delivered in tags:
        timestamp = tags[date_delivered].text[0]
        if timestamp.year and timestamp.month and timestamp.day:
            sermon.date_delivered = date(timestamp.year, timestamp.month, timestamp.day)
        if timestamp.hour is not None and timestamp.minute is not None:
            has_time = True
            sermon.time_delivered = time(timestamp.hour, timestamp.minute)
    if speaker in tags:
        sermon.speaker = Speaker.objects.get_or_create(name=tags[speaker].text[0])[0]

    if bible_book in tags:
        sermon.bible_book = tags[bible_book].text[0]

    if passage in tags:
        sermon.passage = tags[passage].text[0]

    if series in tags:
        sermon.series = Series.objects.get_or_create(name=tags[series].text[0])[0]

    topics_to_add = []
    if topics in tags:
        for t in tags[topics].text[0].split(','):
            # Topics have to be added later, after saving
            topics_to_add.append(Topic.objects.get_or_create(name=t)[0])

    if has_time:
        # Obviously have done export to ID3, so ID3 has good info.
        good_info = True
    else:
        good_info = False
    return good_info, topics_to_add
