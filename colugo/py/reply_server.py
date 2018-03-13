import zmq
from colugo.py.socket import Socket


class ReplyServer(Socket):

    def __init__(self, loop, address, callback):
        super(ReplyServer, self).__init__(loop, zmq.REP)  # Socket.__init__()
        self.callback = callback
        self.bind(address)  # Socket.bind()
        # start listening, and prep the send function to pass back to the application callback
        self.receive(self.request_handler)  # Socket.receive()

    def request_handler(self, message):
        # pass the request message and the socket's send function back out to the application
        # to process before replying
        self.callback(message, self.send)

    def close(self):
        super(ReplyServer, self).close()  # Socket.close()
