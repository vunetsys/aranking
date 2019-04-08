from dblp_crawler import *
from database import Database
from queue import Queue, Empty
import threading
from time import sleep

db = Database()
conferences = []
global_lock = threading.Lock()

author_queue = Queue()
affiliation_queue = Queue()


file_contents = []
filename = "crawled_conferences.txt"
num_thread_author = 0
num_thread_aff = 0

with open(filename, 'r') as f:
    visited = f.read()
    f.close()


def write_to_file(conf_id):
    while global_lock.locked():
        continue

    global_lock.acquire()
    with open(filename, "a") as f:
        print("Writing:", conf_id)
        f.write(str(conf_id) + "\n")
        f.close()
    global_lock.release()


def create_jobs(jobs, queue):
    for j in jobs:
            queue.put(j)


def create_crawlers(target_method):
    workers = []
    for i in range(4):
        t = threading.Thread(target=target_method)
        t.daemon = True
        t.start()
        workers.append(t)
    for worker in workers:
        worker.join()


def get_author_info():
    global num_thread_author
    num_thread_author += 1
    sleep(5)
    while True:
        try:
            conference = author_queue.get_nowait()
            conf_id = conference[1]

            if str(conf_id) not in visited:
                print(num_thread_author)
                author_id = get_papers(conference, num_thread_author)

                for author in author_id:
                    affiliation_queue.put(author)

                write_to_file(conf_id)
            else:
                print("CONF: " + str(conf_id) + " Already visited")
            author_queue.task_done()
            num_thread_author += 1
        except Empty:
            break


def get_affiliations():
    global num_thread_aff
    num_thread_aff += 1
    print("STARTED THREAD:", num_thread_aff)
    sleep(5)
    while True:
        try:
            author = affiliation_queue.get_nowait()
            author_id = author[0]

            if str(author_id) == "9999999":
                get_author(author_id, num_thread_aff)

            affiliation_queue.task_done()
        except Empty:
            break


def main():
    # get_scholar_venues()
    # get_conferences()
    venues = db.get_venues()
    for v in venues:
        conf_id = v[1]
        global conferences
        conferences = get_yearly_conferences(conf_id)
        create_jobs(conferences, author_queue)
    create_crawlers(get_author_info)
    db.c.execute("SELECT id FROM AUTHORS WHERE (affiliation_id = 9999999) ORDER BY id ASC")
    authors = db.c.fetchall()
    if len(authors) > 0:
        create_jobs(authors, affiliation_queue)
        create_crawlers(get_affiliations)


if __name__ == '__main__':
    main()
