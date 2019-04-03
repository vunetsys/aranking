import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher


def get_html(url):
    page = requests.get(url)
    text = page.text
    return BeautifulSoup(text, "html.parser")


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()