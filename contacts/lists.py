from contacts.webfaction import webfaction_session


def update_home_group_lists(*args, **kwargs):
    from .models import HomeGroup, Contact
    if kwargs.get('raw', False):
        return # don't do this for fixture loading

    s = webfaction_session()
    if s is None:
        # This happens during development
        return

    webfaction_email_list = [d['email_address'] for d in s.list_emails()]

    for hg in HomeGroup.objects.exclude(group_email=''):
        if hg.group_email != '':
            email_list = list(set([c.email for c in hg.contact_set.exclude(email='',
                                                                           include_on_email_lists=False)]))
            email_list_s = ', '.join(email_list)
            if hg.group_email in webfaction_email_list:
                # Update:
                s.update_email(hg.group_email, email_list_s)
            else:
                # Create new
                s.create_email(hg.group_email, email_list_s)

    # Lists for all church members and all contacts
    contacts = []
    members = []
    for c in Contact.objects.exclude(email='',
                                     include_on_email_lists=False):
        if c.church_member:
            members.append(c.email)
        contacts.append(c.email)

    s.update_email('church-contacts@christchurchbradford.org.uk', ', '.join(contacts))
    s.update_email('church-members@christchurchbradford.org.uk', ', '.join(members))

