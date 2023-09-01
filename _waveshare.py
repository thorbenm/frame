import sys
import os
import time
import datetime
from PIL import Image, ImageDraw, ImageFont


IMAGE_ARCHIVE_PATH = "/home/frame/image_archive/"
MAX_ARCHIVED_IMAGES = 50000
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DIMENSIONS = (480, 800)


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


def save_image_to_disk(image, name):
    current_datetime = datetime.datetime.now().strftime('%Y_%m_%d__%H_%M_%S_%f')
    file_name = f"{current_datetime}__{name}.png"
    file_path = os.path.join(IMAGE_ARCHIVE_PATH, file_name)

    image.save(file_path)


def purge_images():
    while True:
        existing_images = sorted(os.listdir(IMAGE_ARCHIVE_PATH))
        num_existing_images = len(existing_images)

        if num_existing_images <= MAX_ARCHIVED_IMAGES:
            break

        oldest_image = existing_images[0]
        oldest_image_path = os.path.join(IMAGE_ARCHIVE_PATH, oldest_image)
        os.remove(oldest_image_path)


def show_image(image):
    save_image_to_disk(image, "final")
    purge_images()

    libdir = "/home/frame/Programming/e-Paper/RaspberryPi_JetsonNano/python/lib"
    sys.path.append(libdir)
    
    try:
        from waveshare_epd import epd7in5_V2
        epd = epd7in5_V2.EPD()
        epd.init()
        # epd.Clear()
    
        epd.display(epd.getbuffer(image.transpose(Image.ROTATE_270)))
        epd.sleep()
    
    except KeyboardInterrupt:
        epd7in5_V2.epdconfig.module_exit()
        exit()


def generate_image_from_text(text, dimensions=None, font_size=12):
    if dimensions is None:
        dimensions = DIMENSIONS
    image = Image.new('1', dimensions, 255)
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), text,
              font=ImageFont.truetype(FONT, font_size),
              fill=0)
    return image
    

def show_text(text, font_size=12):
    show_image(generate_image_from_text(text, font_size=font_size))
