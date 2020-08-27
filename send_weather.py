#!/usr/bin/env python3
import sys, requests, pendulum, configparser
from pathlib import Path

config = configparser.ConfigParser()
conf_path = Path(__file__).parent / "config.ini"
conf_path = conf_path.resolve().as_posix()
config.read(conf_path)

if "lang" in config["OpenWeather"]:
    pendulum.set_locale(config.get("OpenWeather", "lang"))


def notify(title, message):
    return requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": config["Pushover"]["APP_TOKEN"],
            "user": config["Pushover"]["USER_KEY"],
            "title": title,
            "message": message,
        },
    )


def get_forecast():
    url = "https://api.openweathermap.org/data/2.5/onecall?appid={}&lat={}&lon={}&units={}&lang={}&exclude=minutely,daily".format(
        config["OpenWeather"]["api_key"],
        config["OpenWeather"]["lat"],
        config["OpenWeather"]["lon"],
        config.get("OpenWeather", "units", fallback="metric"),
        config.get("OpenWeather", "lang", fallback="en"),
    )
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    else:
        # should log error
        return None


if __name__ == "__main__":
    f = get_forecast()
    if f is None:
        # should log
        print("Error when getting forecast")
        sys.exit(1)

    title = ",".join([c["description"] for c in f["current"]["weather"]])
    message = ""
    timezone = f["timezone"]
    now = pendulum.now(timezone)
    summary = ...

    for hour in f["hourly"]:
        time = pendulum.from_timestamp(hour["dt"], tz=timezone)
        # only take 24 hours of forecast
        if now.diff(time).in_hours() >= 24:
            break

        # skip until summary is different
        if summary == [hw["description"] for hw in hour["weather"]]:
            continue

        # summary changed, add new weather section to message
        summary = [hw["description"] for hw in hour["weather"]]
        message += time.to_datetime_string() + ": " + ", ".join(summary) + "\n"

    notify(title, message)
