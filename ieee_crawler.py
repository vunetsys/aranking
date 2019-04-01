import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
import re
from error import AuthorError

link_base_ieee = "https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText="
api_key = "qfyrt56natmrxkbwsneunrqw"


def get_html(url):
    page = requests.get(url)
    text = page.text
    return BeautifulSoup(text, "html.parser")


def get_ieee_author(title, paper_id, db):
    url = link_base_ieee + title
    s = get_html(url)


