#! /usr/bin/env python3

from threading import Thread, Condition, Event
from queue import Queue
import time
import calendar
import sys

class AddJobThread(Thread):
    def __init__(self, condition, job_queue, job_id, start_t, interval_t):
        self.job_id = job_id
        self.start_t = start_t
        self.interval_t = interval_t
        self.job_queue = job_queue
        self.condition = condition
        self.stop_event = Event()
        self.instance_id = 0
        super(AddJobThread, self).__init__()

    def run(self):
        current_time = calendar.timegm(time.gmtime())
        time.sleep(self.start_t - current_time)
        while not self.stop_event.is_set():
            # producer with job_id gets lock
            self.condition.acquire()
            self.instance_id += 1
            self.job_queue.put((self.job_id, self.instance_id))
            # producer notifies the consumer every time new job instance is put into the shared queue
            self.condition.notify()
            self.condition.release()
            time.sleep(self.interval_t)

    def stop(self):
        self.stop_event.set()


class LaunchJobThread(Thread):
    def __init__(self, condition, job_queue):
        self.condition = condition
        self.job_queue = job_queue
        super(LaunchJobThread, self).__init__()

    def run(self):
        # consumer gains lock
        while True:
            self.condition.acquire()
            if self.job_queue.empty():
                # consumer waits for notification from producers
                self.condition.wait()
            current_time = calendar.timegm(time.gmtime())
            launched_job_id, instance_id = self.job_queue.get()
            print("start instance %d of job %d in background at unix timestamp %d" % (instance_id, launched_job_id, current_time))
            # consumer releases lock
            self.condition.release()


class RepeatingJobQueue(object):
    def __init__(self):
        self.job_queue = Queue()
        self.condition = Condition()
        self.thread_dict = dict()
        # start the consumer thread
        self.launchJobThread = LaunchJobThread(self.condition, self.job_queue)
        self.launchJobThread.start()

    def addJob(self, job_id, start_t, interval_t):
        # add new producer with job id
        new_thread = AddJobThread(self.condition, self.job_queue, job_id, start_t, interval_t)
        self.thread_dict[job_id] = new_thread
        new_thread.start()

    def removeJob(self, job_id):
        if job_id in self.thread_dict:
            # stop producer with job_id
            self.thread_dict[job_id].stop()
            self.thread_dict.pop(job_id)
        else:
            # producer with job_id does not exist
            raise Exception("Job %d has not been added to scheduler!" % job_id)


if __name__ == '__main__':
    queue = RepeatingJobQueue()
    job_num, insert_interval, launch_delay, launch_interval, full_run_time = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])

    for job_id in range(job_num):
        time.sleep(insert_interval)
        future_time = calendar.timegm(time.gmtime()) + launch_delay
        queue.addJob(job_id, future_time, launch_interval)

    time.sleep(full_run_time)

    for job_id in range(job_num):
        queue.removeJob(job_id)
        time.sleep(insert_interval)
