from dblp_crawler import *
from thread import *
from database import Database
from queue import Queue, Empty
import threading
from time import sleep
from concurrent.futures import ThreadPoolExecutor, as_completed

queue = Queue()
db = Database()
conferences = []
global_lock = threading.Lock()

file_contents = []
filename = "crawled_conferences.txt"
num_thread = 0

with open(filename, 'r') as f:
    visited = f.read()
    f.close()


def write_to_file(conf_id):
    while global_lock.locked():
        continue

    global_lock.acquire()
    with open(filename, "a") as f:
        f.write(str(conf_id) + "\n")
        f.close()
    global_lock.release()


def create_workers():
    workers = []
    for i in range(5):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()
        workers.append(t)
    for worker in workers:
        worker.join()


def work():
    global num_thread
    num_thread += 1
    try:
        while True:
            conference = queue.get_nowait()
            conf_id = conference[1]
            get_papers(conference, num_thread)
            write_to_file(conf_id)
            queue.task_done()
    except Empty:
        sleep(1)
        pass


def create_jobs(conf):
    for c in conf:
        if str(c[1]) not in visited:
            queue.put(c)


def main():
    # get_scholar_venues()
    # get_conferences()
    venues = db.get_venues()
    db.close_db()
    for v in venues:
        conf_id = v[1]
        global conferences
        conferences = get_yearly_conferences(conf_id)
        create_jobs(conferences)
        # for c in conferences:
        # if c[1] not in visited:
        # with ThreadPoolExecutor(max_workers=8) as pool:
        # pool.submit(get_papers(c))
    create_workers()


if __name__ == '__main__':
    main()
