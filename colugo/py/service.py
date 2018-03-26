#!/usr/bin/env python

import socket
from zeroconf import ServiceInfo
import zmq

COLUGO_TYPE_STR = "_colugo._tcp.local."


class Service:
    """Wrapper object for individual service sockets

    Attributes:
        topic: Topic string associated with the socket
        address: Address string (eg, 127.0.0.1) associated with the socket
        port: Integer where the socket is bound
        socket_type: ZMQ socket type (int)
        node_uuid: Unique identifier of the node that contains the service
        mdns_name: Name string of the service as identified by zeroconf (eg., _topicname._uuid._colugo._tcp.local.)
        server: Bool if the socket type is a server or a client TODO(pickledgator): maybe dont need this
    """

    def __init__(self, topic=None, address=None, port=None, socket_type=None, node_uuid=None, socket=None):
        """Constructor for a Service

        Most of the parameters can be defaulted to None at construction time, since helper functions
        are provided as part of the class (eg, fill_from_info). Python doesn't support multiple 
        constructors!

        Args:
            topic: Topic string associated with the socket (default: None)
            address: Address string (eg, 127.0.0.1) associated with the socket (default: None)
            port: Integer where the socket is bound (default: None)
            socket_type: ZMQ socket type (int) (default: None)
            node_uuid: Unique identifier of the local node where the directory is housed (default: None)
            socket: Reference to the socket object associated with the service (default: None)
        """
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
        """Generate zeroconf.ServiceInfo object from class data

        Returns:
            zeroconf.ServiceInfo: Zeroconf service object filled with the same information from the class
        """
        info = ServiceInfo(type_=COLUGO_TYPE_STR,
                           name=self.mdns_name,
                           address=socket.inet_aton(self.address),
                           port=self.port,
                           # server='{}.local.'.format(socket.gethostname()),
                           properties={"topic": self.topic, "socket_type": str(self.socket_type), "node_uuid": self.node_uuid})
        return info

    def fill_from_info(self, info):
        """Generate class data based on a zeroconf ServiceInfo object

        Args:
            info: zeroconf.ServiceInfo object used to extract socket information

        Returns:
            colugo.py.Service: Service object
        """
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
        """Custom comparitor for class

        Currently checks to see if the topic, address, port, socket_type and node_uuid are the same

        Args:
            s: colugo.py.Service object to compare

        Returns:
            Bool: If elements of the two objects are the same
        """

        return (self.topic == s.topic) and (self.address == s.address) and (self.port == s.port) \
            and (self.socket_type == s.socket_type) and (self.node_uuid == s.node_uuid)

    def __str__(self):
        """String representation of the class

        Returns:
            String: Serialized string that can be printed
        """
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
        """Serialization for lists of the class

        Returns:
            String: The serialized string for each element in the list
        """
        return self.__str__()
