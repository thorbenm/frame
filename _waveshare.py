import sys
import os
import time
import datetime
from PIL import Image, ImageDraw, ImageFont


IMAGE_ARCHIVE_PATH = "/home/frame/image_archive/"
MAX_ARCHIVED_IMAGES = 50000


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


def generate_image_from_text(text, dimensions=(480, 800), font_size=12):
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    image = Image.new('1', dimensions, 255)
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), text,
              font=ImageFont.truetype(font_path, font_size),
              fill=0)
    return image
    

def show_text(text, font_size=12):
    show_image(generate_image_from_text(text, font_size=font_size))
