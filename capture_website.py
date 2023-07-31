from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from io import BytesIO
from PIL import Image

def capture_screenshot(url, size="1920x1080", wait=10):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"--window-size={size}")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    driver.implicitly_wait(wait)

    screenshot_bytes = driver.get_screenshot_as_png()
    driver.quit()
    greyscale = Image.open(BytesIO(screenshot_bytes)).convert('L')
    return greyscale


