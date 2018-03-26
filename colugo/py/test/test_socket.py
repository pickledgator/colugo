#!/usr/bin/env python

import os
import sys
# local path to library
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from colugo.py.zsocket import Socket
from tornado import ioloop
import zmq
import unittest


class TestSocket(unittest.TestCase):
    loop = ioloop.IOLoop.current()
    socket = Socket(loop, zmq.PUB)

    def test_constructor(self):
        self.assertIsNone(self.socket.stream)
        self.assertIsNotNone(self.socket.zmq_socket)
        self.assertEqual(self.socket.protocol, zmq.PUB)
        self.assertEqual(self.socket.zmq_socket.getsockopt(zmq.SNDTIMEO), -1)
        self.assertEqual(self.socket.zmq_socket.getsockopt(zmq.LINGER), -1)

    def test_create_socket(self):
        req_socket = Socket(self.loop, zmq.REQ)
        self.assertEqual(req_socket.protocol, zmq.REQ)
        self.assertEqual(req_socket.ctx.getsockopt(zmq.REQ_CORRELATE), 1)
        self.assertEqual(req_socket.ctx.getsockopt(zmq.REQ_RELAXED), 1)
        self.assertEqual(req_socket.ctx.getsockopt(zmq.SNDTIMEO), 1000)
        self.assertEqual(req_socket.ctx.getsockopt(zmq.LINGER), 0)

if __name__ == '__main__':
    unittest.main()