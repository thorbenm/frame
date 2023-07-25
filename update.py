from PIL import Image, ImageDraw, ImageFont
import time
from _waveshare import show_image


DIMENSIONS = (480, 800)


def make_full_image():
    # Create an image and draw the current time on it using DejaVu Sans font
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    image = Image.new('1', DIMENSIONS, 255)  # 255: clear the frame
    draw = ImageDraw.Draw(image)
    current_time = time.strftime('%-I:%M')
    text_width, text_height = draw.textsize(current_time, font=ImageFont.truetype(font_path, 150))
    draw.text(((DIMENSIONS[0] - text_width) // 2, 20), current_time, font=ImageFont.truetype(font_path, 150), fill=0)
    
    current_date = time.strftime('%a, %Y-%-m-%-d (%U)')
    text_width, text_height = draw.textsize(current_date, font=ImageFont.truetype(font_path, 30))
    draw.text(((DIMENSIONS[0] - text_width) // 2, 10), current_date, font=ImageFont.truetype(font_path, 30), fill=0)
    
    image = image.transpose(Image.ROTATE_270)

    show_image(image)


if __name__ == "__main__":
    make_full_image()
