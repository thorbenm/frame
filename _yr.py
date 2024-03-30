from capture_website import capture_screenshot, capture_text, capture_pdf
from _waveshare import save_image_to_disk, image_contrast
import re


def get_current_weather_image():
    full = capture_screenshot("https://www.yr.no/en/forecast/daily-table/2-2670879/Sweden/Stockholm/Sundbyberg%20Municipality/Sundbyberg")
    save_image_to_disk(full, "yr_full")

    current_conditions = full.crop((330, 267, full.width - 1000, full.height - 757))
    current_conditions = image_contrast(current_conditions, 200.0, 255.0)
    save_image_to_disk(current_conditions, "yr_current_conditions")

    rain_graph = full.crop((1210, 250, full.width - 360, full.height - 740))
    rain_graph = image_contrast(rain_graph, 150.0, 255.0)
    save_image_to_disk(rain_graph, "yr_rain_graph")
    current_conditions = current_conditions.resize((480, round(current_conditions.size[1] * 480 / current_conditions.size[0])))
    rain_graph = rain_graph.resize((480, round(rain_graph.size[1] * 480 / rain_graph.size[0])))
    return current_conditions, rain_graph


def get_short_forecast_image():
    full = capture_screenshot("https://www.yr.no/en/forecast/graph/2-2670879/Sweden/Stockholm/Sundbyberg%20Municipality/Sundbyberg", size="495x1100")
    save_image_to_disk(full, "yr_full2")

    forecast = full.crop((0, 361, 480, 528))
    forecast = image_contrast(forecast, 180.0, 245.0)
    save_image_to_disk(forecast, "yr_forecast")

    return forecast


def get_long_forecast_text():
    text = capture_text("https://www.yr.no/en/forecast/daily-table/2-2670879/Sweden/Stockholm/Sundbyberg%20Municipality/Sundbyberg")

    pattern = re.compile(
        r'([A-Za-z]+ \d+ [A-Za-z]+)\.\s*'  # Date
        r'Maximum minimum temperature:\s*'
        r'(\d+°/\d+°)\s*'  # Temperature high/low
        r'(?:Precipitation\s*'
        r'(\d+\.\d+mm)\s*)?'  # Precipitation
        r'Wind:\s*'
        r'(\d+)\s*m/s'  # Wind
    , re.MULTILINE)

    matches = pattern.findall(text)

    ret = list()
    for match in matches:
        element = lambda: None
        date, temp_high_low, precipitation, wind = match
        if not precipitation:
            precipitation = "0mm"
        element.date = date
        element.temp_high_low = temp_high_low

        precipitation = precipitation.removesuffix("mm")
        precipitation = str(round(float(precipitation)))

        element.precipitation = precipitation
        element.wind = wind
        ret.append(element)
    return ret


def get_long_forecast_icons():
    full = capture_pdf("https://www.yr.no/en/print/forecast/2-2670879/Sweden/Stockholm/Sundbyberg%20Municipality/Sundbyberg")
    full = full.convert("L")
    save_image_to_disk(full, "long_forecast_full")
    offset_x = 632
    offset_y = 1342
    element_size_x = 60
    element_size_y = 60
    separation_y = 23.5
    ret = []
    for j in range(8):
        left = offset_x
        top = offset_y + round(j * (element_size_y + separation_y))
        right = left + element_size_x
        bottom = top + element_size_y
        icon = full.crop((left, top, right, bottom))
        icon = image_contrast(icon, 200.0, 255.0)
        icon = icon.resize((30, 30))
        ret.append(icon)
        save_image_to_disk(ret[-1], "long_forecast_icon_" + str(len(ret)))
    return ret
