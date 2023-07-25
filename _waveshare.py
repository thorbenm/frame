import sys
import os
import time
from PIL import Image, ImageDraw, ImageFont


IMAGE_ARCHIVE_PATH = "/home/pi/image_archives/"
MAX_ARCHIVED_IMAGES = 1440


def save_image_to_disk(image):
    current_datetime = time.strftime('%Y_%m_%d__%H_%M_%S')
    file_name = f"{current_datetime}.png"
    file_path = os.path.join(IMAGE_ARCHIVE_PATH, file_name)

    image.transpose(Image.ROTATE_90).save(file_path)


def delete_old_images():
    while True:
        existing_images = sorted(os.listdir(IMAGE_ARCHIVE_PATH))
        num_existing_images = len(existing_images)

        if num_existing_images <= MAX_ARCHIVED_IMAGES:
            break

        oldest_image = existing_images[0]
        oldest_image_path = os.path.join(IMAGE_ARCHIVE_PATH, oldest_image)
        os.remove(oldest_image_path)


def show_image(image):
    save_image_to_disk(image)
    delete_old_images()

    libdir = "/home/pi/Programming/e-Paper/RaspberryPi_JetsonNano/python/lib"
    if os.path.exists(libdir):
        sys.path.append(libdir)
    
    try:
        from waveshare_epd import epd7in5_V2
        epd = epd7in5_V2.EPD()
        epd.init()
        # epd.Clear()
    
        epd.display(epd.getbuffer(image))
        epd.sleep()
    
    except KeyboardInterrupt:
        epd7in5_V2.epdconfig.module_exit()
        exit()
    

def show_text(text, font_size=12):
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    image = Image.new('1', (480, 800), 255)
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), text,
              font=ImageFont.truetype(font_path, font_size),
              fill=0)
    
    image = image.transpose(Image.ROTATE_270)
    show_image(image)
