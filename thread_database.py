import psycopg2
from psycopg2.pool import ThreadedConnectionPool

link_base_dblp = "https://dblp.org/search/venue/api?q="

DSN = "host='localhost' dbname='academicrankings' user='lucasfaijdherbe'"
tcp = ThreadedConnectionPool(1, 18, DSN)

# Threaded version of the db class


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

    def add_affiliation(self, aff_id, affiliation, country):
        try:
            print(affiliation)
            self.c.execute('''INSERT INTO affiliations(id, affiliation, country) VALUES (%s, %s, %s)''',
                           (aff_id, affiliation, country))
            self.conn.commit()
        except psycopg2.IntegrityError:
            self.conn.rollback()
            print("AFFILIATION ALREADY EXISTS")

    def add_author(self, user_id, first_name, last_name, url, aff_id):
        try:
            self.c.execute('''INSERT INTO authors(user_id, first_name, last_name, url, affiliation_id)
                           VALUES (%s,%s,%s,%s,%s)''', (user_id, first_name, last_name, url, aff_id))
            self.conn.commit()
            print("Added author: " + first_name + " " + last_name)
        except psycopg2.IntegrityError:
            self.conn.rollback()

    def add_author_paper(self, author_id, paper_id):
        try:
            self.c.execute("INSERT INTO authors_papers(author_id, paper_id) VALUES (%s,%s)", (author_id, paper_id))
            self.conn.commit()
        except psycopg2.IntegrityError:
            self.conn.rollback()
            print("Record already exists! Try again.")
