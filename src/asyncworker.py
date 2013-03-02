from threading import Thread
import Queue


class AsyncWorker(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.queue = Queue.Queue(0)

    def add_task(self, task, args):
        self.queue.put((task, args))

    def run(self):
        while not self.queue.empty():
            try:
                method, args = self.queue.get()
                method(*args)
            except Exception, exception:
                print "Exception raised in async worker of type ", type(exception)
                print exception
