import zmq
from colugo.py.zsocket import Socket


class Subscriber(Socket):

    def __init__(self, loop, topic, callback):
        super(Subscriber, self).__init__(loop, zmq.SUB)  # Socket.__init__()
        self.topic = topic
        self.callback = callback
        self.set_filter()

    def connect(self, address, port):
        self.logger.debug("SUB \"{}\" connecting to tcp://{}:{}".format(self.topic, address, port))
        super(Subscriber, self).connect(address, port)
        super(Subscriber, self).receive(self.callback)

    def set_filter(self, filter_string=""):
        # "" is a wildcard to accept all messages
        self.zmq_socket.setsockopt_string(zmq.SUBSCRIBE, filter_string)

    def close(self):
        self.logger.debug("Topic \"{}\" disconnecting".format(self.topic))
        super(Subscriber, self).close()  # Client.close()
