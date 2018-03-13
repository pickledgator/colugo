import zmq
from colugo.socket import Socket


class Publisher(Socket):

    def __init__(self, loop, address):
        super(Publisher, self).__init__(loop, zmq.PUB)  # Socket.__init__()
        self.bind(address)  # Socket.bind()

    def close(self):
        super(Publisher, self).close()  # Socket.close()
