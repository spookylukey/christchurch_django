from django.contrib import admin

from .models import Contact, HomeGroup


class ContactAdmin(admin.ModelAdmin):
    def address(obj):
        lines = obj.address.split('\n')
        return lines[0] + u'...' if len(lines) > 1 else u''
    list_display = ['name', address, 'post_code', 'phone_number', 'mobile_number', 'email', 'church_member', 'home_group']
    list_filter = ['church_member', 'home_group']


class HomeGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'group_email']

admin.site.register(Contact, ContactAdmin)
admin.site.register(HomeGroup, HomeGroupAdmin)
