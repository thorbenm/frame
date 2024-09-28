import capture_website
import re


def subtract_one_minute(string):
    if string == "1 min" or string == "Nu":
        return "Nu"
    if string.endswith(" min"):
        number_of_minutes = int(string.removesuffix(" min"))
        number_of_minutes -= 1
        return str(number_of_minutes) + " min"
    return string


def get_data():
    text = capture_website.capture_text("https://sl.se/?mode=departures&departuresSiteId=9704&name=Sp%C3%A5nga%20station%20(Stockholm)", sleep=3.0)

    pattern = r"^.*\slinje\s(\d+[A-Za-z]?)\smot\s(.*)\.\sNästa\savgång:\s(.*),\sfrån\s"

    matches = list()
    for line in text.strip().split("\n"):
        match = re.match(pattern, line)
        if match:
            matches.append(match.groups())

    # group by connections to append times
    grouped = dict()
    for m in matches:
        number = m[0]
        destination = m[1]
        connection = tuple([number, destination])

        time = subtract_one_minute(m[2])

        if connection not in grouped:
            grouped[connection] = time
        else:
            grouped[connection] += ", " + time

    def create_object(connection, times):
        obj = lambda: None
        obj.number, obj.destination = connection
        obj.times = times
        return obj

    return [create_object(connection, times) for connection, times in grouped.items()]


if __name__ == "__main__":
    for d in get_data():
        print(d.destination, d.number, d.times)
