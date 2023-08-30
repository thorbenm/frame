from PIL import Image, ImageDraw, ImageFont
import time
import datetime
import _waveshare
from capture_website import capture_screenshot
import numpy as np
import traceback
from timeout_decorator import timeout
from _calendar import get_events, convert


DIMENSIONS = (480, 800)
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def image_contrast(image, scale_black, scale_white):
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

    current_conditions = full.crop((330, 260, full.width - 1000, full.height - 750))
    # for j in range(0, 255):
    #     _waveshare.save_image_to_disk(image_contrast(current_conditions, float(j), 255.0).convert("1"), str(j)) 
    current_conditions = image_contrast(current_conditions, 200.0, 255.0)
    _waveshare.save_image_to_disk(current_conditions, "yr_current_conditions")

    rain_graph = full.crop((1210, 250, full.width - 360, full.height - 740))
    rain_graph = image_contrast(rain_graph, 150.0, 255.0)
    _waveshare.save_image_to_disk(rain_graph, "yr_rain_graph")
    return current_conditions, rain_graph


def get_forecast():
    full = capture_screenshot("https://www.yr.no/en/forecast/graph/2-2670879/Sweden/Stockholm/Sundbyberg%20Municipality/Sundbyberg", size="495x1100")
    _waveshare.save_image_to_disk(full, "yr_full2")

    forecast = full.crop((0, 351, 480, 518))
    forecast = image_contrast(forecast, 180.0, 245.0)
    _waveshare.save_image_to_disk(forecast, "yr_forecast")

    return forecast


def get_sl_tunnelbana():
    tunnelbana_full = capture_screenshot("https://sl.se/?mode=departures&origName=Sundbybergs+station+%28Sundbyberg%29&origSiteId=9325&origPlaceId=QT0xQE89U3VuZGJ5YmVyZ3Mgc3RhdGlvbiAoU3VuZGJ5YmVyZylAWD0xNzk3MTQ5NUBZPTU5MzYwODcwQFU9NzRATD0zMDIxMDkzMjVAQj0xQA%3D%3D", size="495x1500", press_coordinates=(24, 920))
    _waveshare.save_image_to_disk(tunnelbana_full, "sl_tunnelbana_full")

    elements = list()
    elements.append(tunnelbana_full.crop((0, 1071, 480, 1132)))
    elements.append(tunnelbana_full.crop((0, 1140, 480, 1201)))
    _waveshare.save_image_to_disk(elements[0], "sl_tunnelbana_0")
    _waveshare.save_image_to_disk(elements[1], "sl_tunnelbana_1")

    kungstradgarden = min(elements, key=lambda img: sum(img.crop((154, 0, 260, img.size[1])).getdata()))
    kungstradgarden = image_contrast(kungstradgarden, 100.0, 240.0)
    kungstradgarden.paste(255, (0, 0, 11, kungstradgarden.height))
    _waveshare.save_image_to_disk(kungstradgarden, "sl_tunnelbana_kungstradgarden")

    return kungstradgarden


def get_sl_pendel():
    pendel_full = capture_screenshot("https://sl.se/?mode=departures&origName=Sundbybergs+station+%28Sundbyberg%29&origSiteId=9325&origPlaceId=QT0xQE89U3VuZGJ5YmVyZ3Mgc3RhdGlvbiAoU3VuZGJ5YmVyZylAWD0xNzk3MTQ5NUBZPTU5MzYwODcwQFU9NzRATD0zMDIxMDkzMjVAQj0xQA%3D%3D", size="495x1500", press_coordinates=(308, 920))
    _waveshare.save_image_to_disk(pendel_full, "sl_pendel_full")

    elements = list()
    elements.append(pendel_full.crop((0, 1071, 480, 1132)))
    elements.append(pendel_full.crop((0, 1140, 480, 1201)))
    elements.append(pendel_full.crop((0, 1209, 480, 1270)))
    _waveshare.save_image_to_disk(elements[0], "sl_pendel_0")
    _waveshare.save_image_to_disk(elements[1], "sl_pendel_1")
    _waveshare.save_image_to_disk(elements[2], "sl_pendel_2")

    vasterhaninge = min(elements, key=lambda img: sum(img.crop((176, 0, 260, img.size[1])).getdata()))
    vasterhaninge = image_contrast(vasterhaninge, 100.0, 240.0)
    vasterhaninge.paste(255, (0, 0, 11, vasterhaninge.height))
    _waveshare.save_image_to_disk(vasterhaninge, "sl_pendel_vasterhanigne")

    return vasterhaninge


def get_sl_bus():
    bus_full = capture_screenshot("https://sl.se/?mode=departures&origName=Tuletorget+%28Sundbyberg%29&origSiteId=3515&origPlaceId=QT0xQE89VHVsZXRvcmdldCAoU3VuZGJ5YmVyZylAWD0xNzk3NDcxM0BZPTU5MzY0ODA3QFU9NzRATD0zMDAxMDM1MTVAQj0xQA%3D%3D", size="495x1500")
    _waveshare.save_image_to_disk(bus_full, "sl_bus_full")

    bus_cropped = bus_full.crop((0, 1023, 480, 1084))
    bus_cropped = image_contrast(bus_cropped, 100.0, 240.0)

    _waveshare.save_image_to_disk(bus_cropped, "sl_bus_cropped")
    return bus_cropped


def add_text_to_image(draw, text, size, location):
    x, y = location
    text_width, text_height = draw.textsize(text,
                                            font=ImageFont.truetype(FONT_PATH, size))
    if x < 0:
        x = (DIMENSIONS[0] - text_width) // 2


    draw.text((x, y), text, font=ImageFont.truetype(FONT_PATH, size), fill=0)
    return text_height


def generate_image():
    image = Image.new('1', DIMENSIONS, 255)
    draw = ImageDraw.Draw(image)

    current_date = time.strftime('%a, %Y-%-m-%-d')
    week_number = datetime.datetime.now().isocalendar()[1]
    current_date += ", Week " + str(week_number)

    c = 0  # vertical cursor

    c += add_text_to_image(draw, current_date, 30, (-1, c))
    c -= 29


    current_time = (datetime.datetime.now() + datetime.timedelta(minutes=1)).strftime('%-I:%M')
    # its actually the time + 1 minute because we start the process early
    c += add_text_to_image(draw, current_time, 150, (-1, c))

    c += 6
    draw.line([(0, c), (DIMENSIONS[0] - 1, c)], fill=0, width=2)
    c += 2

    current_conditions, rain_graph = get_yr()

    current_conditions = current_conditions.resize((480, round(current_conditions.size[1] * 480 / current_conditions.size[0])))
    image.paste(current_conditions, (0, c))
    c += current_conditions.size[1]

    rain_graph = rain_graph.resize((480, round(rain_graph.size[1] * 480 / rain_graph.size[0])))
    image.paste(rain_graph, (0, c))
    c += rain_graph.size[1]

    forecast = get_forecast()
    image.paste(forecast, (0, c))
    c += forecast.size[1]

    draw.line([(0, c), (DIMENSIONS[0] - 1, c)], fill=0, width=2)
    c += 2

    tunnelbana = get_sl_tunnelbana()
    image.paste(tunnelbana, (0, c))
    c += tunnelbana.size[1]

    pendel = get_sl_pendel()
    image.paste(pendel, (0, c))
    c += pendel.size[1]

    bus = get_sl_bus()
    image.paste(bus, (0, c))
    c += bus.size[1]

    draw.line([(0, c), (DIMENSIONS[0] - 1, c)], fill=0, width=2)
    c += 2

    events = get_events()
    for e in events[0:5]:
        add_text_to_image(draw, e.name, 20, (240, c))
        c += add_text_to_image(draw, convert(e.start) + ":", 20, (20, c))

    #
    _waveshare.save_image_to_disk(image, "wip")
    #

    return image


@timeout(59)
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

