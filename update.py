#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import os
from PIL import Image, ImageDraw, ImageFont
import time

# Modify the libdir variable to the correct path
libdir = "/home/pi/Programming/e-Paper/RaspberryPi_JetsonNano/python/lib"
if os.path.exists(libdir):
    sys.path.append(libdir)

try:
    # Rest of the code remains the same

    # Initialize the e-ink display
    from waveshare_epd import epd7in5_V2
    epd = epd7in5_V2.EPD()
    epd.init()
    # epd.Clear()

    # Create an image and draw the current time on it using DejaVu Sans font
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(image)
    current_time = time.strftime('%-I:%M')
    draw.text((10, 0), current_time, font=ImageFont.truetype(font_path, 150), fill=0)

    current_date = time.strftime('%Y-%-m-%-d')
    draw.text((100, 0), current_date, font=ImageFont.truetype(font_path, 30), fill=0)

    image = image.transpose(Image.ROTATE_270)

    # Display the image on the e-ink display
    epd.display(epd.getbuffer(image))

    # # Clear the display
    # epd.Clear()

    # Go to sleep
    epd.sleep()

except KeyboardInterrupt:
    epd7in5_V2.epdconfig.module_exit()
    exit()

