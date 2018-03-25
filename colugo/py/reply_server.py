import zmq
from colugo.py.zsocket import Socket


class ReplyServer(Socket):
    """Socket that binds as a server, listens for a message from a request client, then replies with a
    different message

    A node may have multiple reply server sockets, but each node should only have one reply server
    socket per topic (ie, a node should not have a two reply servers with the same topic name). A reply
    server can service multiple request clients using the same topic. 

    NOTE: If multiple reply servers are utilizing the same topic, each request client message will 
    round robin to each of the reply servers.

    Address and port data are assigned to the specified topic at bind time within the 
    colugo.py.Socket class.

    When a request message is received by the socket, the message is passed to the callback (provided
    at construction time), along with a reference to the socket's send() function. The application may
    then decide when and what to send the reply message back to the request client. 

    Due to the nature of zmq.REQ sockets, the REP socket can only handle a single request per reply 
    (there is an internal state machine inside the the REQ socket type that prevents it from sending or 
    receiving twice in a row). However, the REQ socket options are configured such that if two request 
    messages are received by the REP in a row prior to a reply message being sent back, the original request 
    message will be dropped and only the second reply message will be handled.

    Attributes:
        topic: The topic associated with the socket on the network
        callback: Handler executed when the socket receives messages from a request client
    """

    def __init__(self, loop, topic, callback):
        """Constructor for reply server socket
        Args:
            loop: Reference to tornado event loop
            topic: The topic associated with the socket on the network
            callback: Handler executed when the socket receives messages from a request client
        """
        super(ReplyServer, self).__init__(loop, zmq.REP)  # Socket.__init__()
        self.callback = callback
        self.topic = topic

    def bind(self):
        """Calls the socket's bind function and stages the socket to listen
        """
        (addr, port) = super(ReplyServer, self).bind()  # Socket.bind()
        self.logger.debug("REP \"{}\" binding to tcp://{}:{}".format(self.topic, addr, port))
        # start listening, and prep the send function to pass back to the application callback
        self.receive(self.request_handler)  # Socket.receive()

    def request_handler(self, message):
        """Message received helper that provides the application callback with a reference to
        to the socket's send function for issueing the reply

        Args:
            message: Received message on the socket
        """
        # Pass the request message and the socket's send function back out to the application
        # to process before replying
        self.callback(message, self.send)

    def close(self):
        """Just calls the colugo.py.Socket.close()
        """
        # Socket.unbind() is handled within the close call
        super(ReplyServer, self).close()  # Socket.close()
