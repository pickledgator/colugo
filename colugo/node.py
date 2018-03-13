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

from colugo.publisher import Publisher
from colugo.subscriber import Subscriber
from colugo.request_client import RequestClient
from colugo.reply_server import ReplyServer
from colugo.repeater import Repeater

logging.basicConfig(
    format="[%(asctime)s][%(name)s](%(levelname)s) %(message)s", level=logging.DEBUG)


class Node:

    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger(self.name)
        self.logger.info("Node {} is initializing".format(self.name))
        self.loop = ioloop.IOLoop.current()
        self.sockets = []
        # exit conditions
        signal.signal(signal.SIGINT, lambda sig, frame: self.loop.add_callback_from_signal(self.stop))

    def start(self):
        """ Start the ioloop
        """
        self.logger.info("Node {} is starting".format(self.name))
        self.loop.start()  # blocking

    def stop(self):
        """ Stop the ioloop
        """
        self.logger.info("Node {} is stopping".format(self.name))
        for s in self.sockets:
            s.close()
        self.loop.stop()

    def add_repeater(self, delay_ms, callback):
        """ Helper function that adds a repeater to the node using the node's event loop
            Use functools.partial(callback, arg1, arg2, etc.) to pass arguemnts to callback
        """
        self.logger.info("Adding repeater to node {} with rate {}ms".format(self.name, delay_ms))
        rep = Repeater(self.loop, delay_ms, callback)
        return rep

    def add_delayed_callback(self, delay_ms, callback):
        self.loop.call_later(delay_ms / 1000.0, callback)

    def add_publisher(self, address):
        sock = Publisher(self.loop, address)
        self.sockets.append(sock)
        return sock

    def add_subscriber(self, address, callback):
        sock = Subscriber(self.loop, address, callback)
        self.sockets.append(sock)
        return sock

    def add_request_client(self, address):
        sock = RequestClient(self.loop, address)
        self.sockets.append(sock)
        return sock

    def add_reply_server(self, address, callback):
        sock = ReplyServer(self.loop, address, callback)
        self.sockets.append(sock)
        return sock
