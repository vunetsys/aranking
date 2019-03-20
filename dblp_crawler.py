import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
import re
from database import Database

db = Database()
link_base = "https://dblp.org/search/venue/api?q="

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def get_html(url):
    page = requests.get(url)
    text = page.text
    return BeautifulSoup(text, "html.parser")


def get_page(venue):
    s = get_html(link_base+venue)
    names = s.findAll("venue")
    hits = s.findAll("url")

    for hit in hits:
        if not hit.text.startswith("htt"):
            hits.remove(hit)

    potential_hits = []
    potential_venue_links = []
    solid_hit = 0

    for name, hit in zip(names, hits):

        if similarity(name.text, venue) > 0.8:
            if "/conf" in hit.text:
                db.add_venue(name.text, hit.text)
            solid_hit = 1
            break
        else:
            # FIX POTENTIAL HITS
            potential_hits.append("For " + venue + "Maybe: " + name.text)
            potential_hits.append(hit.text)

    if len(potential_hits) > 0 and solid_hit == 0:
        for hit in potential_hits:
            potential_venue_links.append(hit)
    return potential_venue_links


def convert_lines(venues):
    for v in venues:
        get_page(v)


def get_conferences():
    venues = db.get_venues()
    print(len(venues))
    for v in venues:
        venue_id = v[1]
        s = get_html(v[0])
        titles = s.findAll("span", {"class": "title"})
        contents = s.findAll("a", {"class": "toc-link"})

        for title, content in zip(titles, contents):
            conference = title.text
            url = content.get('href')
            regex = re.compile(r'^(.*?(201[4-9])[^$]*)$')

            if regex.match(conference):
                search = re.search(r'\d{4}', conference)
                year = search.group()
                db.add_conference_entry(conference, url, year, venue_id)


def get_yearly_conferences(conf_id):
    return db.get_conference_entry_urls(conf_id)


def add_author(name, url, paper_title):
    s = get_html(url)
    print("Author:", name)
    affiliation = s.find("li", itemprop="affiliation")
    if affiliation:
        print(affiliation.text)
    else:
        print("No Affiliation found")


# def get_journals():
#     journals = db.get_journals()
#     for j in journals:
#         journal_id = j[1]
#         print(journal_id)
#         s = get_html(j[0])
#         url_string = j[0].replace("/", "\/")
#         url_string = url_string.replace(".", "\.")
#         regex = "(" + url_string + ")((?:[a-z][a-z0-9_]*))"
#         regex = re.compile(r'{}'.format(regex))
#         links = s.findAll("a")
#         print(j[0])
#         for l in links:
#             if l.string:
#                 if regex.match(l.get('href')):
#                     url = l.get('href')
#                     title = l.string
#                     year = get_journal_year(url)
#                     db.add_journal_entry(title, url, year, journal_id)
#
#
# def get_journal_year(url):
#     print(url)
#     s = get_html(url)
#     try:
#         title = s.h2.text
#         regex = re.compile(r'\b(19|20)\d{2}\b')
#         return regex.search(title)[0]
#     except AttributeError:
#         print(s.h1)
#         title = s.h1.text
#         regex = re.compile(r'\b(19|20)\d{2}\b')
#         return regex.search(title)[0]

    # print(links)
    # for j in journals:
        # journal_id = j[1]
        # s = get_html(j[0])
        # print(s.prettify())
