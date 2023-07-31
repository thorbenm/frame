from PIL import Image, ImageDraw, ImageFont
import time
import datetime
import _waveshare
from capture_website import capture_screenshot
import numpy as np


DIMENSIONS = (480, 800)
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def get_yr():
    yr_full = capture_screenshot("https://www.yr.no/en/forecast/daily-table/2-2670879/Sweden/Stockholm/Sundbyberg%20Municipality/Sundbyberg")
    _waveshare.save_image_to_disk(yr_full, "yr_full")

    yr_current_conditions = yr_full.crop((330, 270, yr_full.width - 1000, yr_full.height - 750))
    arr = np.array(yr_current_conditions).astype(float)
    arr -= np.min(arr)
    arr -= 100
    arr /= np.max(arr)
    arr *= 255.0
    arr = np.clip(arr, 0.0, 255.0)
    yr_current_conditions = Image.fromarray(arr.astype(int))
    _waveshare.save_image_to_disk(yr_current_conditions, "yr_current_conditions")

    return yr_current_conditions


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

    yr = get_yr()
    yr = yr.resize((480, round(yr.size[1] * 480 / yr.size[0])))

    image.paste(yr, (0, 200))

    _waveshare.show_image(image)


if __name__ == "__main__":
    main()

