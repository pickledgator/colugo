#!/usr/bin/env python

import os
import sys
import examples.proto.test_pb2
from colugo.py.node import Node

class PublisherExample(Node):
    def __init__(self, name):
        Node.__init__(self, name)
        self.publisher = self.add_publisher("tcp://127.0.0.1:50000")
        self.repeater = self.add_repeater(1000, self.callback)
        self.count = 0

    def callback(self):
        test_message = examples.proto.test_pb2.TestMessage()
        test_message.message = "This is a message"
        test_message.id = 0
        test_message.value = self.count
        self.publisher.send(test_message.SerializeToString())
        self.count += 1

if __name__ == "__main__":

    pub_test_node = PublisherExample("PubExample")
    # this will block while there is work to be done by the ioloop
    pub_test_node.start()
