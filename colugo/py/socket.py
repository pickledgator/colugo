import functools
import logging
from tornado import ioloop
import zmq
from zmq.eventloop.future import Poller
from zmq.eventloop.zmqstream import ZMQStream


class Socket:
    """Wrapper class for zmq.Socket

    This class utilizes a tornado event loop to support using ZmqStream for sending 
    and receiving messages. Additionally it encorporates specific settings and infrastructure
    to allow request/reply sockets to be more robust to timeout conditions and failure states.
    
    Attributes:
        logger: Logger instance for all socket activity
        loop: Tornado event loop instance
        address: Assigned address of the zmq.Socket
        protocol: Assigned zmq socket type
        ctx: ZMQ context instance
        stream: ZmqStream instance
        zmq_socket: Underlying zmq.Socket object
    """

    def __init__(self, loop, protocol):
        """Constructor for Socket class
        
        Args:
            loop: Tornado event loop
            protocol: Assigned protocol for the zmq.Socket
        """
        self.logger = logging.getLogger("Socket")
        self.loop = loop
        self.protocol = protocol
        self.ctx = zmq.Context().instance()
        self.stream = None
        self.zmq_socket = None
        self.address = None
        self.create_socket(protocol)

    def create_socket(self, protocol):
        """Helper function for creating a zmq.Socket of various types with various options

        Assumes that request sockets need extra configuration options to prevent erroneous states
        when two requests are sent before a reply is received. REQ_RELAXED will drop the first
        request and reset the underlying socket automatically allowing the second request to be
        processed. Additionally, these options ensure that an event loop can exit even if a send is
        pending but hasn't been sent yet.

        Args:
            protocol: zmq socket type
            
        """
        if protocol == zmq.REQ:
            # make sure that replies back to req's are coordinated with header data
            self.ctx.setsockopt(zmq.REQ_CORRELATE, 1)
            # allow req socket to internall try to reconnect if two sends are sent in a row
            self.ctx.setsockopt(zmq.REQ_RELAXED, 1)
            # timeout for trying to send
            self.ctx.setsockopt(zmq.SNDTIMEO, 1000)
            # ensure that the socket doesn't block on close
            self.ctx.setsockopt(zmq.LINGER, 0)
        self.zmq_socket = self.ctx.socket(protocol)

    def connect(self, address):
        self.zmq_socket.connect(address)
        self.address = address
        self.start_stream()

    def bind(self, address):
        self.zmq_socket.bind(address)
        self.address = address
        self.start_stream()

    def send(self, message):
        self.logger.debug("Sending message: {}".format(message))
        if type(message) == str:
            # assumes string
            self.stream.send_string(message)
        else:
            # assumes bytes
            self.stream.send(message)

    def start_stream(self):
        if not self.stream:
            self.stream = ZMQStream(self.zmq_socket, self.loop)

    def stop_stream(self):
        if self.stream:
            if not self.stream.closed():
                # TODO(pickledgator): does this block if no recv?
                self.stream.stop_on_recv()
                self.stream.close()
            self.stream = None

    def cycle_socket(self):
        self.close()
        self.create_socket(self.protocol)
        self.connect(self.address)

    def receive(self, handler, timeout_ms=None, timeout_callback=None):
        def msg_handler(handler, timeout, message):
            # this callback receives a message list, with one element, so just pass the contents to the
            # application handler
            handler(message[0])
            # if we received the message, then we need to cancel the watchdog timeout from
            # the last receive call
            if timeout:
                self.loop.remove_timeout(timeout)

        def handle_timeout(timeout_callback):
            if timeout_callback:
                timeout_callback()
            # the event that we hit a timeout, cycle the socket so that it doesn't
            # get stuck in a weird state
            self.cycle_socket()

        if self.stream:
            if timeout_ms:
                # if we want to detect when recv fails, setup a timeout that cleans up the
                # socket (RequestClients)
                timeout = self.loop.call_later(timeout_ms / 1000.0, functools.partial(handle_timeout, timeout_callback))
                # always set the handler, in case it changed
                self.stream.on_recv(functools.partial(msg_handler, handler, timeout))
            else:
                # handle cases when we dont want to put a timeout on the recv function (subscribers)
                self.stream.on_recv(functools.partial(msg_handler, handler, None))
        else:
            self.logger.error("Stream is not open")

    def close(self):
        self.stop_stream()
        self.zmq_socket.close()
