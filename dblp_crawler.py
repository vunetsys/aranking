import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
import re
from database import Database

db = Database()


def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def get_page(journal, line):
    web_url = link_base+line
    page = requests.get(web_url)
    text = page.text
    s = BeautifulSoup(text, "html.parser")
    names = s.findAll("venue")
    hits = s.findAll("url")

    for hit in hits:
        if not hit.text.startswith("htt"):
            hits.remove(hit)

    potential_hits = []
    potential_venue_links = []
    solid_hit = 0

    for name, hit in zip(names, hits):

        if similarity(name.text, journal) > 0.8:
            if "/conf" in hit.text:
                db.add_venue(name.text, hit.text, "Conference")
            else:
                db.add_venue(name.text, hit.text, "Journal")
            solid_hit = 1
            break
        else:
            # FIX POTENTIAL HITS
            potential_hits.append("For " + journal + "Maybe: " + name.text)
            potential_hits.append(hit.text)

    if len(potential_hits) > 0 and solid_hit == 0:
        for hit in potential_hits:
            potential_venue_links.append(hit)
    return potential_venue_links


def convert_lines(journals):
    for line in journals:
        url = line.split(" ")
        url = "+".join(url)
        get_page(line, url)


def get_conferences():
    conferences = db.get_conferences()
    for c in conferences:
        conference_id = c[1]

        page = requests.get(c[0])
        text = page.text
        s = BeautifulSoup(text, "html.parser")
        titles = s.findAll("span", {"class": "title"})
        contents = s.findAll("a", {"class": "toc-link"})

        for title, content in zip(titles, contents):
            conference = title.text
            url = content.get('href')
            if re.match(r'^(.*?(201[4-9])[^$]*)$', conference):
                search = re.search(r'\d{4}', conference)
                year = search.group()
                db.add_conference_entry(conference, url, year, conference_id)


link_base = "https://dblp.org/search/venue/api?q="
