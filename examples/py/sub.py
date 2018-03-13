#!/usr/bin/env python

import os
import sys
from colugo.py.node import Node

class SubscriberExample(Node):
    def __init__(self, name):
        super(SubscriberExample, self).__init__(name)
        self.subscriber = self.add_subscriber("tcp://127.0.0.1:50000", self.callback)

    def callback(self, message):
        self.logger.info("Received message: {}".format(message))

if __name__ == "__main__":

    sub_example_node = SubscriberExample("SubscriberExample")
    # this will block while there is work to be done by the ioloop
    sub_example_node.start()



