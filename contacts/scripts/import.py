#!/usr/bin/env python
from __future__ import print_function

import os
import sys
import re

from contacts.models import Contact

def parse(data):
    # One-off parsing function, for data in a simple text file with double
    # line separating contacts.
    groups = data.split('\n\n')
    items = []
    for g in groups:
        item = {}
        lines = g.strip().split('\n')
        # Name is always first
        item['name'] = lines[0]
        lines.pop(0)
        for i, l in reversed(list(enumerate(lines))):
            if '@' in l:
                item['email'] = l
                lines.pop(i)
            elif l.startswith('01'):
                item['phone_number'] = l
                lines.pop(i)
            elif l.startswith('07'):
                item['mobile_number'] = l
                lines.pop(i)
            elif re.match(r'^(BD|LS|LE)\d+ .*', l):
                item['post_code'] = l.strip().strip('.')
                lines.pop(i)
        if len(lines) > 1:
            print('\n'.join(lines))
            print(g)
            sys.exit()

        elif len(lines) == 1:
            item['address'] = lines[0].replace(', ', '\n').replace(',', '\n')
        items.append(item)
    return items


def import_data(data):
    Contact.objects.all().delete()
    items = parse(data)
    for item in items:
        c = Contact(name=item['name'],
                    address=item.get('address', ''),
                    post_code=item.get('post_code', ''),
                    phone_number=item.get('phone_number', ''),
                    mobile_number=item.get('mobile_number', ''),
                    email=item.get('email', ''),
                    church_member=False)
        c.save()


if __name__ == '__main__':
    import_data(sys.stdin.read())
