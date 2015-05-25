from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('sermons.views',
                       url(r'^read/(\d*)/', 'read', name='sermon_read'),
                       url(r'^$', 'index')
                       )
