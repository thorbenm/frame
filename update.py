from PIL import Image, ImageDraw, ImageFont
import time
import datetime
import _waveshare
from capture_website import capture_screenshot
import numpy as np


DIMENSIONS = (480, 800)
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def scale_image_values(image, scale_black, scale_white):
    def fun(x):
        fx = float(x)
        fx = _map(fx, scale_black, scale_white, 0.0, 255.0)
        fx = min(fx, 255.0)
        fx = max(fx, 0.0)
        return round(fx)
    return image.point(fun, "L")


def get_yr():
    full = capture_screenshot("https://www.yr.no/en/forecast/daily-table/2-2670879/Sweden/Stockholm/Sundbyberg%20Municipality/Sundbyberg")
    _waveshare.save_image_to_disk(full, "yr_full")

    current_conditions = full.crop((330, 270, full.width - 1000, full.height - 750))
    current_conditions = scale_image_values(current_conditions, 100.0, 255.0)
    _waveshare.save_image_to_disk(current_conditions, "yr_current_conditions")

    rain_graph = full.crop((1210, 250, full.width - 360, full.height - 740))
    rain_graph = scale_image_values(rain_graph, 25.0, 255.0)
    _waveshare.save_image_to_disk(rain_graph, "yr_rain_graph")
    return current_conditions, rain_graph


def get_sl():
    tuletorg_full = capture_screenshot("https://sl.se/?mode=departures&origName=Tuletorget+%28Sundbyberg%29&origSiteId=3515&origPlaceId=QT0xQE89VHVsZXRvcmdldCAoU3VuZGJ5YmVyZylAWD0xNzk3NDcxM0BZPTU5MzY0ODA3QFU9NzRATD0zMDAxMDM1MTVAQj0xQA%3D%3D", size="480x1100")
    _waveshare.save_image_to_disk(tuletorg_full, "sl_tuletorg_full")

    tuletorg_cropped = tuletorg_full.crop((0, 1055, 480, 1100))
    tuletorg_cropped = scale_image_values(tuletorg_cropped, 50.0, 240.0)

    _waveshare.save_image_to_disk(tuletorg_cropped, "sl_tuletorg_cropped")
    return tuletorg_cropped


def add_text_to_image(draw, text, size, location):
    x, y = location
    if x < 0:
        text_width, text_height = draw.textsize(text,
                                                font=ImageFont.truetype(FONT_PATH, size))
        x = (DIMENSIONS[0] - text_width) // 2


    draw.text((x, y), text, font=ImageFont.truetype(FONT_PATH, size), fill=0)
    

def main():
    image = Image.new('1', DIMENSIONS, 255)
    draw = ImageDraw.Draw(image)

    current_date = time.strftime('%a, %Y-%-m-%-d')
    week_number = datetime.datetime.now().isocalendar()[1]
    current_date += ", Week " + str(week_number)
    add_text_to_image(draw, current_date, 30, (-1, 10))

    current_time = time.strftime('%-I:%M')
    add_text_to_image(draw, current_time, 150, (-1, 20))

    current_conditions, rain_graph = get_yr()

    current_conditions = current_conditions.resize((480, round(current_conditions.size[1] * 480 / current_conditions.size[0])))
    image.paste(current_conditions, (0, 200))

    rain_graph = rain_graph.resize((480, round(rain_graph.size[1] * 480 / rain_graph.size[0])))
    image.paste(rain_graph, (0, 270))

    sl = get_sl()
    image.paste(sl, (0, 500))

    _waveshare.show_image(image)


if __name__ == "__main__":
    main()

