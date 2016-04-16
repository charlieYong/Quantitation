#!/usr/bin/env python
# coding: utf-8

'''
python多进程测试
'''

import multiprocessing as mp
import time
import sys

def PrintNow ():
    return time.strftime ("%Y%m%d %H:%M:%S", time.localtime (time.time ()))

def PrintLog (s):
    print PrintNow (), s
    sys.stdout.flush ()

class Task(object):

    def __call__(self):
        # pretend to take some time to do the work
        time.sleep (1)

class Worker(mp.Process):
    def __init__(self, task_queue, v):
        mp.Process.__init__(self)
        self._task_queue = task_queue
        self._v = v

    def run(self):
        pname = self.name        
        while True:
            task = self._task_queue.get ()
            if task is None:
                break
            PrintLog ("%s get task" % pname)
            task ()
            with self._v.get_lock():
                self._v.value += 1
            PrintLog ("%s complete task" % pname)
        PrintLog ("%s Exit" % pname)

if __name__ == "__main__":
    complete = mp.Value ('i', 0)
    count = mp.cpu_count () * 2
    tasks = mp.Queue ()
    workers = [Worker(tasks, complete) for i in xrange (count)]

    for worker in workers:
        worker.start ()
    PrintLog ("start %d workers" % len(workers))

    total = 48 
    for i in xrange (total):
        tasks.put (Task ())

    for i in xrange (count):
        tasks.put (None)

    # print working process
    while True:
        PrintLog ("%s total=%d, complete=%d" % ('-'*10, total, complete.value))
        if total <= complete.value:
            break
        time.sleep (0.5)
    PrintLog ("All Task Completed")


