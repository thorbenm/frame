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
import water_temperature


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
        self.cursor, self.previous_cursor = self.previous_cursor, self.cursor

    def add_text_to_image(self, text, size=16, x=None, y=None, line_spacing=1.1):
        f = ImageFont.truetype(_waveshare.FONT, size)
        width, _ = self.draw.textsize(text, font=f)

        if x is None:
            # horizontally centered
            x = (_waveshare.DIMENSIONS[0] - width) // 2
            x += 3
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

    def add_water_temperature_sunrise_sunset(self):
        temp = water_temperature.get()

        def get_sunset_diff():
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

        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        stockholm = ephem.city('Stockholm')
        sunrise = ephem.localtime(stockholm.next_rising(ephem.Sun(), current_date))
        sunset = ephem.localtime(stockholm.next_setting(ephem.Sun(), current_date))
        sunrise = sunrise.strftime('%-H:%M')
        sunset = sunset.strftime('%-H:%M')
        diff = get_sunset_diff()

        self.add_text_to_image(f"Water: {temp}, Sunrise: {sunrise}, Sunset: {sunset} ({diff})")

    def add_calendar_events(self):
        for e in _calendar.get_events(family_calendar)[0:4]:
            name = e.name
            if 23 < len(name):
                name = name[:21] + "..."
            name = " ".join([j.capitalize() for j in name.split()])
            self.add_text_to_image(name, x=240)
            self.move_cursor_to_previous_position()
            self.add_text_to_image(_calendar.convert(e.start) + ":", x=10)

    def add_week(self):
        rectangle_height = 60
        font_offset_x = 5
        font_offset_y = 3
        font_size = 14
        icon_offset_x = 30
        icon_offset_y = 31

        w = _yr.get_long_forecast_text()
        i = _yr.get_long_forecast_icons()
        c = self.cursor
        s = _calendar.shifts(anne_calendar)

        for j in range(8):
            dt = datetime.datetime.now() + datetime.timedelta(days=j)
            weekday = dt.strftime('%a')[:2]
            day_in_month = dt.strftime('%-d')
            weekend = weekday[0] == "S"

            self.image.paste(i[j], (j * 60 + icon_offset_x, c + icon_offset_y))

            rectangle_x0 = j * 60
            rectangle_y0 = c
            rectangle_x1 = rectangle_x0 + 60 + 1
            rectangle_y1 = rectangle_y0 + rectangle_height
            if j == 7:
                rectangle_x1 -= 2

            width = 2
            if weekend:
                width = 4
            self.draw.rectangle([rectangle_x0, rectangle_y0, rectangle_x1, rectangle_y1],
                                outline="black", width=width)

            def calendar_has_event_for_this_day(dt):
                for e in _calendar.get_events(family_calendar):
                    if (dt.year == e.start.year and
                            dt.month == e.start.month and
                            dt.day == e.start.day):
                        return True
                return None

            if calendar_has_event_for_this_day(dt):
                x = rectangle_x0 + 5
                y = rectangle_y0 + 51
                self.draw.rectangle([x, y, x + 4, y + 4],
                                    width=width, fill='black')

            self.move_cursor(font_offset_y)
            self.add_text_to_image(weekday + ", " + day_in_month, font_size, x=font_offset_x+j*60)
            self.add_text_to_image(w[j].temp_high_low[:6], font_size, x=font_offset_x+j*60)
            self.add_text_to_image(s[j] + " " + w[j].precipitation, font_size, x=font_offset_x+j*60)
            self.cursor = c

        self.move_cursor(rectangle_height)

    def add_weather(self):
        current_conditions, rain_graph = _yr.get_current_weather_image()

        self.image.paste(current_conditions, (0, self.cursor))
        self.move_cursor(current_conditions.size[1])

        self.image.paste(rain_graph, (0, self.cursor))
        self.move_cursor(rain_graph.size[1])

        forecast = _yr.get_short_forecast_image()
        self.image.paste(forecast, (0, self.cursor))
        self.move_cursor(forecast.size[1])

    def add_public_transport(self):
        data = _sl.get_data()
        show = list()

        kungstradgarden = "Kungsträdgården"
        balsta = "Bålsta"
        kungsangen = "Kungsängen"
        kallhall = "Kallhäll"

        show.extend(list(filter(lambda x: x.destination == kungstradgarden, data)))
        show.extend(list(filter(lambda x: x.number in ["43", "43X", "44", "44X"] and not x.destination in [balsta, kungsangen, kallhall], data)))
        show.extend(list(filter(lambda x: x.destination == "Rissne", data)))

        data = list(filter(lambda x: x not in show, data))

        total_number_of_elements = 6
        add_elements = total_number_of_elements - len(show)
        if len(data) <= add_elements:
            show.extend(data)
        else:
            show.extend(sample(data, add_elements))

        for s in show:
            self.add_text_to_image(f"{s.destination[:16]} ({s.number}):", x=10)
            self.move_cursor_to_previous_position()
            self.add_text_to_image(s.times, x=240)

    def generate_image(self):
        separator = 4

        self.move_cursor(separator)

        self.add_date_and_time()
        self.move_cursor(separator)

        self.add_line()
        self.move_cursor(separator)

        self.add_water_temperature_sunrise_sunset()
        self.move_cursor(separator)

        self.add_week()
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
