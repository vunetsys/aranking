from dblp_crawler import *
from database import Database
from queue import Queue, Empty
import threading
from time import sleep
from scopus_crawler import process_paper


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

with open(filename, 'r') as f:
    visited = f.read()
    f.close()

with open(filename2, 'r') as f:
    no_result = f.read()
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


def create_jobs(job, queue):
    # print(job[0])
    queue.put(job)


def create_crawlers(target_method):
    workers = []
    for i in range(7):
        t = threading.Thread(target=target_method)
        t.daemon = True
        t.start()
        workers.append(t)
    for worker in workers:
        worker.join()


def get_affiliations():
    global num_thread_aff
    num_thread_aff += 1
    print("STARTED THREAD:", num_thread_aff)
    sleep(1.5)
    while True:
        try:
            paper = paper_queue.get()
            paper_id = paper[0]
            title = paper[1]
            # print(title)
            result = process_paper(title, paper_id)
            # print(result)
            if result:
                write_to_file(paper_id)
            paper_queue.task_done()
            sleep(2)
        except Empty:
            break


def main():
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
    # with open("docs/conferences_low_missing.txt", 'r') as file:
    #     low_missing_conf = file.read()
    #     file.close()
    #
    # with open(filename2) as no_papers:
    #     for paper_id in no_papers:
    #         db.c.execute("SELECT title, conference_id from papers where id=%s", (str(paper_id),))
    #         result = db.c.fetchone()
    #         conf_id = result[1]
    #         if str(conf_id) in low_missing_conf:
    #             title = result[0]
    #             print(title)
    #             with open('docs/paper_titles.txt', 'a') as file:
    #                 file.write(title + "\n")
    #     file.close()
    #     no_papers.close()

            # print(str(k) + ": " + str(v))

            # db.c.execute("SELECT title from papers where id=%s", (paper_id,))
            # result = db.c.fetchone()
            # print(result[0])


# if str(id) in visited or str(id) in no_result:
#             print("Already visited", id)
#             continue
#         else:
#


if __name__ == '__main__':
    main()
