import zmq
from colugo.py.zsocket import Socket


class RequestClient(Socket):
    """Socket that connects to a reply server and listens for replies after sending request messages.

    A node may have multiple request client sockets, and each node may have multiple request client
    sockets per topic.

    NOTE: If multiple reply servers are utilizing the same topic, each request client message will 
    round robin to each of the reply servers.

    Address and port data are assigned to the specified topic at bind time within the 
    colugo.py.Socket class.

    After socket construction, the send() method can be used to pass a request to a reply server. Then,
    the request client socket will wait for a reply. Until a reply is received, it is recommended that 
    additional requests are not sent. As an optional (but recommended) parameter, requests can have an
    associated "wait for reply" timeout. If a timeout occurs before a reply is received, the request socket
    is reset (closed and re-connected) to ensure that should the reply server become available again, 
    subsequent requests can still be serviced. This works even if the address/port of the reply server
    change on the network since the new connection will be initiated by the discovery layer.

    Due to the nature of zmq.REQ sockets, the REP socket can only handle a single request per reply 
    (there is an internal state machine inside the the REQ socket type that prevents it from sending or 
    receiving twice in a row). However, the REQ socket options are configured such that if two request 
    messages are received by the REP in a row prior to a reply message being sent back, the original request 
    message will be dropped and only the second reply message will be handled.

    Attributes:
        topic: The topic associated with the socket on the network
        callback: Handler executed when the socket receives messages (passed at send() time)
        on_connect: Callback handler when a connection is attempted
    """

    def __init__(self, loop, topic, on_connect):
        """Constructor for request client

        Args:
            loop: Reference to the tornado event loop
            topic: The topic associated with the socket on the network
            on_connect: Callback handler when a connection is attempted
        """
        super(RequestClient, self).__init__(loop, zmq.REQ)  # Socket.__init__()
        self.callback = None
        self.topic = topic
        self.on_connect = on_connect

    def connect(self, address, port):
        """Connect to socket at a specified address and port

        Args:
            address: Decimal separated string (eg, 127.0.0.1) where service is bound
            port: int associated with service port
        """
        self.logger.debug("REQ \"{}\" connecting to tcp://{}:{}".format(self.topic, address, port))
        super(RequestClient, self).connect(address, port) # Socket.connect()
        self.on_connect()

    def send(self, message, callback, timeout=2000, timeout_handler=None):
        """Helper function for sending a request message with a reply timeout

        Receive timeouts are reset each time send() is called

        Args:
            message: The message to be sent
            callback: The application callback handler when a reply is received
            timeout: Number of milliseconds to wait for a reply before calling timeout handler
            timeout_handler: The application callback handler when a timeout occurs
        """
        self.callback = callback
        self.receive(self.reply_callback, timeout, timeout_handler)  # Socket.receive()
        super(RequestClient, self).send(message)  # Socket.send()

    def reply_callback(self, message):
        """Ensures that the reply callback function is valid before passing to the application
        
        Args:
            message: The message the was received
        """
        if self.callback:
            self.callback(message)
        # clear the callback since the next request could be a different one
        self.callback = None

    def close(self):
        """Calls colugo.py.Socket.close()
        """
        super(RequestClient, self).close()
