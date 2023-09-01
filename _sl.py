from capture_website import capture_screenshot
from _waveshare import save_image_to_disk, image_contrast



def crop_first_last_rows(image, top_rows=8, bottom_rows=8):
    width, height = image.size
    return image.crop((0, top_rows, width, height - bottom_rows))


ELEMENT_HEIGHT = 61
ELEMENT_SEPARATION = 8


def get_tunnelbana():
    tunnelbana_full = capture_screenshot("https://sl.se/?mode=departures&origName=Sundbybergs+station+%28Sundbyberg%29&origSiteId=9325&origPlaceId=QT0xQE89U3VuZGJ5YmVyZ3Mgc3RhdGlvbiAoU3VuZGJ5YmVyZylAWD0xNzk3MTQ5NUBZPTU5MzYwODcwQFU9NzRATD0zMDIxMDkzMjVAQj0xQA%3D%3D", size="495x1500", press_coordinates=(24, 920))
    save_image_to_disk(tunnelbana_full, "sl_tunnelbana_full")

    elements = list()
    offset = 1071
    elements.append(tunnelbana_full.crop((0, offset, 480, offset + ELEMENT_HEIGHT)))
    elements.append(tunnelbana_full.crop((0, offset + ELEMENT_SEPARATION + ELEMENT_HEIGHT, 480, offset + ELEMENT_SEPARATION + 2 * ELEMENT_HEIGHT)))
    save_image_to_disk(elements[0], "sl_tunnelbana_0")
    save_image_to_disk(elements[1], "sl_tunnelbana_1")

    kungstradgarden = min(elements, key=lambda img: sum(img.crop((154, 0, 260, img.size[1])).getdata()))
    kungstradgarden = image_contrast(kungstradgarden, 95.0, 241.0)
    kungstradgarden.paste(255, (0, 0, 11, kungstradgarden.height))
    kungstradgarden = crop_first_last_rows(kungstradgarden)
    save_image_to_disk(kungstradgarden, "sl_tunnelbana_kungstradgarden")

    return kungstradgarden


def get_pendel():
    pendel_full = capture_screenshot("https://sl.se/?mode=departures&origName=Sundbybergs+station+%28Sundbyberg%29&origSiteId=9325&origPlaceId=QT0xQE89U3VuZGJ5YmVyZ3Mgc3RhdGlvbiAoU3VuZGJ5YmVyZylAWD0xNzk3MTQ5NUBZPTU5MzYwODcwQFU9NzRATD0zMDIxMDkzMjVAQj0xQA%3D%3D", size="495x1500", press_coordinates=(308, 920))
    save_image_to_disk(pendel_full, "sl_pendel_full")

    elements = list()
    offset = 1071
    elements.append(pendel_full.crop((0, offset, 480, offset + ELEMENT_HEIGHT)))
    elements.append(pendel_full.crop((0, offset + ELEMENT_SEPARATION + ELEMENT_HEIGHT, 480, offset + ELEMENT_SEPARATION + 2 * ELEMENT_HEIGHT)))
    elements.append(pendel_full.crop((0, offset + 2 * ELEMENT_SEPARATION + 2 * ELEMENT_HEIGHT, 480, offset + 2 * ELEMENT_SEPARATION + 3 * ELEMENT_HEIGHT)))
    save_image_to_disk(elements[0], "sl_pendel_0")
    save_image_to_disk(elements[1], "sl_pendel_1")
    save_image_to_disk(elements[2], "sl_pendel_2")

    vasterhaninge = min(elements, key=lambda img: sum(img.crop((176, 0, 260, img.size[1])).getdata()))
    vasterhaninge = image_contrast(vasterhaninge, 115.0, 241.0)
    vasterhaninge.paste(255, (0, 0, 11, vasterhaninge.height))
    vasterhaninge = crop_first_last_rows(vasterhaninge)
    save_image_to_disk(vasterhaninge, "sl_pendel_vasterhanigne")

    return vasterhaninge


def get_bus():
    bus_full = capture_screenshot("https://sl.se/?mode=departures&origName=Tuletorget+%28Sundbyberg%29&origSiteId=3515&origPlaceId=QT0xQE89VHVsZXRvcmdldCAoU3VuZGJ5YmVyZylAWD0xNzk3NDcxM0BZPTU5MzY0ODA3QFU9NzRATD0zMDAxMDM1MTVAQj0xQA%3D%3D", size="495x1500")
    save_image_to_disk(bus_full, "sl_bus_full")

    offset = 1023
    bus_cropped = bus_full.crop((0, offset, 480, offset + ELEMENT_HEIGHT))
    bus_cropped = image_contrast(bus_cropped, 100.0, 240.0)
    bus_cropped = crop_first_last_rows(bus_cropped)

    save_image_to_disk(bus_cropped, "sl_bus_cropped")
    return bus_cropped
