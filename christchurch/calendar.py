from dateutil import rrule


def search(calendar, start_date, end_date):
    """
    Searches a vobject calendar for events between the specified datetime objects,
    hanlding recurring events as necessary.

    Returns a list of 2 tuples containing (datetime/date of event, vevent object)
    """
    # First, do a pre run to get all the dates we nned to exclude,
    # i.e. those that have specific instances, identified by recurrence-id

    exclusions = []
    for v in calendar.vevent_list:
        rc = v.contents.get('recurrence-id', None)
        if rc is not None:
            # rc is a list, don't know if it can ever contain more than one
            # item, but we'll deal with that anyway.
            for d in rc:
                exclusions.append(d.value)

    events = []
    for v in calendar.vevent_list:
        if not hasattr(v, 'rrule'):
            # No recurrence, just look at dtstart
            dt = v.dtstart.value
            if not hasattr(dt, 'date'):
                # A 'date', not 'datetime', can't compare to timezone aware
                # 'datetime'
                if dt >= start_date.date() and dt <= end_date.date():
                    events.append((dt, v))
            else:
                if dt >= start_date and dt <= end_date:
                    events.append((dt, v))
        else:
            ruleset = rrule.rruleset()
            rule = rrule.rrulestr(v.rrule.value, dtstart=v.dtstart.value)
            ruleset.rrule(rule)
            if hasattr(v, 'exdate_list'):
                for l in v.exdate_list:
                    for d in l.value:
                        ruleset.exdate(d)
            for d in exclusions:
                ruleset.exdate(d)
            events.extend([(dt, v)
                           for dt in ruleset.between(start_date, end_date)])

    return events
