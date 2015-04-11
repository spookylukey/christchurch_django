#!/usr/bin/env python

from __future__ import unicode_literals
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'christchurch.settings'

import csv


writer = csv.writer(open("contact-list.csv", "w"))

writer.writerow(["First Name", "Last Name", "Gender (M/F)", "Student (Y/N)", "Address", "Email Address", "Phone Number", "Mobile", "Photo File Name", "Home Group", "Username", "Password", "Admin User (Y/N)", "Church member", "Include on email lists"])


from django.contrib.auth.models import User
from contacts.models import Contact

admins = {u.email: u for u in User.objects.all().filter(is_staff=True)}

for contact in Contact.objects.all():
    try:
        first_name, last_name = contact.name.split(' ', 2)
    except ValueError:
        first_name, last_name = contact.name, ""
    writer.writerow([
        first_name,
        last_name,
        "",
        "N",
        contact.address.strip() + "\n" + contact.post_code,
        contact.email,
        contact.phone_number,
        contact.mobile_number,
        "",
        contact.home_group.name if contact.home_group else "",
        admins[contact.email].username if contact.email in admins else "",
        "",
        "Y" if contact.email in admins else "N",
        "Y" if contact.church_member else "N",
        "Y" if contact.include_on_email_lists else "N",
    ])
