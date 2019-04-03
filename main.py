from dblp_crawler import *
from database import Database

# queue = Queue()
db = Database()


def main():
    # get_scholar_venues()
    # get_conferences()
    venues = db.get_venues()
    db.close_db()
    for v in venues:
        id = v[1]
        conferences = get_yearly_conferences(id)
        get_papers(conferences)


if __name__ == '__main__':
    main()
