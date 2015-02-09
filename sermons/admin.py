from functools import partial

from django.contrib import admin
from django.forms.models import modelform_factory

from sermons.models import Speaker, Topic, Series, Sermon


class SpeakerAdmin(admin.ModelAdmin):
    list_display = ['name']


class TopicAdmin(admin.ModelAdmin):
    list_display = ['name']


class SeriesAdmin(admin.ModelAdmin):
    list_display = ['name']


class SermonAdmin(admin.ModelAdmin):
    list_display = ['date_delivered', 'time_delivered', 'speaker', 'title', 'bible_book', 'passage', 'series', 'published']
    list_filter = ['published', 'speaker', 'series']
    date_hierarchy = 'date_delivered'
    list_per_page = 200

    def get_form(self, request, obj=None, **kwargs):
        if obj is None and not "no_mp3" in request.GET:
            # For add view, we have a simplified form that just has an upload field.
            return modelform_factory(self.model,
                                     fields=["sermon"],
                                     formfield_callback=partial(self.formfield_for_dbfield, request=request),)
        else:
            return super(SermonAdmin, self).get_form(request, obj=obj, **kwargs)

    def save_model(self, request, obj, form, change):
        if obj.pk is None:
            from sermons.tags import set_attrs_from_filename
            set_attrs_from_filename(obj)
            obj.save()
        else:
            from sermons.tags import write_id3_tags
            obj.save()
            write_id3_tags(obj)


admin.site.register(Speaker, SpeakerAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(Sermon, SermonAdmin)
