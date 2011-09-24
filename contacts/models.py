from django.db import models


class HomeGroup(models.Model):
    name = models.CharField(max_length=100)
    group_email = models.EmailField(blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']


class ContactManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        return super(ContactManager, self).get_query_set().select_related('home_group')


class Contact(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    post_code = models.CharField(max_length=10, blank=True)
    phone_number = models.CharField(max_length=22, blank=True)
    mobile_number = models.CharField(max_length=22, blank=True)
    email = models.EmailField(blank=True)
    home_group = models.ForeignKey(HomeGroup, null=True, blank=True)
    church_member = models.BooleanField()
    include_on_email_lists = models.BooleanField(default=True)

    objects = ContactManager()

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']


# Signals:
from django.db.models.signals import post_save
from .lists import update_home_group_lists

post_save.connect(update_home_group_lists, sender=Contact)
