from dblp_crawler import *
from database import Database
from queue import Queue, Empty
import threading
from time import sleep
from scopus_crawler import process_paper
from scholar_crawler import read_page

scholar_link = "https://scholar.google.nl/citations?view_op=top_venues&hl=en&vq=eng"

db = Database()
conferences = []
global_lock = threading.Lock()

paper_queue = Queue()

file_contents = []
crawled_paper_filename = "docs/crawled_papers.txt"
no_result_filename = "docs/no_result_papers.txt"

num_thread_author = 0
num_thread_aff = 0

# # Reads in the ids of the already crawled papers
# with open(filename, 'r') as f:
#     visited = f.read()
#     f.close()
#
# # Reads in the paper numbers that did not return any result for the scopus api
# with open(filename2, 'r') as f:
#     no_result = f.read()
#     f.close()


def write_to_file(filename, conf_id):
    # Writes the conference_id to the visited conferences file.
    while global_lock.locked():
        continue

    global_lock.acquire()
    with open(filename, "a") as f:
        print("Writing:", conf_id)
        f.write(str(conf_id) + "\n")
        f.close()
    global_lock.release()


def create_jobs(job, queue):
    # For the crawlers, this method is used to put jobs in the queue
    queue.put(job)


def create_crawlers(target_method):
    #  Creates 7 threads, that will all keep on running the inputted job until all jobs from the queue are done.
    workers = []
    for i in range(7):
        t = threading.Thread(target=target_method)
        t.daemon = True
        t.start()
        workers.append(t)
    for worker in workers:
        worker.join()


def get_affiliations():
    # This method gets a paper from the queue, and tries to find the authors and affiliations for it through Scopus api.
    global num_thread_aff
    num_thread_aff += 1
    print("STARTED THREAD:", num_thread_aff)
    sleep(1.5)
    while True:
        try:
            paper = paper_queue.get()
            paper_id = paper[0]
            title = paper[1]
            result = process_paper(title, paper_id)

            if result:
                write_to_file(crawled_paper_filename, paper_id)
            else:
                write_to_file(no_result_filename, paper_id)
            paper_queue.task_done()
            sleep(2)
        except Empty:
            break


def check_paper_counts():
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
    check_paper_counts()


if __name__ == '__main__':
    main()
