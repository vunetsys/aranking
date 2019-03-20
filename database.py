import sqlite3

# TABLE CREATION
# c.execute('''CREATE TABLE venues
#          (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, url text UNIQUE, type text)''')

# c.execute('''CREATE TABLE conferences (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, url text UNIQUE,
# year text, venue_id INTEGER, FOREIGN KEY(venue_id) REFERENCES venues(id)) ''')

# NOT USED
# c.execute('''CREATE TABLE journals (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, url text UNIQUE,
# year text, volume text UNIQUE, venue_id INTEGER, FOREIGN KEY(venue_id) REFERENCES venues(id)) ''')


class Database:

    def __init__(self):
        self.conn = sqlite3.connect('rankings.db')
        self.c = self.conn.cursor()

    def close_db(self):
        self.conn.close()

    def add_venue(self, name, url):
        try:
            self.c.execute("INSERT INTO venues(name,url) VALUES (?,?)", (name, url))
            self.conn.commit()
        except sqlite3.IntegrityError:
            print("Value " + url + " for: " + name + " already exists! Try again.")

    def get_venues(self):
        self.c.execute("SELECT url, id FROM venues")
        return self.c.fetchall()

    def add_conference_entry(self, name, url, year, venue_id):
        try:
            self.c.execute("INSERT INTO conferences(name,url, year, venue_id) VALUES (?,?,?,?)", (name, url, year,
                                                                                                  venue_id))
            self.conn.commit()
        except sqlite3.IntegrityError:
            print("Value " + url + " for: " + name + " already exists! Try again.")

    def get_conference_entry_urls(self, venue_id):
        self.c.execute("SELECT url FROM conferences WHERE venue_id=?", (venue_id,))
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


# conn = sqlite3.connect("rankings.db")
# c = conn.cursor()
# c.execute('''CREATE TABLE conferences (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, url text UNIQUE,
# year text, venue_id INTEGER, FOREIGN KEY(venue_id) REFERENCES venues(id)) ''')
# c.execute("DROP TABLE conferences")
# TABLE CREATION
# conn.commit()
# c.execute('''CREATE TABLE journals (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, url text UNIQUE,
# year text, venue_id INTEGER, FOREIGN KEY(venue_id) REFERENCES venues(id)) ''')

# c.execute("SELECT url FROM venues where type='Journal' ")
# print(c.fetchall())
