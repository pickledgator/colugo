#!/usr/bin/env python

import functools
import logging
import os
import sys
import signal
import threading
import time
from tornado import ioloop
import zmq
from zmq.eventloop.zmqstream import ZMQStream

from colugo.py.discovery import Discovery
from colugo.py.publisher import Publisher
from colugo.py.subscriber import Subscriber
from colugo.py.request_client import RequestClient
from colugo.py.reply_server import ReplyServer
from colugo.py.repeater import Repeater

logging.basicConfig(
    format="[%(asctime)s][%(name)s](%(levelname)s) %(message)s", level=logging.DEBUG)


class Node:
    """Outer container for ioloop and zmq sockets
    
    Attributes:
        name: The name of the node, used to identify the logger
        logger: Logger instance, specific to activities within the node
        loop: Tornado event loop, socket send/receive, timers operate on this
        sockets: List of socket objects that have been created within the node
    """
    def __init__(self, name):
        """Constructor for the node class

        Args:
            name: Name of the node
        """
        self.name = name
        self.logger = logging.getLogger(self.name)
        self.logger.info("Node {} is initializing".format(self.name))
        self.loop = ioloop.IOLoop.current()
        self.sockets = []
        self.discovery = Discovery(name)
        # exit conditions
        signal.signal(signal.SIGINT, lambda sig, frame: self.loop.add_callback_from_signal(self.stop))

    def start(self):
        """Start the event loop
        """
        self.logger.info("Node {} is starting".format(self.name))
        self.loop.start()  # blocking

    def stop(self):
        """ Stop the event loop and close all open sockets
        """
        self.logger.info("Node {} is stopping".format(self.name))
        for s in self.sockets:
            s.close()
        self.loop.stop()

    def add_repeater(self, delay_ms, callback):
        """Helper function to add a repeater to the node using the node's event loop
            Use functools.partial(callback, arg1, arg2, etc.) to pass arguemnts to callback

        Args:
            delay_ms: Number of milliseconds between callback executions
            callback: Function to execute on repeat

        Returns:
            colugo.py.repeater object that the application layer can manipulate
        """
        self.logger.info("Adding repeater to node {} with rate {}ms".format(self.name, delay_ms))
        rep = Repeater(self.loop, delay_ms, callback)
        return rep

    def add_delayed_callback(self, delay_ms, callback):
        """Helper function to execute a callback function at a time in the future
        
        Args:
            delay_ms: Number of milliseconds in the future when you want the callback to fire
            callback: Function to execute
        """
        self.loop.call_later(delay_ms / 1000.0, callback)

    def add_publisher(self, topic):
        """Helper function to add a colugo.py.Publisher object to the node
        
        Args:
            address: ZMQ address to bind to

        Returns:
            colugo.py.Publisher object, call send() to send a message
        """
        # TODO(pickledgator): Get iface address here
        sock = Publisher(self.loop, "127.0.0.1")
        self.sockets.append(sock)
        self.discovery.register_topic("pub_topic", "PUB", sock.address, sock.port)
        return sock

    def add_subscriber(self, address, callback):
        """Helper function to add a colugo.py.Subscriber object to the node
        
        Args:
            address: ZMQ address to connect to
            callback: Function handler when messages are received

        Returns:
            colugo.py.Subscriber object
        """
        sock = Subscriber(self.loop, address, callback)
        self.sockets.append(sock)
        self.discovery.register_topic("sub_topic", "SUB", sock.address, socket.port)
        return sock

    def add_request_client(self, address):
        """Helper function to add a colugo.py.RequestClient object to the node
        
        Args:
            address: ZMQ address to connect to

        Returns:
            colugo.py.RequestClient object, call send(msg, callback) to send a message
        """
        sock = RequestClient(self.loop, address)
        self.sockets.append(sock)
        return sock

    def add_reply_server(self, address, callback):
        """Helper function to add a colugo.py.ReplyServer object to the node
        
        Args:
            address: ZMQ address to bind to
            callback: Function handler when a request message is received

        Returns:
            colugo.py.ReplyServer object
        """
        sock = ReplyServer(self.loop, address, callback)
        self.sockets.append(sock)
        return sock
