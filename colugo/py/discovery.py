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
# TODO(pickledgator): can we remove this dependency?
import zmq

logging.basicConfig(
    format="[%(asctime)s][%(name)s](%(levelname)s) %(message)s", level=logging.DEBUG)

COLUGO_TYPE_STR = "_colugo._tcp.local."


class Service:

    def __init__(self, topic=None, address=None, port=None, socket_type=None, node_uuid=None, socket=None):
        self.topic = topic
        # stored as a string, and converted to bytes socket.inet_aton when compiling ServiceInfo packet
        self.address = address
        self.port = port
        self.socket = socket
        # this is stored as a zmq socket type (int) and converted to an str(int) when compiling ServiceInfo packet
        self.socket_type = socket_type
        self.node_uuid = node_uuid
        self.mdns_name = "_{}._{}.{}".format(self.topic, self.node_uuid, COLUGO_TYPE_STR)
        self.server = True if (socket_type == zmq.PUB or socket_type == zmq.REP) else False

    def get_service_info(self):
        info = ServiceInfo(type_=COLUGO_TYPE_STR,
                           name=self.mdns_name,
                           address=socket.inet_aton(self.address),
                           port=self.port,
                           # server='{}.local.'.format(socket.gethostname()),
                           properties={"topic": self.topic, "socket_type": str(self.socket_type), "node_uuid": self.node_uuid})
        return info

    def fill_from_info(self, info):
        def socket_type_from_int(value):
            if value == 1:
                return zmq.PUB
            elif value == 2:
                return zmq.SUB
            elif value == 3:
                return zmq.REQ
            elif value == 4:
                return zmq.REP
            else:
                return None

        self.address = socket.inet_ntoa(info.address)
        self.port = info.port
        self.socket_type = socket_type_from_int(int(info.properties['socket_type'.encode('utf-8')]))
        self.node_uuid = info.properties['node_uuid'.encode('utf-8')].decode('utf-8')
        self.topic = info.properties['topic'.encode('utf-8')].decode('utf-8')
        self.mdns_name = info.name
        self.server = True if (self.socket_type == zmq.PUB or self.socket_type == zmq.REP) else False
        return self

    def __eq__(self, s):
        return (self.topic == s.topic) and (self.address == s.address) and (self.port == s.port) \
            and (self.socket_type == s.socket_type) and (self.node_uuid == s.node_uuid)

    def __str__(self):
        def socket_str(value):
            if value == 1:
                return "PUB"
            elif value == 2:
                return "SUB"
            elif value == 3:
                return "REQ"
            elif value == 4:
                return "REP"
            else:
                return "?"
        return "Service({}): {}@{} | {}@{}".format(self.topic, self.address, self.port, socket_str(self.socket_type), self.node_uuid)

    def __repr__(self):
        return self.__str__()


class Directory:

    def __init__(self, node_uuid):
        self.node_uuid = node_uuid
        self.services = []
        self.logger = logging.getLogger("Discovery")

    def add(self, service):
        if self.check_existance(service):
            self.logger.warn("Service {}@{} already exists!".format(service.mdns_name, service.node_uuid))
            return False
        self.services.append(service)
        return True

    def check_existance(self, service):
        for s in self.services:
            # use Service eq operator to compare service definitions
            if s == service:
                return True
        return False

    def remove(self, topic):
        for s in self.services:
            # use Service eq operator to compare service definitions
            if s.topic == topic:
                self.services.remove(s)
                return True
        return False


class Discovery:

    def __init__(self, name, node_uuid, on_add, on_remove):
        # grab the logger with the same name as the node
        self.logger = logging.getLogger("Discovery")
        self.zeroconf = Zeroconf()
        self.browser = ServiceBrowser(self.zeroconf, "_colugo._tcp.local.", self)
        self.node_uuid = node_uuid
        self.on_add = on_add
        self.on_remove = on_remove
        self.directory = Directory(self.node_uuid)
        self.clients = Directory(self.node_uuid)

    def register_server(self, topic, socket_type, node_uuid, socket, address, port):
        service = Service(topic, address, port, socket_type, node_uuid, socket)
        # for local sockets, we need to add to the directory manually, not from the mdns callback
        # since we won't have access to the socket object for the mdns callbacks
        self.directory.add(service)
        self.zeroconf.register_service(service.get_service_info())

    def unregister_server(self, service):
        self.zeroconf.unregister_service(service.get_service_info())

    def register_client(self, topic, socket_type, node_uuid, socket, address=None, port=None):
        service = Service(topic, address, port, socket_type, node_uuid, socket)
        self.clients.add(service)

    def unregister_client(self, service):
        # TODO(pickledgator): Do other network servers/clients care if a local client goes down?
        self.clients.remove(service)

    def service_from_zeroconf_query(self, topic, uuid):
        def fix_socket_type(info):
            # For whatever reason, zeroconf is casting a property=1 to property=True
            # This just undoes that cast since socket_type will be an int (not bool)
            if info.properties['socket_type'.encode('utf-8')] == True:
                info.properties['socket_type'.encode('utf-8')] = 1
            return info

        info = ServiceInfo(type_=COLUGO_TYPE_STR,
                           name="_{}._{}.{}".format(topic, uuid, COLUGO_TYPE_STR))
        res = info.request(self.zeroconf, 1000)
        address = port = node_uuid = None
        service = Service()
        if res:
            info = fix_socket_type(info)
            service.fill_from_info(info)
            return service
        return None

    def unregister_all_servers(self):
        for s in self.directory.services:
            if s.node_uuid == self.node_uuid:
                self.unregister_server(s)

    def unregister_all_clients(self):
        for c in self.clients.services:
            if c.node_uuid == self.node_uuid:
                self.unregister_client(c)

    def stop_listening(self):
        self.zeroconf.remove_all_service_listeners()

    def stop(self):
        self.unregister_all_servers()
        self.zeroconf.close()

    def topic_from_mdns_name(self, name):
        # assumes name is rigidly structured eg, _topic.string._colugo._tcp.local.
        tokens = [t[:-1] for t in name.split("_")][1:]
        return (tokens[0], tokens[1])

    def add_service(self, zeroconf, service_type, name):
        """This function is utilized by the ServiceBrowser callbacks
        """
        # get details of the newly discovered service
        (topic, uuid) = self.topic_from_mdns_name(name)
        # generate our full topic object from the acquired info
        service = self.service_from_zeroconf_query(topic, uuid)
        if service:
            self.logger.debug("Service added: {}".format(name))
            # try to add the topic to the directory
            # this will fail for local topics that were already added
            if not self.directory.check_existance(service):
                if self.directory.add(service):
                    self.on_add(service)

    def remove_service(self, zeroconf, service_type, name):
        """This function is utilized by the ServiceBrowser callbacks
        """
        topic = self.topic_from_mdns_name(name)
        self.logger.debug("Service removed: {}".format(name))
        # By time this callback occurs, we can no longer access the ServiceInfo
        # for the specified service, so we can have to remove our service from the
        # Directory based on the topic only.
        # TODO(pickledgator): This wont work if we have two services with the same topic
        self.directory.remove(topic)
        self.on_remove(topic)

if __name__ == "__main__":

    import time
    import uuid

    discovery = Discovery("DiscoveryTest")
    count = 0
    while True:
        # print("Topic Map:\n{}".format(discovery.topics.map))
        print(".")
        node_uuid = str(uuid.uuid1())
        if count == 3:
            discovery.register_topic("test/topic", "PUB", "127.0.0.1", 10001, node_uuid)
        if count == 5:
            discovery.register_topic("test/topic", "PUB", "127.0.0.1", 10001, node_uuid)
        count += 1
        time.sleep(1)
