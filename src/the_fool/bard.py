import requests
import json
from bardapi import BardCookies

cookie_dict = {}

session = requests.Session()
with open("./cookies.json") as f:
    cookies = json.load(f)
    for cookie in cookies:
        cookie_dict[cookie["name"]] = cookie["value"]
        session.cookies.set(cookie["name"], cookie["value"])


bard_instance = BardCookies(cookie_dict=cookie_dict)
