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

    # Convert threshold to naive datetime for comparisons
    threshold_naive = threshold.replace(tzinfo=None)

    ret = list()
    recurrence_map = {}

    for event in cal.walk('VEVENT'):
        event_start = event.get('dtstart').dt

        # Convert to naive datetime objects
        if isinstance(event_start, datetime):
            if event_start.tzinfo:
                event_start = event_start.astimezone(tz).replace(tzinfo=None)
            else:
                event_start = event_start.replace(tzinfo=None)
        elif isinstance(event_start, date):
            event_start = datetime.combine(event_start, datetime.min.time())

        event_end = event.get('dtend').dt

        if isinstance(event_end, datetime):
            if event_end.tzinfo:
                event_end = event_end.astimezone(tz).replace(tzinfo=None)
            else:
                event_end = event_end.replace(tzinfo=None)
        elif isinstance(event_end, date):
            event_end = datetime.combine(event_end, datetime.min.time())

        exdates = []
        if 'EXDATE' in event:
            exdate_field = event.get('EXDATE')
            if not isinstance(exdate_field, list):
                exdate_field = [exdate_field]
            for exdate in exdate_field:
                for ex in exdate.dts:
                    ex_dt = ex.dt
                    if isinstance(ex_dt, datetime) and ex_dt.tzinfo:
                        ex_dt = ex_dt.astimezone(tz).replace(tzinfo=None)
                    elif isinstance(ex_dt, date):
                        ex_dt = datetime.combine(ex_dt, datetime.min.time())
                    exdates.append(ex_dt)

        uid = event.get('UID')
        summary = event.get('SUMMARY')

        if 'RRULE' in event:
            try:
                # Parse and modify the RRULE if it contains UNTIL
                rule_text = event['RRULE'].to_ical().decode('utf-8')

                # Check if the rule has a COUNT parameter
                has_count = 'COUNT=' in rule_text
                count_value = None
                has_until = 'UNTIL=' in rule_text
                until_date = None

                if has_count:
                    # Extract the COUNT value
                    rule_parts = rule_text.split(';')
                    for part in rule_parts:
                        if part.startswith('COUNT='):
                            try:
                                count_value = int(part.replace('COUNT=', ''))
                            except ValueError:
                                pass

                # If UNTIL is in the rule, we need to handle it specially
                if has_until:
                    # Extract the UNTIL date to use as a boundary
                    rule_parts = rule_text.split(';')

                    for part in rule_parts:
                        if part.startswith('UNTIL='):
                            until_str = part.replace('UNTIL=', '')
                            try:
                                # Parse the UNTIL date
                                if 'T' in until_str:
                                    until_format = '%Y%m%dT%H%M%SZ'
                                else:
                                    until_format = '%Y%m%d'
                                until_date = datetime.strptime(until_str, until_format)
                                # If the UNTIL date is in the past, we'll check if we should skip this event
                                if until_date < threshold_naive:
                                    # Skip this recurring event entirely as it has ended
                                    break
                            except ValueError:
                                pass

                    # If the event has ended (UNTIL date is in the past), skip it
                    if until_date and until_date < threshold_naive:
                        continue

                    # Use the original rule with the UNTIL part intact
                    rule = rrulestr(rule_text, dtstart=event_start)
                else:
                    rule = rrulestr(rule_text, dtstart=event_start)

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
                        "has_count": has_count,
                        "count_value": count_value,
                        "has_until": has_until,
                        "until_date": until_date,
                    }
                else:
                    recurrence_map[uid]["rrule_set"].rrule(rule)
                    for exdate in exdates:
                        recurrence_map[uid]["rrule_set"].exdate(exdate)
                    # Update has_count and count_value if this rule has them
                    if has_count:
                        recurrence_map[uid]["has_count"] = has_count
                        recurrence_map[uid]["count_value"] = count_value
                    # Update has_until and until_date if this rule has them
                    if has_until:
                        recurrence_map[uid]["has_until"] = has_until
                        recurrence_map[uid]["until_date"] = until_date
            except ValueError:
                # If we still get an error, just add the first occurrence
                t = min(event_start.replace(hour=23, minute=59), event_end)
                if threshold_naive < t:
                    e = lambda: None
                    e.name = summary
                    e.start = event_start
                    e.end = event_end
                    ret.append(e)

        elif 'RECURRENCE-ID' in event:
            recurrence_id = event.get('RECURRENCE-ID').dt
            if isinstance(recurrence_id, datetime) and recurrence_id.tzinfo:
                recurrence_id = recurrence_id.astimezone(tz).replace(tzinfo=None)
            elif isinstance(recurrence_id, date):
                recurrence_id = datetime.combine(recurrence_id, datetime.min.time())

            if uid in recurrence_map:
                rrule_set = recurrence_map[uid]["rrule_set"]
                rrule_set.exdate(recurrence_id)

                e = lambda: None
                e.name = summary
                e.start = event_start
                e.end = event_end
                ret.append(e)
        else:
            # single event
            t = min(event_start.replace(hour=23, minute=59), event_end)

            if threshold_naive < t:
                e = lambda: None
                e.name = summary
                e.start = event_start
                e.end = event_end
                ret.append(e)

    for uid, value in recurrence_map.items():
        rrule_set = value["rrule_set"]
        summary = value["summary"]
        event_start = value["start"]
        event_end = value["end"]
        has_count = value.get("has_count", False)
        count_value = value.get("count_value", None)
        has_until = value.get("has_until", False)
        until_date = value.get("until_date", None)

        if bunch_reoccuring:
            occurrences = rrule_set.after(threshold_naive)
            if occurrences is not None:
                e = lambda: None
                e.name = summary
                e.start = occurrences
                e.end = (occurrences + (event_end - event_start))

                counter = -1
                while occurrences is not None and counter <= 99:
                    counter += 1
                    occurrences = rrule_set.after(occurrences)

                # Add appropriate label based on whether it has COUNT, UNTIL or neither
                if has_count and count_value is not None:
                    e.name += f" (+{counter})"
                elif has_until and until_date is not None:
                    e.name += f" (+{counter})"
                else:
                    e.name += " (recurring)"

                ret.append(e)
        else:
            occurrences = rrule_set.after(threshold_naive)
            if occurrences is not None:
                # Calculate total occurrences for events with UNTIL
                total_occurrences = None
                if has_until and until_date is not None:
                    total_occurrences = 0
                    temp_occurrences = occurrences
                    while temp_occurrences is not None and total_occurrences <= 99:
                        total_occurrences += 1
                        temp_occurrences = rrule_set.after(temp_occurrences)

                counter = -1
                while occurrences is not None and counter <= 99:
                    e = lambda: None
                    e.name = summary
                    e.start = occurrences
                    e.end = (occurrences + (event_end - event_start))

                    counter += 1

                    # When bunch_reoccuring=False, don't add any labels

                    next_occurrence = rrule_set.after(occurrences)
                    occurrences = next_occurrence

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
    hash_input = url + str(bunch_reoccuring)
    hash_value = hashlib.md5(hash_input.encode()).hexdigest()[:8]
    filename = f'/tmp/calendar_buffer_{hash_value}.json'

    if os.path.exists(filename):
        last_modified = datetime.fromtimestamp(os.path.getmtime(filename))
        if datetime.now() - last_modified < timedelta(minutes=refresh_interval_minutes):
            return read_events_from_disk(filename)

    events = __force_get_events(url, threshold, bunch_reoccuring)
    save_events_to_disk(events, filename)
    return events


if __name__ == "__main__":
    from personal_data import (
        family_calendar,
        anne_work_calendar,
        thorben_personal_calendar,
        anne_personal_calendar
    )

    print("Family calendar:")
    print_events(get_events(family_calendar))
    print("")
    print("Family calendar (bunch reoccuring=False):")
    print_events(get_events(family_calendar, bunch_reoccuring=False))
    print("")
    print("Anne work calendar:")
    print_events(get_events(anne_work_calendar))
    print("")
    print("Anne work calendar shifts:")
    print(shifts(anne_work_calendar))
    print("")
    print("Thorben personal calendar:")
    print_events(get_events(thorben_personal_calendar))
    print("")
    print("Anne personal calendar:")
    print_events(get_events(anne_personal_calendar))
    print("")
