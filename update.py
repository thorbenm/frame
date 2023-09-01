from PIL import Image, ImageDraw, ImageFont
import time
import datetime
import _waveshare
import numpy as np
import traceback
from timeout_decorator import timeout
import _calendar
import _yr
import _sl


def add_text_to_image(draw, text, size, location):
    x, y = location
    f = ImageFont.truetype(_waveshare.FONT, size)
    width, height = draw.textsize(text, font=f)
    if x < 0:
        x = (_waveshare.DIMENSIONS[0] - width) // 2

    draw.text((x, y), text, font=f, fill=0)
    return height


def add_line(draw, c, thickness=2):
    draw.line([(0, c), (_waveshare.DIMENSIONS[0] - 1, c)],
               fill=0, width=thickness)
    return thickness


def add_date_and_time(draw, c):
    cc = 0
    current_date = time.strftime('%a, %Y-%-m-%-d')
    week_number = datetime.datetime.now().isocalendar()[1]
    current_date += ", Week " + str(week_number)

    cc += add_text_to_image(draw, current_date, 30, (-1, c + cc))
    cc -= 20

    current_time = (datetime.datetime.now() + datetime.timedelta(minutes=1)).strftime('%-I:%M')
    # its actually the time + 1 minute because we start the process early
    cc += add_text_to_image(draw, current_time, 150, (-1, c + cc))
    cc += 10
    return cc


def add_calendar_events(draw, c):
    cc = 0
    events = _calendar.get_events()
    for e in events[0:6]:
        add_text_to_image(draw, e.name, 17, (240, c + cc))
        cc += add_text_to_image(draw, _calendar.convert(e.start) + ":", 17, (10, c + cc))
    return cc


def add_weather(image, c):
    cc = 0
    current_conditions, rain_graph = _yr.get_current_weather()

    image.paste(current_conditions, (0, c + cc))
    cc += current_conditions.size[1]

    image.paste(rain_graph, (0, c + cc))
    cc += rain_graph.size[1]

    forecast = _yr.get_short_forecast()
    image.paste(forecast, (0, c + cc))
    cc += forecast.size[1]

    return cc


def add_public_transport(image, c):
    cc = 0
    tunnelbana = _sl.get_tunnelbana()
    image.paste(tunnelbana, (0, c + cc))
    cc += tunnelbana.size[1]

    pendel = _sl.get_pendel()
    image.paste(pendel, (0, c + cc))
    cc += pendel.size[1]

    bus = _sl.get_bus()
    image.paste(bus, (0, c + cc))
    cc += bus.size[1]

    return cc


@timeout(45)
def generate_image():
    image = Image.new('1', _waveshare.DIMENSIONS, 255)
    draw = ImageDraw.Draw(image)
    c = 0  # vertical cursor

    separator = 6

    c += separator
    c += add_date_and_time(draw, c)
    c += separator
    c += add_line(draw, c)
    c += separator
    c += add_calendar_events(draw, c)
    c += separator
    c += add_line(draw, c)
    c += separator
    c += add_weather(image, c)
    c += separator
    c += add_line(draw, c)
    c += separator
    c += add_public_transport(image, c)

    #
    _waveshare.save_image_to_disk(image, "wip")
    #

    return image


def main():
    _waveshare.show_image(generate_image())


def try_main():
    try:
        main()
    except Exception:
        error_message = traceback.format_exc()
        print(error_message)
        _waveshare.show_text(error_message)


if __name__ == "__main__":
    try_main()
