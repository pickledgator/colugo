#!/usr/bin/env python

import os
import sys
from colugo.py.node import Node

class PublisherExample(Node):
    def __init__(self, name):
        Node.__init__(self, name)
        self.publisher = self.add_publisher("tcp://127.0.0.1:50000")
        self.repeater = self.add_repeater(1000, self.callback)

    def callback(self):
        self.publisher.send("Message")

if __name__ == "__main__":

    pub_test_node = PublisherExample("PubExample")
    # this will block while there is work to be done by the ioloop
    pub_test_node.start()
