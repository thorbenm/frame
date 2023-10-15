import requests
from icalendar import Calendar
from urllib.parse import urlparse
from datetime import datetime, timedelta, date
from personal_data import webcal_url
from pytz import timezone


def get_events():
    url_parts = urlparse(webcal_url)
    if url_parts.scheme == "webcal":
        http_url = f"https://{url_parts.netloc}{url_parts.path}"
    else:
        http_url = webcal_url
    
    response = requests.get(http_url)
    calendar_data = response.text
    
    cal = Calendar.from_ical(calendar_data)

    tz = timezone('Europe/Stockholm')
    
    current_time = datetime.now(tz).replace(tzinfo=None)

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

        threshold = min(event_start.replace(hour=23, minute=59), event_end)
        threshold = threshold.replace(tzinfo=None)
    
        if current_time < threshold:
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

    return ret


if __name__ == "__main__":
    events = get_events()
    max_start_length = max(len(convert(e.start)) for e in events)

    for e in events:
        start = convert(e.start)
        padding = " " * (max_start_length - len(start))
        print(start + ":" + padding + " " + e.name)

