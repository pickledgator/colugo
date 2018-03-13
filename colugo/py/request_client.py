import zmq
from colugo.py.socket import Socket


class RequestClient(Socket):

    def __init__(self, loop, address):
        super(RequestClient, self).__init__(loop, zmq.REQ)  # Socket.__init__()
        self.connect(address)  # Socket.connect()
        self.callback = None

    def request(self, message, callback, timeout=2000, timeout_handler=None):
        # TODO(pickledgator): what if server is dead?
        # TODO(pickledgator): timeout/retry?
        self.callback = callback
        self.receive(self.reply_callback, timeout, timeout_handler)  # Socket.receive()
        self.send(message)  # Socket.send()

    def reply_callback(self, message):
        if self.callback:
            self.callback(message)
        # clear the callback since the next request could be a different one
        self.callback = None

    def close(self):
        super(RequestClient, self).close()
