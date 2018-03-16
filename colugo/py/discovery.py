#!/usr/bin/env python

import logging
import socket
from zeroconf import (
    ServiceInfo,
    ServiceBrowser,
    ServiceStateChange,
    Zeroconf,
    ZeroconfServiceTypes,
)

class Discovery:

    def __init__(self, name):
        # grab the logger with the same name as the node
        self.logger = logging.getLogger(name)
        self.zeroconf = Zeroconf()
        self.browser = ServiceBrowser(self.zeroconf, "_colugo._tcp.local.", self)

    def register_topic(self, topic, socket_type, address, port):
        type_str = "_colugo._tcp.local."
        info = ServiceInfo(type_ = type_str,
                           name = "_{}.{}".format(topic, type_str),
                           address = socket.inet_aton(address),
                           port = port,
                           weight = 0,
                           priority = 0,
                           properties = {"socket_type": socket_type})
        self.zeroconf.register_service(info)

    def unregister_topic(self, topic, socket_type):
        type_str = "_colugo._tcp.local."
        info = ServiceInfo(type_ = type_str,
                           name = "_{}.{}".format(topic, type_str))
        self.zeroconf.unregister_service(info)

    def unregister_all_topics(self):
        self.zeroconf.unregister_all_services()

    def add_service(self, zeroconf, service_type, name):
        info = zeroconf.get_service_info(service_type, name)
        self.logger.debug("Service added: {} {}".format(name, info))

    def print_services(self):
        print(self.browser.services)

    def remove_service(self, zeroconf, service_type, name):
        self.logger.debug("Service removed: {}".format(name))
