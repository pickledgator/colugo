#!/usr/bin/env python

import os
import sys
# local path to library
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import logging
from colugo.py.reply_server import ReplyServer
from colugo.py.request_client import RequestClient
from tornado import ioloop
import zmq
import time
import unittest

logging.basicConfig(
    format="[%(asctime)s][%(name)s](%(levelname)s) %(message)s", level=logging.DEBUG)

class TestSocket(unittest.TestCase):
    def test_rpc(self):
        loop = ioloop.IOLoop.current()
        req_message = "asdf"
        rep_message = "fdsa"
        def request_handler(msg, send_reply):
            self.assertEqual(msg, req_message)
            self.assertIsNotNone(send_reply)
            send_reply(rep_message)
        def reply_handler(msg):
            self.assertEqual(msg, rep_message)
            loop.stop()
        def send_request():
            req.send(req_message, reply_handler)
        rep = ReplyServer(loop, "topic", request_handler)
        rep.bind()
        req = RequestClient(loop, "topic")
        req.connect(rep.address, rep.port)
        loop.call_later(0.1, send_request)
        loop.start()

    def test_rpc_timeout(self):
        loop = ioloop.IOLoop.current()
        req_message = "asdf"
        rep_message = "fdsa"
        def timeout_handler():
            self.assertTrue(True)
            loop.stop()
        def request_handler(msg, send_reply):
            self.assertEqual(msg, req_message)
            self.assertIsNotNone(send_reply)
            # delay the reply to trigger the timeout
            loop.call_later(0.2, send_reply, rep_message)
        def reply_handler(msg):
            # This shouldn't trigger
            self.assertTrue(False)
        def send_request():
            req.send(req_message, reply_handler, 0.1, timeout_handler)
        rep = ReplyServer(loop, "topic", request_handler)
        rep.bind()
        req = RequestClient(loop, "topic")
        req.connect(rep.address, rep.port)
        loop.call_later(0.1, send_request)
        loop.start()

if __name__ == '__main__':
    unittest.main()