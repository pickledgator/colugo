#!/usr/bin/env python

import os
import sys
from colugo.py.node import Node
import functools
import time
import threading

class RequestClientExample(Node):
    def __init__(self, name):
        Node.__init__(self, name)
        self.request_client = self.add_request_client("rpc.topic", self.connect_handler)
        # self.repeater = self.add_repeater(1000, self.request_sender)
        self.counter = 0
        
    def connect_handler(self):
        self.request_sender()

    def request_sender(self):
        self.logger.info("Sending request: Message {}".format(self.counter))
        self.request_client.send("Message {}".format(self.counter), self.reply_callback, timeout_handler = self.request_timeout)
        self.counter += 1

    def request_timeout(self):
        self.logger.error("Request timed out")

    def reply_callback(self, message):
        self.logger.info("Got reply: {}".format(message))
        self.add_delayed_callback(1000, self.request_sender)

if __name__ == "__main__":

    req_example_node = RequestClientExample("RequestClient")
    req_example_node.start()
