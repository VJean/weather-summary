#!/usr/bin/env python3
import requests

import configparser

config = configparser.ConfigParser()
config.read('config.ini')

def notify(message):
    return requests.post("https://api.pushover.net/1/messages.json", data = {
        "token": config['Pushover']['APP_TOKEN'],
        "user": config['Pushover']['USER_KEY'],
        "message": "hello world"
    })

def get_forecast():
    url = "https://api.darksky.net/forecast/{}/{},{}?lang={}".format(config['DarkSky']['api_key'],config['DarkSky']['lat'],config['DarkSky']['lon'],config.get('DarkSky','lang',fallback='en'))
    return requests.get(url)
