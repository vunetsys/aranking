from dblp_crawler import *
from database import Database
from queue import Queue, Empty
import threading
from time import sleep
from scopus_crawler import process_paper
from initial_rankings import give_initial_ranking, add_initial_universities

db = Database()
conferences = []
global_lock = threading.Lock()

paper_queue = Queue()

file_contents = []
# filename = "crawled_conferences.txt"
filename = "docs/crawled_papers.txt"
filename2 = "docs/no_result_papers.txt"

num_thread_author = 0
num_thread_aff = 0

# Reads in the ids of the already crawled papers
with open(filename, 'r') as f:
    visited = f.read()
    f.close()

# Reads in the paper numbers that did not return any result for the scopus api
with open(filename2, 'r') as f:
    no_result = f.read()
    f.close()


def write_to_file(conf_id):
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
                write_to_file(paper_id)
            paper_queue.task_done()
            sleep(2)
        except Empty:
            break


def main():
    # First gets all scholar venues, then all conferences, then all papers,
    # then tries to find affiliations for the papers

    # get_scholar_venues()
    # get_conferences()
    # get_papers()
    # papers = db.get_papers()
    # db.close_db()

    with open(filename2) as f2:
        for paper_id in f2:
            if int(paper_id) > 85870:
                db.c.execute("SELECT title FROM papers where id=%s", (paper_id,))
                title = db.c.fetchone()
                paper = [int(paper_id), title[0]]
                # print(paper)
                create_jobs(paper, paper_queue)

    #     if str(id) in no_result:
    #         create_jobs(paper, paper_queue)
    create_crawlers(get_affiliations)
    add_initial_universities()
    give_initial_ranking()


if __name__ == '__main__':
    main()
