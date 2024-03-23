import requests
from icalendar import Calendar
from urllib.parse import urlparse
from datetime import datetime, date, timedelta
from personal_data import family_calendar, anne_calendar
from pytz import timezone
from dateutil.rrule import rrulestr


def get_events(url=None):
    url_parts = urlparse(url)
    if url_parts.scheme == "webcal":
        http_url = f"https://{url_parts.netloc}{url_parts.path}"
    else:
        http_url = url
    
    response = requests.get(http_url)
    calendar_data = response.text
    
    cal = Calendar.from_ical(calendar_data)

    tz = timezone('Europe/Stockholm')
    
    current_time = datetime.now(tz)

    ret = list()
    
    for event in cal.walk('VEVENT'):
        event_start = event.get('dtstart').dt
    
        if isinstance(event_start, datetime):
            event_start = event_start.replace(tzinfo=tz)
        elif isinstance(event_start, date):
            event_start = datetime.combine(event_start, datetime.min.time(), tz)

        event_end = event.get('dtend').dt
    
        if isinstance(event_end, datetime):
            event_end = event_end.replace(tzinfo=tz)
        elif isinstance(event_end, date):
            event_end = datetime.combine(event_end, datetime.min.time(), tz)

        if 'RRULE' in event:
            # reoccuring event
            rule = rrulestr(event['RRULE'].to_ical().decode('utf-8'), dtstart=event_start)
            occurrences = rule.after(current_time)
            if occurrences is not None:
                e = lambda: None
                e.name = event.get('summary')
                e.name = e.name[0].capitalize() + e.name[1:]
                e.start = occurrences.replace(tzinfo=None)
                e.end = (occurrences + (event_end - event_start)).replace(tzinfo=None)

                counter = -1
                while occurrences is not None and counter <= 100:
                    counter += 1
                    occurrences = rule.after(occurrences)

                e.name += " (+" + str(counter) + ")"

                ret.append(e)
        else:
            # single event
            threshold = min(event_start.replace(hour=23, minute=59), event_end)
            threshold = threshold.replace(tzinfo=None)

            if current_time.replace(tzinfo=None) < threshold:
                e = lambda: None
                e.name = event.get('summary')
                e.name = e.name[0].capitalize() + e.name[1:]
                e.start = event_start.replace(tzinfo=None)
                e.end = event_end.replace(tzinfo=None)
                ret.append(e)

    ret = sorted(ret, key=lambda x: x.start)

    return ret


def convert(target_date):
    last_midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    difference = target_date.replace() - last_midnight
    days = difference.days
    seconds = difference.seconds

    ret = ""
    if days == 0:
        if int(target_date.strftime('%-H')) < 17:
            ret += "Today"
        else:
            ret += "Tonight"
    elif days == 1:
        ret += "Tomorrow"
    elif days < 7:
        ret += target_date.strftime('%a').capitalize()
        ret += " (+" + str(days) + ")"
    else:
        ret += target_date.strftime('%-m-%-d, ')
        ret += target_date.strftime('%a').capitalize()
        ret += " (+" + str(days) + ")"

    time = target_date.strftime('%-H:%M')
    if time != "0:00":
        ret += ", " + time 

    if 22 < len(ret):
        ret = ret[:-3]

    return ret


def shifts(nof_days=8):
    current_date = datetime.now()
    list_dates = []
    list_dates.append(current_date.replace(hour=0, minute=0, second=0, microsecond=0))
    for _ in range(nof_days - 1):
        current_date += timedelta(days=1)
        list_dates.append(current_date.replace(hour=0, minute=0, second=0, microsecond=0))

    events = get_events(anne_calendar)
    list_shifts = list()
    for d in list_dates:
        for j in events:
            if j.start == d:
                list_shifts.append(j.name[0].upper())
                break
        else:
            list_shifts.append("L")

    return list_shifts


def print_events(events):
    max_start_length = max(len(convert(e.start)) for e in events)
    for e in events:
        start = convert(e.start)
        padding = " " * (max_start_length - len(start))
        print(start + ":" + padding + " " + e.name)


if __name__ == "__main__":
    print_events(get_events(family_calendar))
    print("")
    print_events(get_events(anne_calendar))
    print("")
    print(shifts())
