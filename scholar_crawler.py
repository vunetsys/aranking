import requests
import re
from bs4 import BeautifulSoup

linkbase = 'https://scholar.google.nl'
f = open("scholarJournals3.txt", "w+")


def read_page(web_url, n):
    n = n-1
    if n >= 0:
        url = web_url
        page = requests.get(url)
        text = page.text
        s = BeautifulSoup(text, "html.parser")
        print(s.title.string)
        f.write(s.title.string)
        for link in s.findAll('a'):
            link_url = link.get('href')
            if "/citations?" in link_url:
                read_page(linkbase+link_url, n)
                f.write("\n")

        for titles in s.findAll('td', class_="gsc_mvt_t"):
            f.write(titles.string + "\n")


# read_page(linkbase + '/citations?view_op=top_venues&hl=en&vq=eng', 2)
# f.close()