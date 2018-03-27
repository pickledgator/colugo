#!/usr/bin/env python

import os
import sys
# local path to library
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import logging
from colugo.py.zsocket import Socket
from tornado import ioloop
import zmq
import unittest

logging.basicConfig(
    format="[%(asctime)s][%(name)s](%(levelname)s) %(message)s", level=logging.DEBUG)

class TestSocket(unittest.TestCase):
    def test_constructor(self):
        loop = ioloop.IOLoop.current()
        socket = Socket(loop, zmq.PUB)
        self.assertIsNone(socket.stream)
        self.assertIsNotNone(socket.zmq_socket)
        self.assertEqual(socket.protocol, zmq.PUB)
        self.assertEqual(socket.zmq_socket.getsockopt(zmq.SNDTIMEO), -1)
        self.assertEqual(socket.zmq_socket.getsockopt(zmq.LINGER), -1)

    def test_create_socket(self):
        loop = ioloop.IOLoop.current()
        req_socket = Socket(loop, zmq.REQ)
        self.assertEqual(req_socket.protocol, zmq.REQ)
        self.assertEqual(req_socket.ctx.getsockopt(zmq.REQ_CORRELATE), 1)
        self.assertEqual(req_socket.ctx.getsockopt(zmq.REQ_RELAXED), 1)
        self.assertEqual(req_socket.ctx.getsockopt(zmq.SNDTIMEO), 1000)
        self.assertEqual(req_socket.ctx.getsockopt(zmq.LINGER), 0)

    def test_connect_disconnect(self):
        loop = ioloop.IOLoop.current()
        socket_sub = Socket(loop, zmq.SUB)
        (addr, p) = socket_sub.connect("127.0.0.1", 30004)
        self.assertEqual("127.0.0.1", addr)
        self.assertEqual(30004, p)
        self.assertIsNotNone(socket_sub.stream)
        socket_sub.disconnect()
        self.assertIsNone(socket_sub.stream)

    def test_get_local_ip(self):
        loop = ioloop.IOLoop.current()
        socket = Socket(loop, zmq.PUB)
        ip = socket.get_local_ip()
        self.assertIsNotNone(ip)

    def test_bind(self):
        loop = ioloop.IOLoop.current()
        socket = Socket(loop, zmq.PUB)
        def unbind():
            socket.unbind()
            self.assertIsNone(socket.stream)
            loop.stop()
        (addr, p) = socket.bind()
        ip = socket.get_local_ip()
        self.assertEqual(ip, addr)
        self.assertNotEqual(p, 0)
        self.assertFalse(socket.zmq_socket.closed)
        loop.add_callback(unbind)
        loop.start()

    def test_send_rec(self):
        loop = ioloop.IOLoop.current()
        socket = Socket(loop, zmq.PUB)
        socket_sub = Socket(loop, zmq.SUB)
        def handler(msg):
            self.assertEqual(msg, "test")
            loop.stop()
        def send():
            socket.send("test")
        (addr, p) = socket.bind()
        socket_sub.connect(addr, p)
        socket_sub.set_filter()
        socket_sub.receive(handler)
        # make sure this happens last on the ioloop
        loop.call_later(0.1, send)
        loop.start()

    def test_recv_timeout(self):
        loop = ioloop.IOLoop.current()
        def timeout_handler():
            loop.stop()
            self.assertTrue(True)
        def reply(msg, send_helper):
            self.assertTrue(False)
        def send():
            socket_req.receive(reply, 0.1, timeout_handler)
            socket_req.send("test req")
        socket_rep = Socket(loop, zmq.REP)
        (addr, p) = socket_rep.bind()
        socket_req = Socket(loop, zmq.REQ)
        socket_req.connect(addr, p)
        loop.call_later(0.1, send)
        loop.start()


if __name__ == '__main__':
    unittest.main()