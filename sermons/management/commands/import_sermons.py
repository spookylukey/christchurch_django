"""
import_sermons command
"""
import os
import os.path

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand

from sermons.models import Sermon, SERMONS_PATH
from sermons.tags import set_attrs_from_filename

class Command(BaseCommand):

    def handle(self, *args, **options):
        from django.conf import settings
        sermon_dir = os.path.join(settings.MEDIA_ROOT, SERMONS_PATH)
        sermons = []
        errors = []
        for f in os.listdir(sermon_dir):
            if f.endswith('.mp3'):
                s = Sermon(sermon=os.path.join(SERMONS_PATH, f))
                set_attrs_from_filename(s)
                try:
                    s.full_clean()
                    s.published = True
                    sermons.append(s)
                except ValidationError as e:
                    errors.append("%s could not be imported due to missing/bad data for fields: %s" % (f, ','.join(e.message_dict.keys())))

        if len(errors) > 0:
            for e in errors:
                self.stderr.write(e + '\n')
        else:
            for s in sermons:
                if Sermon.objects.filter(date_delivered=s.date_delivered, time_delivered=s.time_delivered).exists():
                    self.stderr.write("Skipping duplicate: %s\n" % s.sermon.url)
                else:
                    self.stdout.write("Importing sermon:   %s\n" % s.sermon.url)
                    s.save()
