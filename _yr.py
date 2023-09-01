from capture_website import capture_screenshot
from _waveshare import save_image_to_disk, image_contrast


def get_current_weather():
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


def get_short_forecast():
    full = capture_screenshot("https://www.yr.no/en/forecast/graph/2-2670879/Sweden/Stockholm/Sundbyberg%20Municipality/Sundbyberg", size="495x1100")
    save_image_to_disk(full, "yr_full2")

    forecast = full.crop((0, 351, 480, 518))
    forecast = image_contrast(forecast, 180.0, 245.0)
    save_image_to_disk(forecast, "yr_forecast")

    return forecast
