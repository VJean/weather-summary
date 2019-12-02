#!/usr/bin/env python3
import sys, requests, pendulum, configparser
from pathlib import Path

config = configparser.ConfigParser()
conf_path = Path(__file__).parent / "config.ini"
conf_path = conf_path.resolve().as_posix()
config.read(conf_path)

if "lang" in config["DarkSky"]:
    pendulum.set_locale(config.get("DarkSky", "lang"))


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
    url = "https://api.darksky.net/forecast/{}/{},{}?lang={}&units={}&exclude=minutely,daily,flags".format(
        config["DarkSky"]["api_key"],
        config["DarkSky"]["lat"],
        config["DarkSky"]["lon"],
        config.get("DarkSky", "lang", fallback="en"),
        config.get("DarkSky", "units", fallback="auto"),
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

    title = f["hourly"]["summary"]
    message = ""
    timezone = f["timezone"]
    now = pendulum.now(timezone)
    summary = ...

    for hour in f["hourly"]["data"]:
        time = pendulum.from_timestamp(hour["time"], tz=timezone)
        # only take 24 hours of forecast
        if now.diff(time).in_hours() >= 24:
            break

        # skip until summary is different
        if summary == hour["summary"]:
            continue

        # summary changed, add new weather section to message
        summary = hour["summary"]
        message += time.to_datetime_string() + ": " + summary + "\n"

    notify(title, message)
