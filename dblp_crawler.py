import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
import re
from database import Database
from google_search import google_search

db = Database()
link_base_dblp = "https://dblp.org/search/venue/api?q="
seen_conferences = set()

'''
TO DO:
- Implement set to check for visited urls
- Change authors method to check for data in acm & ieee
'''


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def get_html(url):
    page = requests.get(url)
    text = page.text
    return BeautifulSoup(text, "html.parser")


def get_scholar_venues():
    venues = db.get_scholar_venues()

    for v in venues:
        venue = v[0]
        if "Journal" in venue:
            continue

        s = get_html(link_base_dblp + venue)
        names = s.findAll("venue")
        hits = s.findAll("url")

        for h in hits:
            if not h.text.startswith("htt"):
                hits.remove(h)

        solid_hit = 0

        for name, hit in zip(names, hits):
            title = name.text
            url = hit.text

            similarity = similar(venue, title)
            if similarity >= 0.8:
                solid_hit = 1
                if "/conf" in url:
                    db.add_venue(title, url)
                    break

        if solid_hit == 0:
            searching_term = "dblp " + venue
            search_results = google_search(searching_term)
            urls = []
            for result in search_results:
                url = result['link']
                if url.endswith("/index"):
                    if "/conf" in url:
                        db.add_venue(venue, url)
                    break
                urls.append(url)

            print("No match for", venue)
            for url in urls:
                # For last resort manual adding
                if "https://dblp.org/db/conf" in url:
                    print(url)


def get_conferences():
    venues = db.get_venues()

    for v in venues:
        venue_id = v[1]
        url = v[0]
        print(venue_id)
        s = get_html(url)
        titles = s.findAll("span", {"class": "title"})
        contents = s.findAll("a", {"class": "toc-link"})

        for title, content in zip(titles, contents):
            conference = title.text.replace(".", "")
            url = content.get('href')
            regex = re.compile(r'^(.*?(201[4-9])[^$]*)$')

            if regex.match(conference):
                print(conference)
                search = re.search(r'\d{4}', conference)
                year = search.group()
                db.add_conference_entry(conference, url, year, venue_id)


def get_yearly_conferences(conf_id):
    return db.get_conference_entry_urls(conf_id)


def get_author(title, paper_id):
    return
    # db.add_author_paper(author_id[0], paper_id)

    # s = get_html(url)
    # n = HumanName(name)
    # first_name = n.first
    # middle_name = n.middle
    # last_name = n.last
    # affiliation = None
    # location = None
    # is_affiliated = s.find("li", itemprop="affiliation")
    # if is_affiliated:
    #     affiliated_to = is_affiliated.find("span", itemprop="name")
    #     location = affiliated_to.text.split(",")
    #     if len(location) == 1:
    #         affiliation = location[0]
    #         location = None
    #     else:
    #         affiliation = location[0]
    #         place = location[1:]
    #         location = ",".join(place)
    #
    # author_id = database.add_author(first_name, middle_name, last_name, url, affiliation, location)
    # database.add_author_paper(author_id[0], paper_id)


def get_papers(conferences):
    for c in conferences:
        if c[0] not in seen_conferences:
            url = c[0]
            conference_id = c[1]
            print(conference_id)
            s = get_html(url)
            li = s.findAll("li", {"class": "entry inproceedings"})
            for l in li:
                divs = l.findAll("div", itemprop="headline")
                for d in divs:
                    # span = d.findAll("span", itemprop="author")
                    title = d.find("span", {"class": "title"})
                    paper_title = title.text.replace(".", "")
                    print(paper_title)
                    paper_id = db.add_paper(paper_title, conference_id)
                    # paper_id = paper_id[0]
                    # get_author(paper_title, paper_id)
                    # for sp in span:
                    #     name = sp.text
                    #     link = sp.find("a").get("href")
                    #     get_author(name, link, paper_id, db)
            seen_conferences.add(url)

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