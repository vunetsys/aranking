from dblp_crawler import *
from database import Database, remove_duplicate_affiliations, check_paper_counts
from scholar_crawler import read_page
from thread import *
from scoring_algorithm import run_algorithm

scholar_link = "https://scholar.google.nl/citations?view_op=top_venues&hl=en&vq=eng"
number_of_cycles = 1

db = Database()


def main():
    # First gets all scholar venues, then all conferences, then all papers,
    # then tries to find affiliations for the papers.
    # In the end, checks all conferences for number of papers with affiliations and deletes ones with too little info.

    read_page(scholar_link, 2)
    get_scholar_venues()
    get_conferences()

    conferences = db.get_conferences()

    for conference in conferences:
        get_papers(conference)

    papers = db.get_papers()

    for paper in papers:
        create_jobs(paper, paper_queue)

    create_crawlers(get_affiliations())
    remove_duplicate_affiliations()
    check_paper_counts()

    run_algorithm(number_of_cycles)


if __name__ == '__main__':
    main()
