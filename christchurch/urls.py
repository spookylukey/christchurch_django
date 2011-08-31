from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^photochanger/$', 'christchurch.views.photochanger'),
                       url(r'^thissunday/$', 'christchurch.views.this_sunday'),
                       url(r'^upcoming-midweek/$', 'christchurch.views.upcoming_midweek'),
                       url(r'^semantic/', include('semanticeditor.urls')),

                       # Plug in the password reset views
                       (r'^admin/password_reset/$', 'django.contrib.auth.views.password_reset'),
                       (r'^admin/password_reset/done/$', 'django.contrib.auth.views.password_reset_done'),
                       (r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm'),
                       (r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete'),

                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^', include('cms.urls')),
                       # Sermons views included via apphooks
)

if settings.DEVBOX:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    # appmedia
    urlpatterns += patterns('',
                           (r'^' + settings.MEDIA_URL.lstrip('/'), include('appmedia.urls')),
    )

    # staticfiles and usermedia

    urlpatterns += patterns('',
                            (r'^usermedia/(?P<path>.*)$', 'django.views.static.serve',
                             {'document_root': settings.MEDIA_ROOT}),
    )

    urlpatterns += staticfiles_urlpatterns()
