"""
Deals with reading/writing MP3 tags and metadata in sermon filename
"""
from datetime import date, time
import os
import re

from sermons.models import BIBLE_BOOKS, BIBLE_NAME_TO_VAL, Speaker


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

