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
    
    current_time = datetime.now(tz)
    print(current_time)

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
    
        if event_start > current_time:
            e = lambda: None
            e.name = event.get('summary')
            e.start = event_start.replace(tzinfo=None)
            e.end = event_end.replace(tzinfo=None)
            ret.append(e)

    ret = sorted(ret, key=lambda x: x.start)

    return ret


def convert(target_date):
    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    difference = target_date.replace() - now
    days = difference.days
    seconds = difference.seconds

    ret = "+"
    ret += str(days)
    ret += "d, "
    if days < 1:
        ret += "today"
    elif days == 1:
        ret += "tmrw"
    else:
        ret += target_date.strftime('%a').capitalize()
    if target_date.strftime('%-H:%M') != "0:00":
        ret += ", " + target_date.strftime('%-H:%M') 
    # if days < 1:
    #     ret = f"today, {target_date.strftime('%-H:%M')}"
    # elif days == 1:
    #     ret = f"tmrw, {target_date.strftime('%-H:%M')}"
    # elif days < 7:
    #     ret = f"{target_date.strftime('%a').capitalize()}, {target_date.strftime('%-H:%M')}"
    # else:
    #     ret = "+" + str(days) + "d, " + target_date.strftime('%a, %-H:%M') 
    # if ret.endswith(" 0:00"):
    #     ret = ret[0:-6]
    return ret


if __name__ == "__main__":
    for e in get_events():
        print(f"Event: {e.name}")
        print(f"Start: {e.start}")
        print(f"Start (formatted): {convert(e.start)}")
        print(f"End: {e.end}")
