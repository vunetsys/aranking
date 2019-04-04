from nameparser import HumanName
from general import get_html
import psycopg2
from psycopg2.pool import ThreadedConnectionPool


link_base_dblp = "https://dblp.org/search/venue/api?q="
filename = "crawled_conferences.txt"

DSN = "host='localhost' dbname='academicrankings' user='lucasfaijdherbe'"
tcp = ThreadedConnectionPool(1, 12, DSN)


def get_papers(conference, thread_id):
    database = ThreadDb()
    # print("Paper opened")
    with open(filename, 'r') as f:
        visited = f.read()
        f.close()

    url = conference[0]
    conference_id = conference[1]
    conf_id = str(conference_id)
    print("STARTING CONFERENCE WITH ID " + conf_id + " FOR THREAD " + str(thread_id))

    if conf_id not in visited:
        s = get_html(url)
        li = s.findAll("li", {"class": "entry inproceedings"})
        for l in li:
            divs = l.findAll("div", itemprop="headline")
            for d in divs:
                span = d.findAll("span", itemprop="author")
                title = d.find("span", {"class": "title"})
                paper_title = title.text.replace(".", "")
                print("FOR " + str(thread_id) + " Paper: " + paper_title)
                paper_id = database.add_paper(paper_title, conference_id)
                paper_id = paper_id[0]
                for sp in span:
                    name = sp.text
                    link = sp.find("a").get("href")
                    get_author(name, link, paper_id, database)
        print("THREAD " + str(thread_id) + " DONE")
        database.put_connection()
    else:
        print(str(conference_id) + " already visited!")
        print("THREAD " + str(thread_id) + " DONE")
        database.put_connection()


def get_author(name, url, paper_id, database):
    s = get_html(url)
    n = HumanName(name)
    first_name = n.first
    middle_name = n.middle
    last_name = n.last
    is_affiliated = s.find("li", itemprop="affiliation")

    if is_affiliated:
        affiliated_to = is_affiliated.find("span", itemprop="name")
        affiliation_id = database.add_affiliation(affiliated_to.text)
        author_id = database.add_author(first_name, middle_name, last_name, url, affiliation_id[0])
    else:
        author_id = database.add_author(first_name, middle_name, last_name, url, 0)
        # print("No affiliation for author with id", author_id[0])

    database.add_author_paper(author_id[0], paper_id)


class ThreadDb:
    def __init__(self):
        self.conn = tcp.getconn()
        self.c = self.conn.cursor()

    def put_connection(self):
        tcp.putconn(self.conn)

    def close_db(self):
        self.c.close()
        self.conn.close()

    def add_paper(self, title, conference_id):
        try:
            self.c.execute("INSERT INTO papers(title, conference_id) VALUES (%s,%s)", (title, conference_id))
            self.conn.commit()
            self.c.execute("SELECT id FROM papers WHERE title=%s", (title,))
            return self.c.fetchone()
        except psycopg2.IntegrityError:
            # print("Value " + title + " already exists! Try again.")
            self.conn.rollback()
            self.c.execute("SELECT id FROM papers WHERE title=%s", (title,))
            return self.c.fetchone()

    def add_affiliation(self, affiliation):
        try:
            print(affiliation)
            self.c.execute('''INSERT INTO affiliation(affiliation) VALUES (%s)''', (affiliation,))
            self.conn.commit()
            self.c.execute("SELECT id FROM affiliation WHERE affiliation=%s", (affiliation,))
            return self.c.fetchone()
        except psycopg2.IntegrityError:
            # print(affiliation + " already exists!")
            self.conn.rollback()
            self.c.execute("SELECT id FROM affiliation WHERE affiliation=%s", (affiliation,))
            return self.c.fetchone()

    def add_author(self, first_name, middle_name, last_name, url, aff_id):
        try:
            self.c.execute('''INSERT INTO authors(first_name, middle_name, last_name, url, affiliation_id)
                           VALUES (%s,%s,%s,%s,%s)''', (first_name, middle_name, last_name, url, aff_id))
            self.conn.commit()
            print("Added author: " + first_name + " " + last_name)
            self.c.execute("SELECT id FROM authors where url=%s", (url,))
            return self.c.fetchone()
        except psycopg2.IntegrityError:
            # print("Author:" + first_name + " " + last_name + " already exists! Try again.")
            self.conn.rollback()
            self.c.execute("SELECT id FROM authors WHERE url=%s", (url,))
            return self.c.fetchone()

    def add_author_paper(self, author_id, paper_id):
        try:
            self.c.execute("INSERT INTO authors_papers(author_id, paper_id) VALUES (%s,%s)", (author_id, paper_id))
            self.conn.commit()
        except psycopg2.IntegrityError:
            self.conn.rollback()
            # print("Record already exists! Try again.")
