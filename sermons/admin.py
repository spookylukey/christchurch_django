from django.contrib import admin

from sermons.models import Speaker, Topic, Series, Sermon


class SpeakerAdmin(admin.ModelAdmin):
    list_display = ['name']


class TopicAdmin(admin.ModelAdmin):
    list_display = ['name']


class SeriesAdmin(admin.ModelAdmin):
    list_display = ['name']


class SermonAdmin(admin.ModelAdmin):
    list_display = ['date_delivered', 'time_delivered', 'speaker', 'title', 'bible_book', 'passage', 'series', 'published']
    list_editable = ['title', 'bible_book', 'passage']
    list_filter = ['published', 'speaker', 'series']
    date_hierarchy = 'date_delivered'
    list_per_page = 200



admin.site.register(Speaker, SpeakerAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(Sermon, SermonAdmin)
