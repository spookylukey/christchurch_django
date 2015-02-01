from django.shortcuts import render
from django_easyfilters import FilterSet

from sermons.models import Sermon

class SermonFilterSet(FilterSet):
    fields = [
        ('speaker', dict(order_by_count=True)),
        'bible_book',
        ('date_delivered', dict(max_links=6,
                                max_depth='month')),
        'series',
        ]

    title_fields = [
        'speaker',
        'bible_book',
        ]


def index(request):
    sermons = Sermon.objects.filter(published=True).select_related('series', 'speaker').order_by('-date_delivered', '-time_delivered')
    sermonsfilter = SermonFilterSet(sermons, request.GET)
    return render(request, "sermons/index.html", {'sermons': sermonsfilter.qs,
                                                  'sermonsfilter': sermonsfilter})
