#!/usr/bin/env python

import os
import sys
# local path to library
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import logging
from colugo.py.node import Node
from tornado import ioloop
import uuid
import zmq
import unittest

logging.basicConfig(
    format="[%(asctime)s][%(name)s](%(levelname)s) %(message)s", level=logging.DEBUG)

class TestSocket(unittest.TestCase):
    def test_start_stop(self):
        node = Node("TestNode")
        self.assertIsNotNone(node.logger)
        node.loop.call_later(0.2, node.stop)
        node.start()
        self.assertTrue(True)

    def test_call_later(self):
        node = Node("TestNode2")
        def callback():
            self.assertTrue(True)
            node.stop()
        node.add_delayed_callback(100, callback)
        node.start()
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()