from tornado import ioloop


class Repeater:
    """Periodic repeater that executes a callback function at a specified interval

    Basically a simple wrapper function for Tornado.ioloop.PeriodicCallback(). Does not
    account for compiling time drift.

    Attributes:
        rep: PeriodicCallback object
    """
    def __init__(self, loop, delay_ms, callback):
        """Constructor for the class
        Args:
            loop: Reference to the tornado event loop
            delay_ms: Number of milliseconds before callback execution
            callback: Callback to execute after delay_ms have elapsed
        """
        self.rep = ioloop.PeriodicCallback(callback, delay_ms)
        self.start()

    def start(self):
        """Enable the task on the event loop
        """
        self.rep.start()

    def stop(self):
        """Stop the task on the event loop
        """
        self.rep.stop()

    def __del__(self):
        """Deconstructor
        """
        self.stop()
