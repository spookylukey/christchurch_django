from datetime import date, time
import os
import re

from django.db import models

BIBLE_BOOKS = ['Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy', 'Joshua', 'Judges', 'Ruth', '1 Samuel', '2 Samuel', '1 Kings', '2 Kings', '1 Chronicles', '2 Chronicles', 'Ezra', 'Nehemiah', 'Esther', 'Job', 'Psalm', 'Proverbs', 'Ecclesiastes', 'Song of Solomon', 'Isaiah', 'Jeremiah', 'Lamentations', 'Ezekiel', 'Daniel', 'Hosea', 'Joel', 'Amos', 'Obadiah', 'Jonah', 'Micah', 'Nahum', 'Habakkuk', 'Zephaniah', 'Haggai', 'Zechariah', 'Malachi', 'Matthew', 'Mark', 'Luke', 'John', 'Acts', 'Romans', '1 Corinthians', '2 Corinthians', 'Galatians', 'Ephesians', 'Philippians', 'Colossians', '1 Thessalonians', '2 Thessalonians', '1 Timothy', '2 Timothy', 'Titus', 'Philemon', 'Hebrews', 'James', '1 Peter', '2 Peter', '1 John', '2 John', '3 John', 'Jude', 'Revelation']
BIBLE_BOOKS_CHOICES = [('', '(Unspecified)')] + [(b,b) for b in BIBLE_BOOKS]
SERMONS_PATH = 'downloads/sermons/'
expected_filename_re = re.compile(ur'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2}) (?P<hour>\d{2})(?P<minute>\d{2}) (?P<speaker>[^-]+)( - (?P<title>.*))?\.mp3')


class Speaker(models.Model):
    name = models.CharField(max_length=255, db_index=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Topic(models.Model):
    name = models.CharField(max_length=255, db_index=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Series(models.Model):
    name = models.CharField(max_length=255, db_index=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'serieses'


class SermonManager(models.Manager):
    def get_query_set(self, *args, **kwargs):
        return super(SermonManager, self).get_query_set(*args, **kwargs).select_related('speaker')


class Sermon(models.Model):
    sermon = models.FileField(upload_to=SERMONS_PATH, max_length=255)
    speaker = models.ForeignKey(Speaker)
    title = models.CharField(max_length=255, blank=True)
    bible_book = models.CharField(max_length=20, choices=BIBLE_BOOKS_CHOICES, blank=True)
    passage = models.CharField(max_length=255, blank=True)
    topics = models.ManyToManyField(Topic, blank=True)
    series = models.ForeignKey(Series, null=True, blank=True)
    date_delivered = models.DateField(db_index=True)
    time_delivered = models.TimeField(db_index=True)
    published = models.BooleanField()

    objects = SermonManager()


    def nice_time(self):
        t = self.time_delivered
        if t <= time(11):
            return "Morning service"
        elif t >= time(17):
            return "Evening service"
        else:
            return "Afternoon service"

    def nice_passage(self):
        return self.passage if self.passage else self.bible_book

    def load_attrs_from_filename(self):
        """
        Fills in the details that can be found from the filename
        """

        filename = os.path.basename(self.sermon.name)
        m_filename = expected_filename_re.match(filename)

        if m_filename is not None:
            d = m_filename.groupdict()
            self.date_delivered = date(int(d['year']), int(d['month']), int(d['day']))
            self.time_delivered = time(int(d['hour']), int(d['minute']))
            self.speaker = Speaker.objects.get_or_create(name=d['speaker'])[0]
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
                self.bible_book = book
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
                    self.bible_book = book

            self.title = title
            if passage is not None:
                self.passage = passage
            return True
        else:
            return False


    def __unicode__(self):
        return "%s - %s" % (self.speaker.name, self.title)

    class Meta:
        ordering = ['-date_delivered', 'time_delivered']
