from PIL import Image, ImageDraw, ImageFont
import time
import datetime
import _waveshare
from capture_website import capture_screenshot
import numpy as np


DIMENSIONS = (480, 800)
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def get_yr():
    full = capture_screenshot("https://www.yr.no/en/forecast/daily-table/2-2670879/Sweden/Stockholm/Sundbyberg%20Municipality/Sundbyberg")
    _waveshare.save_image_to_disk(full, "yr_full")

    current_conditions = full.crop((330, 270, full.width - 1000, full.height - 750))
    current_conditions_arr = np.array(current_conditions).astype(float)
    current_conditions_arr -= np.min(current_conditions_arr)
    current_conditions_arr -= 100
    current_conditions_arr /= np.max(current_conditions_arr)
    current_conditions_arr *= 255.0
    current_conditions_arr = np.clip(current_conditions_arr, 0.0, 255.0)
    current_conditions = Image.fromarray(current_conditions_arr.astype(int))
    _waveshare.save_image_to_disk(current_conditions, "yr_current_conditions")

    rain_graph = full.crop((1210, 250, full.width - 360, full.height - 740))
    rain_graph_arr = np.array(rain_graph).astype(float)
    rain_graph_arr -= np.min(rain_graph_arr)
    rain_graph_arr -= 25
    rain_graph_arr /= np.max(rain_graph_arr)
    rain_graph_arr *= 255.0
    rain_graph_arr = np.clip(rain_graph_arr, 0.0, 255.0)
    rain_graph = Image.fromarray(rain_graph_arr.astype(int))
    _waveshare.save_image_to_disk(rain_graph, "yr_rain_graph")
    return current_conditions, rain_graph


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


    _waveshare.show_image(image)


if __name__ == "__main__":
    main()

