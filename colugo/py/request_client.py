import zmq
from colugo.py.zsocket import Socket


class RequestClient(Socket):

    def __init__(self, loop, topic, on_connect):
        super(RequestClient, self).__init__(loop, zmq.REQ)  # Socket.__init__()
        self.callback = None
        self.topic = topic
        self.on_connect = on_connect

    def connect(self, address, port):
        self.logger.debug("REQ \"{}\" connecting to tcp://{}:{}".format(self.topic, address, port))
        super(RequestClient, self).connect(address, port) # Socket.connect()
        self.on_connect()

    def send(self, message, callback, timeout=2000, timeout_handler=None):
        # TODO(pickledgator): what if server is dead?
        # TODO(pickledgator): timeout/retry?
        self.callback = callback
        self.receive(self.reply_callback, timeout, timeout_handler)  # Socket.receive()
        super(RequestClient, self).send(message)  # Socket.send()

    def reply_callback(self, message):
        if self.callback:
            self.callback(message)
        # clear the callback since the next request could be a different one
        self.callback = None

    def close(self):
        super(RequestClient, self).close()
