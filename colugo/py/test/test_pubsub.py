#!/usr/bin/env python

import os
import sys
# local path to library
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import logging
from colugo.py.publisher import Publisher
from colugo.py.subscriber import Subscriber
from tornado import ioloop
import zmq
import unittest

logging.basicConfig(
    format="[%(asctime)s][%(name)s](%(levelname)s) %(message)s", level=logging.DEBUG)

class TestSocket(unittest.TestCase):
    def test_message(self):
        loop = ioloop.IOLoop.current()
        message = "asdf"
        def callback(msg):
            self.assertEqual(msg, message)
            loop.stop()
        def on_connect():
            self.assertTrue(True)
        def send():
            pub.send(message)
        pub = Publisher(loop, "topic")
        pub.bind()
        sub = Subscriber(loop, "topic", callback, on_connect)
        sub.connect(pub.address, pub.port)
        loop.call_later(0.1, send)
        loop.start()

if __name__ == '__main__':
    unittest.main()