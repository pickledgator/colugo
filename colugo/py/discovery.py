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

# class TopicMap:
#     """Tree structure storing information about discovered services, their topics and their addresses

#     Example tree structure
#     {
#         'topic.name.1': {
#             'service.name.1': ServiceInfo(),
#             'service.name.2': ServiceInfo()
#             }
#         'topic.name.2': {
#             'service.name.1': ServiceInfo(),
#             'service.name.2': ServiceInfo()
#             }
#     }

#     """
#     def __init__(self):
#         # map with keys by topic
#         self.map = {}

#     def add(self, info):
#         # clean up the utf encodings from zeroconf
#         topic_name = info.properties[b'topic'].decode('utf-8')
#         service_name = info.name
#         # check to see if our topic already exists in the map
#         if topic_name in self.map:
#             # check to see if our specific service already exists within the individual topic identifier
#             if service_name in self.map[topic_name]:
#                 self.logger.error("Service {} already exists in map".format(service_name))
#                 return False
#             else:
#                 # otherwise add the service to the map, within the topic key
#                 self.map[topic_name][service_name] = info
#         # otherwise, if our topic is not already in the map, create a new list out of the new service
#         else:
#             self.map[topic_name] = {service_name: info}

#         return True

#     def remove(self, service_name, topic_name):
#         removed = False
#         # check to see if our topic is in the map at all
#         if topic_name in self.map:
#             if service_name in self.map[topic_name]:
#                 del self.map[topic_name][service_name]
#                 removed = True
#             # if all of our services have been removed for a specific topic, delete the topic from the map
#             if len(self.map[topic_name].items()) == 0:
#                 del self.map[topic_name]
#         return True if removed else False

#     def contains(self, info):
#         return True if info.name in self.map else False

# def topic_from_service(service_name, service_type):
#     # remove service_type from the end of the string, then ignore the first element ("_")
#     # eg., _topic.name.1._colugo._tcp._local. -> topic.name.1
#     return service_name.replace(service_type, "")[1:]


class Service:

    def __init__(self, topic=None, address=None, port=None, socket_type=None, node_uuid=None, socket=None):
        self.topic = topic
        # stored as a string, and converted to bytes socket.inet_aton when compiling ServiceInfo packet
        self.address = address
        self.port = port
        self.socket = socket
        self.socket_type = socket_type
        self.node_uuid = node_uuid
        self.mdns_name = "_{}.{}".format(self.topic, COLUGO_TYPE_STR)
        self.server = True if (socket_type == zmq.PUB or socket_type == zmq.REP) else False

    def get_service_info(self):
        info = ServiceInfo(type_=COLUGO_TYPE_STR,
                           name=self.mdns_name,
                           address=socket.inet_aton(self.address),
                           port=self.port,
                           # server='{}.local.'.format(socket.gethostname()),
                           properties={"topic": self.topic, "socket_type": self.socket_type, "node_uuid": self.node_uuid})
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
        # TODO(pickledgator): this needs to be zmq.PUB type
        self.socket_type = socket_type_from_int(info.properties['socket_type'.encode('utf-8')])
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

    def remove(self, service):
        for s in self.services:
            # use Service eq operator to compare service definitions
            if s == service:
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

    def service_from_zeroconf_query(self, topic):
        def fix_socket_type(info):
            # For whatever reason, zeroconf is casting a property=1 to property=True
            # This just undoes that cast since socket_type will be an int (not bool)
            if info.properties['socket_type'.encode('utf-8')] == True:
                info.properties['socket_type'.encode('utf-8')] = 1
            return info

        info = ServiceInfo(type_=COLUGO_TYPE_STR,
                           name="_{}.{}".format(topic, COLUGO_TYPE_STR))
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

    def stop_listening(self):
        self.zeroconf.remove_all_service_listeners()

    def stop(self):
        self.unregister_all_servers()
        self.zeroconf.close()

    def topic_from_mdns_name(self, name):
        # assumes name is rigidly structured eg, _topic.string._colugo._tcp.local.
        tokens = [t[:-1] for t in name.split("_")][1:]
        return tokens[0]

    def add_service(self, zeroconf, service_type, name):
        """This function is utilized by the ServiceBrowser callbacks
        """
        # get details of the newly discovered service
        topic = self.topic_from_mdns_name(name)
        # generate our full topic object from the acquired info
        service = self.service_from_zeroconf_query(topic)
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
        # self.directory.remove(s)
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
