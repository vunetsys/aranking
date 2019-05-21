import psycopg2 as p
from general import similar

# TABLE CREATION

# c.execute('''CREATE TABLE scholar_venues (name text UNIQUE, category text)''')

# c.execute('''CREATE TABLE venues
#          (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, url text UNIQUE)''')

# c.execute('''CREATE TABLE conferences (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, url text UNIQUE,
# year text, venue_id INTEGER, FOREIGN KEY(venue_id) REFERENCES venues(id)) ''')

# c.execute('''CREATE TABLE papers (id INTEGER PRIMARY KEY AUTOINCREMENT, title text UNIQUE,
# conference_id INTEGER, FOREIGN KEY(conference_id) REFERENCES conferences(id)) ''')
#
# c.execute('''CREATE TABLE affiliation (id INTEGER PRIMARY KEY AUTOINCREMENT, affiliation text UNIQUE,
# location text)''')
#
# c.execute('''CREATE TABLE authors (id INTEGER PRIMARY KEY AUTOINCREMENT, first_name text, middle_name text,
# last_name text, url text UNIQUE, affiliation_id INTEGER, FOREIGN KEY(affiliation_id) REFERENCES affiliation(id)) '''))
#
# c.execute('''CREATE TABLE authors_papers (author_id INTEGER NOT NULL, paper_id INTEGER NOT NULL,
# PRIMARY KEY(author_id, paper_id), FOREIGN KEY(author_id) REFERENCES authors(id),
# FOREIGN KEY(paper_id) REFERENCES papers(id))''')
#
# c.execute('''CREATE TABLE ranking_lists (id INTEGER PRIMARY KEY, name text UNIQUE, qs_rank text, the_rank text,
# shanghai_rank text)''')
#
# db.c.execute('''CREATE TABLE ranked_affiliations (id INTEGER PRIMARY KEY UNIQUE, affiliation text UNIQUE,
# location text, ranking INTEGER)''')

# NOT USED
# c.execute('''CREATE TABLE journals (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, url text UNIQUE,
# year text, volume text UNIQUE, venue_id INTEGER, FOREIGN KEY(venue_id) REFERENCES venues(id)) ''')




def remove_duplicate_affiliations():
    conn = p.connect(database='academicrankings', user='lucasfaijdherbe')
    c = conn.cursor()

    c.execute("select affiliation, country from affiliations group by affiliation, "
              "country having count(*) > 1 order by country asc")

    double_values = c.fetchall()

    for value in double_values:
        affiliation = value[0]
        country = value[1]
        c.execute("SELECT id FROM affiliations WHERE affiliation=%s AND country=%s", (affiliation, country))
        ids = c.fetchall()

        new_id = ids[0][0]

        for id in ids[1:]:
            old_id = id[0]
            c.execute("UPDATE authors SET affiliation_id=%s WHERE affiliation_id=%s", (new_id, old_id))
            c.execute("DELETE FROM affiliations where id=%s", (old_id,))
            conn.commit()

    c.execute("SELECT DISTINCT country from affiliations")
    countries = c.fetchall()

    count = 0
    for country in countries:
        # print(country[0])
        c.execute("SELECT * FROM affiliations WHERE country=%s ORDER BY affiliation ASC", (country[0],))
        affiliations = c.fetchall()
        if len(affiliations) > 1:
            for aff in affiliations:
                current_id = aff[0]
                current_affiliation = aff[1]
                # print(current_affiliation)
                for other_aff in affiliations:
                    other_id = other_aff[0]
                    other_affiliation = other_aff[1]
                    if similar(other_affiliation, current_affiliation) >= 0.95 and current_id != other_id:
                        # print(current_affiliation + " matches: " + other_affiliation[1])
                        c.execute("UPDATE authors SET affiliation_id=%s WHERE affiliation_id=%s",
                                     (current_id, other_id))
                        c.execute("DELETE FROM affiliations where id=%s", (other_id,))
                        conn.commit()
                        affiliations.remove(other_aff)
                        count += 1
                        print(
                            "DELETED AFFILIATION: " + other_affiliation + " AND REPLACED WITH: " + current_affiliation)
    print(count)


class Database:

    def __init__(self):
        self.conn = p.connect(database='academicrankings', user='lucasfaijdherbe')
        self.c = self.conn.cursor()
        # self.conn = sqlite3.connect('rankings.db', timeout=20, check_same_thread=False)
        # self.c = self.conn.cursor()
        # self.c.execute("PRAGMA journal_mode=WAL;")
        # self.conn.commit()

    def close_db(self):
        self.c.close()
        self.conn.close()

    def add_scholar_venue(self, name, category):
        try:
            self.c.execute("INSERT INTO scholar_venues(name, category) VALUES (%s, %s)", (name, category))
            self.conn.commit()
        except p.IntegrityError:
            return

    def add_venue(self, name, url):
        try:
            self.c.execute("INSERT INTO venues(name,url) VALUES (%s,%s)", (name, url))
            self.conn.commit()
        except p.IntegrityError:
            return
            # print("Value " + url + " for: " + name + " already exists! Try again.")

    def add_conference_entry(self, name, url, year, venue_id):
        try:
            self.c.execute("INSERT INTO conferences(name,url, year, venue_id) VALUES (%s,%s,%s,%s)", (name, url, year,
                                                                                                      venue_id))
            self.conn.commit()
        except p.IntegrityError:
            print("Value " + url + " for: " + name + " already exists! Try again.")

    def update_affiliation(self, affiliation, country, id):
        try:
            self.c.execute("UPDATE affiliation SET affiliation=%s, location=%s WHERE id=%s", (affiliation, country, id))
            self.conn.commit()
        except p.IntegrityError:
            self.conn.rollback()
            print("Duplicate value for " + affiliation)

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

    def get_papers(self):
        self.c.execute("SELECT id, title FROM papers where id < 2171")
        return self.c.fetchall()

    def get_conference_entry_urls(self, venue_id):
        self.c.execute("SELECT url, id FROM conferences WHERE venue_id=%s ORDER BY id ASC", (venue_id,))
        return self.c.fetchall()

    def get_affiliations(self):
        self.c.execute("SELECT id, affiliation, country from affiliations")
        return self.c.fetchall()

    def get_universities(self):
        self.c.execute("select * from affiliations where affiliation like '%University%' OR affiliation like "
                       "'%Universidad%' or affiliation like '%Université%' or affiliation like '%Universiteti%' "
                       "or affiliation like '%Universiti%' or affiliation like'%College%' or affiliation like "
                       "'%Universitaria%' or affiliation like '%Academy%' or affiliation like '%Faculty%' or "
                       "affiliation like '%Universidade%' or affiliation like '%Instituto%' or affiliation like "
                       "'%Universität%' or affiliation like '%Universitat%' or affiliation like '%Universitatea%' "
                       "or affiliation like '%Universitetas%' or affiliation like '%Univeristà%' or affiliation like "
                       "'%Egyetem%' or affiliation like '%Ecole%' or affiliation like '%Univerzita%' or affiliation "
                       "like '%Universiteti%' or affiliation like '%Institute of Technology%' or affiliation like "
                       "'%Üniversitesi%' order by country, affiliation asc")
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

#


# db = Database()
# db.c.execute("ALTER TABLE ranked_affiliations ALTER COLUMN ranking TYPE float8")
# db.conn.commit()
