import re
from database import Database
from google_search import google_search
from general import get_html, similar
from thread_database import ThreadDb

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
    # Gets conferences from 2014 - 2019
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
    database = ThreadDb()
    print(conference)
    url = conference[0]
    conference_id = conference[1]
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
            database.add_paper(paper_title, conference_id)
    database.put_connection()


# def check_author(author_id):
#     db.c.execute("SELECT * FROM authors WHERE user_id=%s", (author_id,))
#     author = db.c.fetchone()
#     user_id = author[0]
#     first_name = author[1]
#     last_name = author[2]
#     url = author[3]
#     aff_id = author[4]
#     print(user_id, first_name, last_name, url, aff_id)
#     check_affiliation(aff_id)
#
#     try:
#         c.execute("INSERT INTO authors (user_id, first_name, last_name, url, affiliation_id) "
#                   "VALUES (%s, %s, %s, %s, %s)", (user_id, first_name, last_name, url, aff_id))
#         conn.commit()
#         print("Added to db!")
#     except p.IntegrityError:
#         conn.rollback()
#         print("Author already exists!")
#
#
# def check_affiliation(aff_id):
#     db.c.execute("SELECT * FROM affiliations WHERE id=%s", (aff_id,))
#     aff = db.c.fetchone()
#     id = aff[0]
#     name = aff[1]
#     country = aff[2]
#     print(id, name, country)
#
#     try:
#         c.execute("INSERT INTO affiliations (id, affiliation, country) VALUES (%s, %s, %s)", (id, name, country))
#         conn.commit()
#         print("Added aff to db!")
#     except p.IntegrityError:
#         conn.rollback()
#         print("Affiliation already exists!")
#
#
# db.c.execute("SELECT * FROM CONFERENCES WHERE id > 1737")
# conferences = db.c.fetchall()
#
# for conference in conferences:
#     conf_id = conference[0]
#     name = conference[1]
#     url = conference[2]
#     year = conference[3]
#     venue_id = conference[4]
#
#     c.execute("INSERT INTO conferences (id, name, url, year, venue_id) VALUES (%s, %s, %s, %s, %s)",
#               (conf_id, name, url, year, venue_id))
#     conn.commit()
#
#
# db.c.execute("SELECT * FROM PAPERS WHERE conference_id > 1737")
# papers = db.c.fetchall()
#
# for paper in papers:
#     paper_id = paper[0]
#     title = paper[1]
#     conference_id = paper[2]
#     db.c.execute("SELECT * FROM authors_papers WHERE paper_id=%s", (paper_id,))
#     author_ids = db.c.fetchall()
#
#     c.execute("INSERT INTO papers (id, title, conference_id) VALUES (%s, %s, %s)", (paper_id, title, conference_id))
#     conn.commit()
#
#     for ids in author_ids:
#         aut_id = ids[0]
#         check_author(aut_id)
#         c.execute("INSERT INTO authors_papers (author_id, paper_id) VALUES (%s, %s)", (aut_id, paper_id))
#         conn.commit()
