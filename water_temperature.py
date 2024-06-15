import requests
import re


def get():
    url = "https://www.allabadplatser.se/a/stockholms-lan/stockholm/malaren-smedsuddsbadet-v/1411/"
    response = requests.get(url)
    if response.status_code == 200:
        content = response.text
        match = re.search(r'temperatur via satellit var <strong>([\d,]+°C)</strong> upp', content)
        if match:
            return match.group(1).replace(",", ".")
    return None


if __name__ == "__main__":
    print(get())
