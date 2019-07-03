from general import similar
import psycopg2 as p

database = "rankecategorie"
user = "lucas"

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


class Database:

    def __init__(self):
        connection = "dbname=" + database + " user=" + user
        self.conn = p.connect(connection)
        self.c = self.conn.cursor()
        self.c.execute("SELECT * FROM venues")
        print(self.c.fetchall())

    def close_db(self):
        self.c.close()
        self.conn.close()

    def add_scholar_venue(self, name, category):
        # Adds entry into scholar venues table
        try:
            self.c.execute("INSERT INTO scholar_venues(name, category) VALUES (%s, %s)", (name, category))
            self.conn.commit()
        except p.IntegrityError:
            return

    def add_venue(self, name, url):
        # Adds entry into venues table
        try:
            self.c.execute("INSERT INTO venues(name,url) VALUES (%s,%s)", (name, url))
            self.conn.commit()
        except p.IntegrityError:
            return
            # print("Value " + url + " for: " + name + " already exists! Try again.")

    def add_conference_entry(self, name, url, year, venue_id):
        # Adds entry into conferences table
        try:
            # print(name)
            # print(url)
            # print(year)
            # print(venue_id)
            self.conn.rollback()
            self.c.execute("INSERT INTO conferences(name, url, year, venue_id) VALUES (%s,%s,%s,%s)", (name, url, year,
                                                                                                       venue_id))
            self.conn.commit()
        except p.IntegrityError:
            print("Value " + url + " for: " + name + " already exists! Try again.")

    def add_paper(self, title, conference_id):
        # Adds entry into papers table
        try:
            self.c.execute("INSERT INTO papers(title, conference_id) VALUES (%s,%s)", (title, conference_id))
            self.conn.commit()
            self.c.execute("SELECT id FROM papers WHERE title=%s", (title,))
            return self.c.fetchone()
        except p.IntegrityError:
            # print("Value " + title + " already exists! Try again.")
            self.conn.rollback()
            self.c.execute("SELECT id FROM papers WHERE title=%s", (title,))
            return self.c.fetchone()

    def update_affiliation(self, affiliation, country, id):
        # Updates affiliation
        try:
            self.c.execute("UPDATE affiliation SET affiliation=%s, location=%s WHERE id=%s", (affiliation, country, id))
            self.conn.commit()
        except p.IntegrityError:
            self.conn.rollback()
            print("Duplicate value for " + affiliation)

    def get_scholar_venues(self):
        # Gets all  scholar venues in categories relevant to this project
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
        # Get venues from database
        self.c.execute("SELECT url, id FROM venues ORDER BY id ASC")
        return self.c.fetchall()

    def get_papers(self):
        # Get papers from database
        self.c.execute("SELECT id, title FROM papers")
        return self.c.fetchall()

    def get_conference_entry_urls(self, venue_id):
        # Get conference urls from database
        self.c.execute("SELECT url, id FROM conferences WHERE venue_id=%s ORDER BY id ASC", (venue_id,))
        return self.c.fetchall()

    def get_affiliations(self):
        # Get affiliations from database
        self.c.execute("SELECT id, affiliation, country from affiliations")
        return self.c.fetchall()

    def get_universities(self):
        # Get universities from affiliations table from database
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

    def get_ranked_unis(self):
        # Get unis with a ranking from database
        self.c.execute("SELECT id, ranking FROM ranked_affiliations WHERE ranking IS NOT NULL")
        return self.c.fetchall()

    def get_author_from_paper(self, pid):
        # Gets the sum of scores for authors for a paper
        self.c.execute("SELECT sum(aff_ranking), count(user_id) FROM authors WHERE user_id IN"
                       "(SELECT author_id FROM authors_papers WHERE paper_id=%s) AND aff_ranking IS NOT NULL",
                       (pid,))
        return self.c.fetchall()[0]

    def get_conferences(self):
        # Get conferences from table
        self.c.execute("SELECT id, ranking, url FROM conferences ORDER BY id ASC")
        return self.c.fetchall()

    def get_confpaper_score(self, conf_id):
        # Gets the sum of paper scores for a conference
        self.c.execute(
            "SELECT SUM(ranking), count(ranking) FROM papers WHERE conference_id=%s AND ranking IS NOT NULL",
            (conf_id,))
        return self.c.fetchall()[0]

    def get_venues_ranking(self):
        # Gets the ranking from venues
        self.c.execute("SELECT id, ranking FROM venues")
        return self.c.fetchall()

    def get_venue_score(self, venue_id):
        # Gets sum of scores for conferences for a venue
        self.c.execute("SELECT sum(ranking), count(ranking) FROM conferences WHERE venue_id=%s and ranking IS NOT NULL",
                       (venue_id,))
        return self.c.fetchall()[0]

    def get_affiliation_ids(self):
        # Get the ids from the ranked affiliations
        self.c.execute("SELECT id from ranked_affiliations ORDER BY id ASC")
        return self.c.fetchall()

    def get_affiliation_score(self, aff_id):
        # Gets the sum of all venue scores where the affiliation has published a paper
        self.c.execute( "SELECT SUM(ranking), count(ranking) FROM venues WHERE id IN (SELECT venue_id from conferences "
                        "WHERE id IN (SELECT conference_id FROM papers WHERE id IN "
                        "(SELECT paper_id FROM authors_papers WHERE author_id IN "
                        "(SELECT user_id FROM authors WHERE affiliation_id=%s)))) "
                        "AND ranking is NOT NULL", (aff_id,))
        return self.c.fetchall()


def remove_duplicate_affiliations():
    # Removes all duplicate affiliations having the same name.
    conn = p.connect(database='rankedcategories', user='lucas')
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


def check_paper_counts():
    db = Database()
    # Checks all conferences for their affiliation paper counts. If count is too low, conference is removed from
    # consideration.
    db.c.execute("SELECT id FROM conferences ORDER BY ID ASC")
    conference_ids = db.c.fetchall()

    with open("docs/conference_counts.txt", 'a') as f:
        for id in conference_ids:
            paper_count = 0
            total_paper_count = 0

            print("CONF: " + str(id))
            db.c.execute("SELECT id FROM papers WHERE conference_id=%s ORDER BY ID ASC", (id,))
            paper_ids = db.c.fetchall()
            for pid in paper_ids:
                db.c.execute("SELECT 1 FROM authors_papers WHERE paper_id=%s", (pid,))
                if db.c.fetchall():
                    paper_count += 1
                total_paper_count += 1
            percentage = (paper_count / total_paper_count) * 100
            if percentage < 85:
                print("Number of present papers: " + str(percentage) + "%")
                f.write("Conference: " + str(id[0]) + " papers: " + str(percentage) + "%\n")

    f.close()

    with open('docs/conference_counts.txt', 'r') as f:
        for line in f:
            conf_id = line.split()[1]
            percentage = line.split()[3]
            percentage = percentage[:-1]
            if float(percentage) <= 30.0:
                print(conf_id)
                db.c.execute(
                    "DELETE FROM authors_papers WHERE paper_id IN (SELECT id from papers WHERE conference_id=%s)",
                    (conf_id,))
                db.conn.commit()
                db.c.execute("DELETE FROM papers WHERE conference_id=%s", (conf_id,))
                db.conn.commit()
                db.c.execute("DELETE FROM conferences WHERE id=%s", (conf_id,))
                db.conn.commit()
    f.close()
    db.close_db()
