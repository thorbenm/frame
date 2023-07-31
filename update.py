from PIL import Image, ImageDraw, ImageFont
import time
import datetime
from _waveshare import show_image


DIMENSIONS = (480, 800)
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


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

    image = image.transpose(Image.ROTATE_270)
    show_image(image)


if __name__ == "__main__":
    main()

