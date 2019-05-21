import requests
import json
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from time import sleep


def get_json(url):
    page = requests.get(url)
    text = page.text
    return json.loads(text)


def get_html(url):
    try:
        page = requests.get(url)
        if str(page.status_code) == "429":
            raise TooManyRequests
        text = page.text
        # sleep(1)
        return BeautifulSoup(text, "html.parser")
    except TooManyRequests:
        print("Error! Too many requests to url " + url + "  for thread: " + str(thread_id) +
              ". Trying again in 4 mins.")
        sleep(300)
        return get_html(url)


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


class Error(Exception):
    """Base class"""
    pass


class TooManyRequests(Error):
    """For HTTP STATUS CODE 429"""
    pass
