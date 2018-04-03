from threading import Thread
import queue
import traceback

class AsyncWorker(Thread):
    """
    Tiny class to queue up tasks to run on a worker thread.
    """
    def __init__(self, name=""):
        Thread.__init__(self)
        self.queue = queue.Queue(0)
        self.name = name
        self.finished = False

    def add_task(self, task, args=()):
        self.queue.put((task, args))

    def run(self):
        while not self.queue.empty():
            try:
                method, args = self.queue.get()
                method(*args)
            except Exception:
                print("In worker thread....")
                print(traceback.format_exc())
        self.finished = True
