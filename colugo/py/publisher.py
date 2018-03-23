import zmq
from colugo.py.zsocket import Socket


class Publisher(Socket):

    def __init__(self, loop, topic):
        super(Publisher, self).__init__(loop, zmq.PUB)  # Socket.__init__()
        self.topic = topic

    def bind(self):
        (addr, port) = super(Publisher, self).bind()  # Socket.bind()
        self.logger.debug("PUB \"{}\" binding to tcp://{}:{}".format(self.topic, addr, port))

    def close(self):
        # Socket.unbind() is handled within the close call
        super(Publisher, self).close()  # Socket.close()
