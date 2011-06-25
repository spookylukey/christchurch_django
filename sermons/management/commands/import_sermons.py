"""
import_sermons command
"""
import os
import os.path

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand

from sermons.models import Sermon, SERMONS_PATH
from sermons.tags import set_attrs_from_filename, set_attrs_from_id3_tags

class Command(BaseCommand):

    def handle(self, *args, **options):
        from django.conf import settings
        sermon_dir = os.path.join(settings.MEDIA_ROOT, SERMONS_PATH)
        sermons = []
        errors = []
        topics = []
        for f in os.listdir(sermon_dir):
            if f.endswith('.mp3'):
                s = Sermon(sermon=os.path.join(SERMONS_PATH, f))
                # topics have to be set after saving, so they
                # are returned from set_attrs_from_id3_tags for later processing
                good_info, topics_to_add = set_attrs_from_id3_tags(s)
                if not good_info:
                    set_attrs_from_filename(s)
                    self.stderr.write("Falling back to filename for %s\n" % os.path.basename(f))
                try:
                    s.full_clean()
                    s.published = True
                    sermons.append(s)
                    topics.append(topics_to_add)
                except ValidationError as e:
                    errors.append("%s could not be imported due to missing/bad data for fields: %s" % (f, ','.join(e.message_dict.keys())))

        if len(errors) > 0:
            for e in errors:
                self.stderr.write(e + '\n')
        else:
            for s, ts in zip(sermons, topics):
                if Sermon.objects.filter(date_delivered=s.date_delivered, time_delivered=s.time_delivered, speaker__name=s.speaker.name).exists():
                    self.stderr.write("Skipping duplicate: %s\n" % os.path.basename(s.sermon.file.name))
                else:
                    s.save()
                    for t in ts:
                        s.topics.add(t)
