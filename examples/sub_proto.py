#!/usr/bin/env python

import os
import sys
# local path to library
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import proto.test_pb2
from colugo.node import Node

class SubscriberExample(Node):
    def __init__(self, name):
        super(SubscriberExample, self).__init__(name)
        self.subscriber = self.add_subscriber("tcp://127.0.0.1:50000", self.callback)

    def callback(self, message):
        msg = proto.test_pb2.TestMessage()
        try:
            msg.ParseFromString(message)
            self.logger.info("Received message!\n{}".format(msg))
        except Exception as e:
            self.logger.error("Failed to parse message")


if __name__ == "__main__":

    sub_example_node = SubscriberExample("SubscriberExample")
    # this will block while there is work to be done by the ioloop
    sub_example_node.start()



