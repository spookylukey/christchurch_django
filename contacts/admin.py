from django.contrib import admin

from .models import Contact, HomeGroup


CONTACT_VIEWER_GROUP_NAME = 'Contact viewers'

def is_contact_viewer(user):
    return user.groups.filter(name=CONTACT_VIEWER_GROUP_NAME).exists()

class ContactAdmin(admin.ModelAdmin):
    def address(obj):
        return ', '.join(obj.address.strip().split('\n'))
    list_display = ['name', address, 'post_code', 'phone_number', 'mobile_number', 'email', 'church_member', 'home_group']
    list_filter = ['church_member', 'home_group']

    # We allow some church people to view admin screens.  Some data is kept
    # private from them, therefore we are careful about list_display,
    # list_filter, fieldsets
    # TODO:
    # Once we move to Django 1.4, can define get_list_display
    # and conditionally add attributes not in church_public_attrs

    church_public_attrs = ['name', 'address', 'post_code', 'phone_number',
                           'mobile_number', 'email']

    def get_fieldsets(self, request, obj=None):
        if  is_contact_viewer(request.user):
           return [('', {'fields': self.church_public_attrs})]
        else:
            return super(ContactAdmin, self).get_fieldsets(request, obj=obj)

    def get_readonly_fields(self, request, obj=None):
        if is_contact_viewer(request.user):
            # All are readonly
            return [f.name for f in Contact._meta.fields if not f.primary_key]
        else:
            return super(ContactAdmin, self).get_readonly_fields(request, obj=obj)

class HomeGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'group_email']

admin.site.register(Contact, ContactAdmin)
admin.site.register(HomeGroup, HomeGroupAdmin)
