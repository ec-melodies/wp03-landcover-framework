__author__ = 'Jane'
# https://docs.python.org/2/library/queue.html
# https://docs.python.org/2/library/threading.html#threading.Thread

import Queue
import threading
import os

def worker():
    while True:
        item = q.get()
        # make temp dir based on year/tile/doy string to put o/p files in
        do_work(item)
        q.task_done()

def do_work(thing):
    print str(thing)


q = Queue.Queue()
for i in range(8):   # num_worker_threads
    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()

for my_file in os.listdir('C:\Users\Jane\workspace\Melodies_scripts\Operational python\GetData\src'):  # item in source():
    q.put(my_file)

q.join() # block until all tasks are done
























