from django.conf import settings
from django.shortcuts import render

from sermons.models import Sermon

def index(request):
    sermons = Sermon.objects.filter(published=True)
    return render(request, "sermons/index.html", {'sermons': sermons})
