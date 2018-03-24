import zmq
from colugo.py.zsocket import Socket


class Publisher(Socket):
    """Socket that binds as a server and publishes to one or many subscriber sockets.

    A node may have multiple publisher sockets, but each node should only have one publisher
    per topic (ie, a node should not have a two publishers with the same topic name).

    Address and port data are assigned to the specified topic at bind time within the 
    colugo.py.Socket class.

    To send a message using the publisher socket after it has been constructed, use the 
    send() method (inherited from colugo.py.Socket)

    Attributes:
        loop: Reference to the tornado event loop
        topic: The topic associated with the socket on the network
    """

    def __init__(self, loop, topic):
        """Constructor for the publisher class

        Args:
            loop: Reference to the tornado event loop
            topic: The topic associated with the socket on the network
        """
        super(Publisher, self).__init__(loop, zmq.PUB)  # Socket.__init__()
        self.topic = topic

    def bind(self):
        """Just calls the colugo.py.Socket.bind() but has a helpful print
        """
        (addr, port) = super(Publisher, self).bind()  # Socket.bind()
        self.logger.debug("PUB \"{}\" binding to tcp://{}:{}".format(self.topic, addr, port))

    def close(self):
        """Just calls the colugo.py.Socket.close()
        """
        # TODO(pickledgator): We can problably remove this and just use the base class method
        # Socket.unbind() is handled within the close call
        super(Publisher, self).close()  # Socket.close()
