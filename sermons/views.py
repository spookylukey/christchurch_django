from django.conf import settings
from django.shortcuts import render
from django_easyfilters import FilterSet, FilterOptions

from sermons.models import Sermon

class SermonFilterSet(FilterSet):
    fields = [
        ('speaker', FilterOptions(order_by_count=True)),
        'series',
        'topics',
        'bible_book',
        ]

def index(request):
    sermons = Sermon.objects.filter(published=True)
    sermonsfilter = SermonFilterSet(sermons, request.GET)
    return render(request, "sermons/index.html", {'sermons': sermonsfilter.qs,
                                                  'sermonsfilter': sermonsfilter})
