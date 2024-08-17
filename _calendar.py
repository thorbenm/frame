import requests
from icalendar import Calendar
from urllib.parse import urlparse
from datetime import datetime, date, timedelta
from pytz import timezone
from dateutil.rrule import rrulestr, rruleset
import json
import hashlib
import os


def __force_get_events(url=None, threshold=None, bunch_reoccuring=True):
    url_parts = urlparse(url)
    if url_parts.scheme == "webcal":
        http_url = f"https://{url_parts.netloc}{url_parts.path}"
    else:
        http_url = url
    
    response = requests.get(http_url)
    calendar_data = response.text
    
    cal = Calendar.from_ical(calendar_data)

    tz = timezone('Europe/Stockholm')
    
    if threshold is None:
        threshold = datetime.now(tz)
    else:
        threshold = threshold.replace(tzinfo=tz)

    ret = list()
    recurrence_map = {}

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

        exdates = []
        if 'EXDATE' in event:
            exdate_field = event.get('EXDATE')
            if not isinstance(exdate_field, list):
                exdate_field = [exdate_field]
            for exdate in exdate_field:
                for ex in exdate.dts:
                    exdates.append(ex.dt.replace(tzinfo=tz))

        uid = event.get('UID')
        summary = event.get('SUMMARY')

        if 'RRULE' in event:
            rule = rrulestr(event['RRULE'].to_ical().decode('utf-8'), dtstart=event_start)
            rrule_set = rruleset()
            rrule_set.rrule(rule)
            for exdate in exdates:
                rrule_set.exdate(exdate)

            if uid not in recurrence_map:
                recurrence_map[uid] = {
                    "rrule_set": rrule_set,
                    "summary": summary,
                    "start": event_start,
                    "end": event_end,
                }
            else:
                recurrence_map[uid]["rrule_set"].rrule(rule)
                for exdate in exdates:
                    recurrence_map[uid]["rrule_set"].exdate(exdate)

        elif 'RECURRENCE-ID' in event:
            recurrence_instance = event.get('RECURRENCE-ID').dt.replace(tzinfo=tz)
            if uid in recurrence_map:
                rrule_set = recurrence_map[uid]["rrule_set"]
                rrule_set.exdate(recurrence_instance)

                e = lambda: None
                e.name = summary
                e.start = event_start.replace(tzinfo=None)
                e.end = event_end.replace(tzinfo=None)
                ret.append(e)
        else:
            # single event
            t = min(event_start.replace(hour=23, minute=59), event_end)
            t = t.replace(tzinfo=None)

            if threshold.replace(tzinfo=None) < t:
                e = lambda: None
                e.name = summary
                e.start = event_start.replace(tzinfo=None)
                e.end = event_end.replace(tzinfo=None)
                ret.append(e)

    for uid, value in recurrence_map.items():
        rrule_set = value["rrule_set"]
        summary = value["summary"]
        event_start = value["start"]
        event_end = value["end"]

        if bunch_reoccuring:
            occurrences = rrule_set.after(threshold)
            if occurrences is not None:
                e = lambda: None
                e.name = summary
                e.start = occurrences.replace(tzinfo=None)
                e.end = (occurrences + (event_end - event_start)).replace(tzinfo=None)

                counter = -1
                while occurrences is not None and counter <= 99:
                    counter += 1
                    occurrences = rrule_set.after(occurrences)

                e.name += " (+" + str(counter) + ")"

                ret.append(e)
        else:
            occurrences = rrule_set.after(threshold)
            if occurrences is not None:
                counter = -1
                while occurrences is not None and counter <= 99:
                    e = lambda: None
                    e.name = summary
                    e.start = occurrences.replace(tzinfo=None)
                    e.end = (occurrences + (event_end - event_start)).replace(tzinfo=None)

                    counter += 1
                    occurrences = rrule_set.after(occurrences)

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


def shifts(url, nof_days=8):
    current_date = datetime.now()
    list_dates = []
    list_dates.append(current_date.replace(hour=0, minute=0, second=0, microsecond=0))
    for _ in range(nof_days - 1):
        current_date += timedelta(days=1)
        list_dates.append(current_date.replace(hour=0, minute=0, second=0, microsecond=0))

    events = get_events(url)
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


def save_events_to_disk(events, filename):
    data = [
        {attr: (getattr(lmbda, attr).isoformat() if isinstance(getattr(lmbda, attr), datetime) else getattr(lmbda, attr))
         for attr in dir(lmbda) if not attr.startswith('__')} for lmbda in events
    ]
    with open(filename, 'w') as f:
        json.dump(data, f)


def read_events_from_disk(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    events = []
    for item in data:
        o = lambda: None
        for k, v in item.items():
            try:
                setattr(o, k, datetime.fromisoformat(v))
            except (TypeError, ValueError):
                setattr(o, k, v)
        events.append(o)
    return events


def get_events(url, threshold=None, bunch_reoccuring=True, refresh_interval_minutes=10):
    hash_value = hashlib.md5(url.encode()).hexdigest()[:8]
    filename = f'/tmp/calendar_buffer_{hash_value}.json'

    if os.path.exists(filename):
        last_modified = datetime.fromtimestamp(os.path.getmtime(filename))
        if datetime.now() - last_modified < timedelta(minutes=refresh_interval_minutes):
            return read_events_from_disk(filename)

    events = __force_get_events(url, threshold, bunch_reoccuring)
    save_events_to_disk(events, filename)
    return events


if __name__ == "__main__":
    from personal_data import family_calendar, anne_calendar

    print_events(get_events(family_calendar))
    print("")
    print_events(get_events(anne_calendar))
    print("")
    print(shifts(anne_calendar))
