import capture_website
import re


def get_data():
    text = capture_website.capture_text("https://sl.se/?mode=departures&origName=Sundbybergs+station+%28Sundbyberg%29&origSiteId=9325&origPlaceId=QT0xQE89U3VuZGJ5YmVyZ3Mgc3RhdGlvbiAoU3VuZGJ5YmVyZylAWD0xNzk3MTQ5NUBZPTU5MzYwODcwQFU9NzRATD0zMDIxMDkzMjVAQj0xQA%3D%3D")

    pattern = r"^(.*)\slinje\s(\d+)\smot\s(.*)\.\sNästa\savgång:\s(.*),\sfrån\s"

    matches = []
    for line in text.strip().split("\n"):
        match = re.match(pattern, line)
        if match:
            matches.append(match.groups())

    grouped = {}
    for item in matches:
        key = tuple(item[:3])
        if key not in grouped:
            grouped[key] = [item[3]]
        else:
            grouped[key].append(item[3])

    result = [(key[0], key[1], key[2], ", ".join(times)) for key, times in grouped.items()]
    result = [type('', (), {"type": j[0], "number": j[1], "destination": j[2], "times": j[3]})() for j in result]
    return result


if __name__ == "__main__":
    for d in get_data():
        print(d.type, d.number, d.destination, d.times)
