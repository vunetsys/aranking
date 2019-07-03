from queue import Queue, Empty
import threading
from time import sleep
from scopus_crawler import process_paper

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
