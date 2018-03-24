import zmq
from colugo.py.zsocket import Socket


class ReplyServer(Socket):

    def __init__(self, loop, topic, callback):
        super(ReplyServer, self).__init__(loop, zmq.REP)  # Socket.__init__()
        self.callback = callback
        self.topic = topic

    def bind(self):
        (addr, port) = super(ReplyServer, self).bind()  # Socket.bind()
        self.logger.debug("REP \"{}\" binding to tcp://{}:{}".format(self.topic, addr, port))
        # start listening, and prep the send function to pass back to the application callback
        self.receive(self.request_handler)  # Socket.receive()

    def request_handler(self, message):
        # pass the request message and the socket's send function back out to the application
        # to process before replying
        self.callback(message, self.send)

    def close(self):
        # Socket.unbind() is handled within the close call
        super(ReplyServer, self).close()  # Socket.close()
