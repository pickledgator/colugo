#!/usr/bin/env python

import os
import sys
from colugo.py.node import Node

class ReplyServerExample(Node):
    def __init__(self, name):
        Node.__init__(self, name)
        self.reply_server = self.add_reply_server("rpc.topic", self.request_callback)

    def request_callback(self, message, reply):
        self.logger.info("Got request message: {}".format(message))
        reply(message)

if __name__ == "__main__":

    rep_example_node = ReplyServerExample("ReplyServer")
    rep_example_node.start()
