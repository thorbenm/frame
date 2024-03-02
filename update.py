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
import ephem
from personal_data import family_calendar, anne_calendar
from random import sample


class ImageGenerator():
    def __init__(self):
        self.image = Image.new('1', _waveshare.DIMENSIONS, 255)
        self.draw = ImageDraw.Draw(self.image)
        self.cursor = 0
        self.previous_cursor = 0

    def move_cursor(self, movement):
        self.previous_cursor = self.cursor
        self.cursor += movement

    def move_cursor_to_previous_position(self):
        self.cursor = self.previous_cursor

    def add_text_to_image(self, text, size, x=None, y=None, line_spacing=1.1):
        f = ImageFont.truetype(_waveshare.FONT, size)
        width, _ = self.draw.textsize(text, font=f)

        if x is None:
            # horizontally centered
            x = (_waveshare.DIMENSIONS[0] - width) // 2
        if y is None:
            y = self.cursor

        self.draw.text((x, y), text, font=f, fill=0)
        self.move_cursor(round(line_spacing * size))

    def add_line(self, thickness=2):
        self.draw.line([(0, self.cursor), (_waveshare.DIMENSIONS[0] - 1, self.cursor)],
                       fill=0, width=thickness)
        self.move_cursor(thickness)

    def add_date_and_time(self):
        current_date = time.strftime('%a, %Y-%-m-%-d')
        week_number = datetime.datetime.now().isocalendar()[1]
        current_date += ", Week " + str(week_number)

        self.add_text_to_image(current_date, 30)
        self.move_cursor(-25)  # WTF?

        current_time = (datetime.datetime.now() + datetime.timedelta(minutes=1)).strftime('%H:%M')
        # its actually the time + 1 minute because we start the process early
        self.add_text_to_image(current_time, 150, line_spacing=1.0)

    def get_sunset_diff(self):
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        stockholm = ephem.city('Stockholm')
        sunset = ephem.localtime(stockholm.next_setting(ephem.Sun(), current_date))
        sunset_yesterday = ephem.localtime(stockholm.next_setting(ephem.Sun(), yesterday))
        sunset_yesterday = sunset_yesterday + datetime.timedelta(days=1)
        sunset_diff = abs(sunset - sunset_yesterday)

        if sunset_yesterday < sunset:
            sign = "+"
        else:
            sign = "-"

        return sign + (datetime.datetime(1970, 1, 1) + sunset_diff).strftime('%-M\' %S"')

    def add_sunrise_sunset(self):
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        stockholm = ephem.city('Stockholm')
        sunrise = ephem.localtime(stockholm.next_rising(ephem.Sun(), current_date))
        sunset = ephem.localtime(stockholm.next_setting(ephem.Sun(), current_date))
        sunrise = sunrise.strftime('%-H:%M')
        sunset = sunset.strftime('%-H:%M')

        self.add_text_to_image("Sunrise: " + sunrise, 17, x=10)
        self.move_cursor_to_previous_position()
        self.add_text_to_image("Sunset: " + sunset + " (" +
                               self.get_sunset_diff() + ")", 17, x=240)

    def add_calendar_events(self):
        events = _calendar.get_events(family_calendar)
        for e in events[0:4]:
            self.add_text_to_image(e.name, 17, x=240)
            self.move_cursor_to_previous_position()
            self.add_text_to_image(_calendar.convert(e.start) + ":", 17, x=10)

    def add_shifts(self):
        self.add_text_to_image(_calendar.shifts(), 17, x=10)

    def add_weather(self):
        current_conditions, rain_graph = _yr.get_current_weather()

        self.image.paste(current_conditions, (0, self.cursor))
        self.move_cursor(current_conditions.size[1])

        self.image.paste(rain_graph, (0, self.cursor))
        self.move_cursor(rain_graph.size[1])

        forecast = _yr.get_short_forecast()
        self.image.paste(forecast, (0, self.cursor))
        self.move_cursor(forecast.size[1])

    def add_public_transport(self):
        d = _sl.get_data()
        kungstradgarden = "Kungsträdgården"
        vasterhaninge = "Västerhaninge"
        tunnelbana = next(filter(lambda x: x.destination == kungstradgarden, d), None)
        pendel = next(filter(lambda x: x.destination == vasterhaninge, d), None)
        buss = next(filter(lambda x: x.destination == "Rissne", d), None)

        if tunnelbana is not None:
            d.remove(tunnelbana)
        if pendel is not None:
            d.remove(pendel)
        if buss is not None:
            d.remove(buss)
        r = sample(d, 4 + sum([j is None for j in [tunnelbana, pendel, buss]]))

        def add_element(d):
            if d is not None:
                self.add_text_to_image(d.destination[:15] + " (" +
                                       d.number + "):", 17, x=10)
                self.move_cursor_to_previous_position()
                self.add_text_to_image(d.times, 17, x=240)

        add_element(tunnelbana)
        add_element(pendel)
        add_element(buss)
        for rr in r:
            add_element(rr)


    def generate_image(self):

        separator = 5

        self.move_cursor(separator)

        self.add_date_and_time()
        self.move_cursor(separator)

        self.add_line()
        self.move_cursor(separator)

        self.add_shifts()
        self.add_sunrise_sunset()
        self.move_cursor(separator)

        self.add_line()
        self.move_cursor(separator)

        self.add_calendar_events()
        self.move_cursor(separator)

        self.add_line()
        self.move_cursor(separator)

        self.add_weather()
        self.move_cursor(separator)

        self.add_line()
        self.move_cursor(separator)

        self.add_public_transport()

        return self.image


@timeout(45)
def generate_image():
    ig = ImageGenerator()
    image = ig.generate_image()
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
