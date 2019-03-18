import sqlite3


class Database:

    def __init__(self):
        self.conn = sqlite3.connect('rankings.db')
        self.c = self.conn.cursor()

    def close_db(self):
        self.conn.close()

    # c.execute('''CREATE TABLE venues
    #               (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, url text, type text)''')

    # c.execute('''CREATE TABLE conferences (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, url text, year text,
    # venue_id INTEGER, FOREIGN KEY(venue_id) REFERENCES venues(id)) ''')

    def add_venue(self, name, url, venue_type):
        self.c.execute("INSERT INTO venues(name,url, type) VALUES (?,?,?)", (name, url, venue_type))
        self.conn.commit()

    def select(self):
        self.c.execute('''SELECT * FROM venues''')
        print(c.fetchall())

    def get_conferences(self):
        self.c.execute("SELECT url, id FROM venues WHERE type='Conference'")
        return self.c.fetchall()

    def get_journals(self):
        self.c.execute("SELECT url FROM venues WHERE type='Journal'")
        return self.c.fetchall()

    def add_conference_entry(self, name, url, year, conference_id):
        self.c.execute("INSERT INTO conferences(name,url, year, venue_id) VALUES (?,?,?,?)", (name, url, year,
                                                                                              conference_id))
        self.conn.commit()

    def get_yearly_conference(self):
        self.c.execute("SELECT name, venue_id FROM conferences")
        return self.c.fetchall()


conn = sqlite3.connect('rankings.db')
c = conn.cursor()

# c.execute('''SELECT url FROM venues WHERE type="Journal"''')
# url_test = c.fetchone()
# print(url_test[0])


