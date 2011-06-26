from datetime import date, time

from django.db import models

BIBLE_BOOKS = ['Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy', 'Joshua', 'Judges', 'Ruth', '1 Samuel', '2 Samuel', '1 Kings', '2 Kings', '1 Chronicles', '2 Chronicles', 'Ezra', 'Nehemiah', 'Esther', 'Job', 'Psalms', 'Proverbs', 'Ecclesiastes', 'Song of Solomon', 'Isaiah', 'Jeremiah', 'Lamentations', 'Ezekiel', 'Daniel', 'Hosea', 'Joel', 'Amos', 'Obadiah', 'Jonah', 'Micah', 'Nahum', 'Habakkuk', 'Zephaniah', 'Haggai', 'Zechariah', 'Malachi', 'Matthew', 'Mark', 'Luke', 'John', 'Acts', 'Romans', '1 Corinthians', '2 Corinthians', 'Galatians', 'Ephesians', 'Philippians', 'Colossians', '1 Thessalonians', '2 Thessalonians', '1 Timothy', '2 Timothy', 'Titus', 'Philemon', 'Hebrews', 'James', '1 Peter', '2 Peter', '1 John', '2 John', '3 John', 'Jude', 'Revelation']
BIBLE_BOOKS_CHOICES = [('', '(Unspecified)')] + [(b.replace(' ',''), b) for b in BIBLE_BOOKS]
# From book name to choice val:
BIBLE_NAME_TO_VAL = dict([(b[1], b[0]) for b in BIBLE_BOOKS_CHOICES])
SERMONS_PATH = 'downloads/sermons/'


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
        return super(SermonManager, self).get_query_set(*args, **kwargs).select_related('speaker', 'series')


class Sermon(models.Model):
    sermon = models.FileField(upload_to=SERMONS_PATH, max_length=255,
                              help_text="""The file name must be in the form:<br/>
&nbsp;&nbsp;<code>YYYY-MM-DD HHmm Speaker Name - Title - Passage.mp3</code><br/>
For example:<br/>
&nbsp;&nbsp;<code>2011-06-26 1700 Joe Bloggs - In the beginning - Genesis 1v1-2.mp3</code><br/>
<br/>
Title and Passage are optional.
""")
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

    def __unicode__(self):
        return "%s - %s" % (self.speaker.name, self.title)

    class Meta:
        ordering = ['-date_delivered', 'time_delivered']
