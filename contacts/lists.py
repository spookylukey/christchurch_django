from contacts.webfaction import webfaction_session


def update_home_group_lists(*args, **kwargs):
    from .models import HomeGroup

    s = webfaction_session()
    if s is None:
        # This happens during development
        return

    for hg in HomeGroup.objects.exclude(group_email=''):
        if hg.group_email != '':
            email_list = list(set([c.email for c in hg.contact_set.exclude(email='')]))
            s.update_email(hg.group_email, ', '.join(email_list))

