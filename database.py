import sqlite3

# TABLE CREATION

# c.execute('''CREATE TABLE scholar_venues (name text UNIQUE, category text)''')

# c.execute('''CREATE TABLE venues
#          (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, url text UNIQUE)''')

# c.execute('''CREATE TABLE conferences (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, url text UNIQUE,
# year text, venue_id INTEGER, FOREIGN KEY(venue_id) REFERENCES venues(id)) ''')

# c.execute('''CREATE TABLE papers (id INTEGER PRIMARY KEY AUTOINCREMENT, title text UNIQUE,
# conference_id INTEGER, FOREIGN KEY(conference_id) REFERENCES conferences(id)) ''')
#
# c.execute('''CREATE TABLE authors (id INTEGER PRIMARY KEY AUTOINCREMENT, first_name text, middle_name text,
# last_name text, url text UNIQUE, affiliation text, place text) ''')
#
# c.execute('''CREATE TABLE authors_papers (author_id INTEGER NOT NULL, paper_id INTEGER NOT NULL,
# PRIMARY KEY(author_id, paper_id), FOREIGN KEY(author_id) REFERENCES authors(id),
# FOREIGN KEY(paper_id) REFERENCES papers(id))''')

# NOT USED
# c.execute('''CREATE TABLE journals (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, url text UNIQUE,
# year text, volume text UNIQUE, venue_id INTEGER, FOREIGN KEY(venue_id) REFERENCES venues(id)) ''')


class Database:

    def __init__(self):
        self.conn = sqlite3.connect('rankings.db', timeout=20)
        self.c = self.conn.cursor()

    def close_db(self):
        self.conn.close()

    def add_scholar_venue(self, name, category):
        try:
            self.c.execute("INSERT INTO scholar_venues(name, category) VALUES (?, ?)", (name, category))
            self.conn.commit()
        except sqlite3.IntegrityError:
            return

    def add_venue(self, name, url):
        try:
            self.c.execute("INSERT INTO venues(name,url) VALUES (?,?)", (name, url))
            self.conn.commit()
        except sqlite3.IntegrityError:
            return
            # print("Value " + url + " for: " + name + " already exists! Try again.")

    def add_conference_entry(self, name, url, year, venue_id):
        try:
            self.c.execute("INSERT INTO conferences(name,url, year, venue_id) VALUES (?,?,?,?)", (name, url, year,
                                                                                                  venue_id))
            self.conn.commit()
        except sqlite3.IntegrityError:
            print("Value " + url + " for: " + name + " already exists! Try again.")

    def add_paper(self, title, conference_id):
        try:
            self.c.execute("INSERT INTO papers(title, conference_id) VALUES (?,?)", (title, conference_id))
            self.conn.commit()
            self.c.execute("SELECT id FROM papers WHERE title=?", (title,))
            return self.c.fetchone()
        except sqlite3.IntegrityError:
            print("Value " + title + " already exists! Try again.")
            self.c.execute("SELECT id FROM papers WHERE title=?", (title,))
            return self.c.fetchone()

    def add_author(self, first_name, middle_name, last_name, url, affiliation, place):
        try:
            print("Trying:", first_name)
            self.c.execute('''INSERT INTO authors(first_name, middle_name, last_name, url, affiliation, place)
                           VALUES (?,?,?,?,?,?)''', (first_name, middle_name, last_name, url, affiliation, place))
            self.conn.commit()
            print("Added author: " + first_name + " " + last_name)
            self.c.execute("SELECT id FROM authors where url=?", (url,))
            return self.c.fetchone()
        except sqlite3.IntegrityError:
            print("Author:" + first_name + " " + last_name + " already exists! Try again.")
            self.c.execute("SELECT id FROM authors WHERE url=?", (url,))
            return self.c.fetchone()

    def add_author_paper(self, author_id, paper_id):
        try:
            self.c.execute("INSERT INTO authors_papers(author_id, paper_id) VALUES (?,?)", (author_id, paper_id))
            self.conn.commit()
        except sqlite3.IntegrityError:
            print("Record already exists! Try again.")

    def get_scholar_venues(self):
        self.c.execute('''SELECT name FROM scholar_venues WHERE (category = 'Artificial Intelligence'
                       OR category = 'Computational Linguistics' OR category = 'Computer Graphics' OR
                       category = 'Computer Hardware Design' OR category = 'Computer Networks & Wireless Communication' 
                       OR category = 'Computer Security & Cryptography' 
                       OR category = 'Computer Vision & Pattern Recognition' OR category = 'Computing Systems' 
                       OR category = 'Data Mining & Analysis' OR category = 'Databases & Information Systems' 
                       OR category = 'Human Computer Interaction' OR category = 'Multimedia' OR category = 'Robotics' 
                       OR category = 'Theoretical Computer Science') ''')
        return self.c.fetchall()

    def get_venues(self):
        self.c.execute("SELECT url, id FROM venues ORDER BY id ASC")
        return self.c.fetchall()

    def get_conference_entry_urls(self, venue_id):
        self.c.execute("SELECT url, id FROM conferences WHERE venue_id=? ORDER BY id ASC", (venue_id,))
        return self.c.fetchall()

    # def add_journal_entry(self, name, url, year, journal_id):
    #     try:
    #         self.c.execute("INSERT INTO journals(name, url, year, venue_id) VALUES (?,?,?,?)", (name, url, year,
    #                                                                                             journal_id))
    #         self.conn.commit()
    #     except sqlite3.IntegrityError:
    #         print("Value " + url + " for: " + name + " already exists! Try again.")

    # def get_journals(self):
    #     self.c.execute("SELECT url, id FROM venues WHERE type='Journal' and id > 177")
    #     return self.c.fetchall()


conn = sqlite3.connect("rankings.db")
c = conn.cursor()
conn.commit()
conn.close()
