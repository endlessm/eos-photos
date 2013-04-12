from threading import Thread
import Queue
import traceback

class AsyncWorker(Thread):
    """
    Tiny class to queue up tasks to run on a worker thread.
    """
    def __init__(self):
        Thread.__init__(self)
        self.queue = Queue.Queue(0)

    def add_task(self, task, args=()):
        self.queue.put((task, args))

    def run(self):
        while not self.queue.empty():
            try:
                method, args = self.queue.get()
                method(*args)
            except Exception:
                print "In worker thread...."
                print traceback.format_exc()
