"""
write_ID3_tags command.
"""
from django.core.management.base import BaseCommand

from sermons.models import Sermon
from sermons.tags import write_id3_tags

class Command(BaseCommand):

    def handle(self, *args, **options):
        for sermon in Sermon.objects.all():
            write_id3_tags(sermon)
