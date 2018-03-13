import zmq
from colugo.socket import Socket


class Subscriber(Socket):

    def __init__(self, loop, address, callback):
        super(Subscriber, self).__init__(loop, zmq.SUB)  # Socket.__init__()
        self.callback = callback
        self.set_filter()
        # TODO(pickledgator): this would ultimately only get called when a server is
        # identified on the network
        self.connect(address)  # Socket.connect()
        self.receive(self.callback)  # Socket.receive()

    def set_filter(self, filter_string=""):
        # "" is a wildcard to accept all messages
        self.zmq_socket.setsockopt_string(zmq.SUBSCRIBE, filter_string)

    def close(self):
        super(Subscriber, self).close()  # Client.close()
