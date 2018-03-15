#!/usr/bin/env python

import json
import os
import sys
from colugo.py.node import Node

class SubscriberExample(Node):
    def __init__(self, name):
        super(SubscriberExample, self).__init__(name)
        self.subscriber = self.add_subscriber("tcp://127.0.0.1:50000", self.callback)

    def callback(self, message):
        # Decode UTF-8 bytes to Unicode, and convert single quotes 
        # to double quotes to make it valid JSON
        msg_unicode = message.decode('utf8').replace("'", '"')
        json_message = json.loads(msg_unicode)
        self.logger.info("Received message!\n{}".format(json_message))

if __name__ == "__main__":

    sub_example_node = SubscriberExample("SubscriberExample")
    # this will block while there is work to be done by the ioloop
    sub_example_node.start()



