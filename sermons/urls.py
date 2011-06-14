from django.conf.urls.defaults import patterns, url
from django.views.generic.base import TemplateView

urlpatterns = patterns('sermons.views',
                       url(r'^$', 'index')
                       )
