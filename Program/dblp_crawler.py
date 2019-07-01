import re
from database import Database
from google_search import google_search
from general import get_html, similar


db = Database()
link_base_dblp = "https://dblp.org/search/venue/api?q="
filename = "crawled_conferences.txt"


def get_scholar_venues():
    # Searches for all venues gotten through google scholar on dblp.
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
    # Gets conferences from 2014 - 2019 (Regex determines the year span)
    venues = db.get_venues()

    for v in venues:
        venue_id = v[0]
        url = v[1]
        print(venue_id)
        print(url)
        s = get_html(url)
        titles = s.findAll("span", {"class": "title"})
        contents = s.findAll("a", {"class": "toc-link"})

        for title, content in zip(titles, contents):
            conference = title.text.replace(".", "")
            url = content.get('href')
            regex = re.compile(r'^(.*?(201[4-9])[^$]*)$')

            if regex.match(conference):
                # print(conference)
                search = re.search(r'\d{4}', conference)
                year = search.group()
                db.add_conference_entry(conference, url, year, venue_id)


def get_yearly_conferences(conf_id):
    return db.get_conference_entry_urls(conf_id)


def get_papers(conference):
    # Gets all paper titles through dblp
    print(conference)
    url = conference[2]
    conference_id = conference[0]
    conf_id = str(conference_id)
    print("STARTING CONFERENCE WITH ID " + conf_id)

    s = get_html(url)
    li = s.findAll("li", {"class": "entry inproceedings"})
    for l in li:
        divs = l.findAll("div", itemprop="headline")
        for d in divs:
            # span = d.findAll("span", itemprop="author")
            title = d.find("span", {"class": "title"})

            paper_title = title.text.replace(".", "")
            print(paper_title)
            db.add_paper(paper_title, conference_id)
