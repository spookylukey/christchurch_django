from django.conf import settings
from django.shortcuts import render
from django_easyfilters import FilterSet

from sermons.models import Sermon

class SermonFilterSet(FilterSet):
    fields = ['speaker']

def index(request):
    sermons = Sermon.objects.filter(published=True)
    sermonsfilter = SermonFilterSet(sermons, request.GET)
    return render(request, "sermons/index.html", {'sermonsfilter': sermonsfilter,
                                                  'sermons': sermonsfilter.qs})
