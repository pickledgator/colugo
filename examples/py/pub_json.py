#!/usr/bin/env python

import json
import os
import sys
from colugo.py.node import Node

class PublisherExample(Node):
    def __init__(self, name):
        Node.__init__(self, name)
        self.publisher = self.add_publisher("json.pub.topic")
        self.repeater = self.add_repeater(1000, self.callback)
        self.count = 0

    def callback(self):
        json_message = json.dumps({"message": "This is a message", "id": 0, "value": self.count})
        self.publisher.send(json_message)
        self.count += 1

if __name__ == "__main__":

    pub_test_node = PublisherExample("PubExample")
    # this will block while there is work to be done by the ioloop
    pub_test_node.start()
