import requests

def get():
    t = requests.get("https://sv.seatemperature.net/current/sweden/stockholm-stockholm-sweden").text
    match_before = "temp1\'><h3>"
    match_after = "<span id="
    temp = t[t.find(match_before):t.find(match_after)][len(match_before):]
    return temp + "°C"


if __name__ == "__main__":
    print(get())
