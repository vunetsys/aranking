import requests
from bs4 import BeautifulSoup
from database import Database
from general import get_html

db = Database()
linkbase = 'https://scholar.google.nl'


def read_page(web_url, n):
    # Starts at input page, reads all links and saves conference names until depth n.
    n = n-1
    if n >= 0:
        s = get_html(web_url)
        for link in s.findAll('a'):
            link_url = link.get('href')
            if "/citations?" in link_url:
                read_page(linkbase+link_url, n)

    if n == 0:
        for titles in s.findAll('td', class_="gsc_mvt_t"):
            category = s.title.string[:-25]
            title = titles.string

            if category == "English" or category == "Engineering & Computer Science":
                continue

            db.add_scholar_venue(title, category)