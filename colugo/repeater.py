from tornado import ioloop


class Repeater:

    def __init__(self, loop, delay_ms, callback):
        self.rep = ioloop.PeriodicCallback(callback, delay_ms)
        self.start()

    def start(self):
        self.rep.start()

    def stop(self):
        self.rep.stop()

    def __del__(self):
        self.stop()
