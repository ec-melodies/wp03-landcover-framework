__author__ = 'Jane'
# http://stackoverflow.com/questions/2046603/is-it-possible-to-run-function-in-a-subprocess-without-threading-or-writing-a-se
# code based on https://docs.python.org/2/library/multiprocessing.html  16.6.1.1

from multiprocessing import Process, Queue
import os

def info(title):
    print '2 - ' + title
    print 'module name:', __name__
    if hasattr(os, 'getppid'):  # only available on Unix - parent process id
        print 'parent process:', os.getppid()
    print 'process id:', os.getpid()

def do_work(q):
    info('function do_work()')
    print '3 - hello'
    while True:
        thelist = q.get()
        item = thelist[0]
        count = thelist[1]
        print 'xxx ' + str(item) + '  ' + str(count)
        # q.task_done()

if __name__ == '__main__':
    num_proc = 5
    q = Queue()
    info('1 - main line')
    counter = 0
    for my_file in os.listdir('C:\Users\Jane\workspace\Melodies_scripts\Operational python\GetData\src'):  # item in source():
        thelist = (my_file, counter)
        q.put(thelist)
        counter += 1
    for i in range (num_proc):
        p = Process(target=do_work, args=(q,))  # , args=('bob',))
        p.start()
    p.join()