from g4f import set_cookies
import json
from collections import defaultdict


cookie_dict = defaultdict(lambda: {})

with open("./cookies.json") as f:
    cookies = json.load(f)
    for cookie in cookies:
        cookie_dict[cookie["domain"]][cookie["name"]] = cookie["value"]


for domain, cookies in cookie_dict.items():
    set_cookies(domain, cookies)
