from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from io import BytesIO
from PIL import Image
import requests
from pdf2image import convert_from_path, convert_from_bytes


def capture_screenshot(url, size="1920x1080", wait=10, press_coordinates=None):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"--window-size={size}")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    driver.implicitly_wait(wait)

    if press_coordinates is not None:
        action = webdriver.common.action_chains.ActionChains(driver)
        action.move_by_offset(*press_coordinates)
        action.click()
        action.perform()
        driver.implicitly_wait(wait)

    screenshot_bytes = driver.get_screenshot_as_png()
    driver.quit()
    greyscale = Image.open(BytesIO(screenshot_bytes)).convert('L')
    return greyscale


def capture_text(url, size="1920x1080", wait=10):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"--window-size={size}")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    driver.implicitly_wait(wait)

    body_text = driver.find_element(By.TAG_NAME, "body").text

    driver.quit()
    return body_text


def capture_pdf(url):
    response = requests.get(url)
    pdf_bytes = BytesIO(response.content)
    images = convert_from_bytes(pdf_bytes.read())
    return images[0]  # Return the first page as PIL image object
