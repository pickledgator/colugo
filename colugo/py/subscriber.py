import zmq
from colugo.py.zsocket import Socket


class Subscriber(Socket):
    """Socket that connects to one or many publisher sockets.

    A node may have multiple subscriber sockets, and each node may have one or more subscribers
    per topic.

    Address and port data for connection are resolved via a network discovery mechanism.

    Attributes:
        loop: Reference to the tornado event loop
        topic: The topic associated with the socket on the network
        callback: Handler executed when the socket receives messages from a publisher
    """

    def __init__(self, loop, topic, callback, on_connect=None):
        """Constructor for the subscriber class

        Args:
            topic: The topic associated with the socket on the network
            callback: Handler executed when the socket receives messages from a publisher
            on_connect: Callback handler when a connection is attempted (default: None)
        """
        super(Subscriber, self).__init__(loop, zmq.SUB)  # Socket.__init__()
        self.topic = topic
        self.callback = callback
        self.on_connect = on_connect
        self.set_filter() # Socket.set_filter()

    def connect(self, address, port):
        """Connect to a publisher socket at a specified address and port and setup listening
        task on event loop

        Args:
            address: Decimal separated string (eg, 127.0.0.1) where service is bound
            port: int associated with service port
        """
        self.logger.debug("SUB \"{}\" connecting to tcp://{}:{}".format(self.topic, address, port))
        super(Subscriber, self).connect(address, port)
        super(Subscriber, self).receive(self.callback)
        if self.on_connect: 
            self.on_connect()

    def close(self):
        """Just calls the colugo.py.Socket.close()
        """
        self.logger.debug("SUB \"{}\" disconnecting".format(self.topic))
        super(Subscriber, self).close()  # Client.close()
