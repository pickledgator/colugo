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

from colugo.py.service import Service
from colugo.py.directory import Directory

logging.basicConfig(
    format="[%(asctime)s][%(name)s](%(levelname)s) %(message)s", level=logging.DEBUG)
COLUGO_TYPE_STR = "_colugo._tcp.local."


class Discovery:
    """Utility class for socket service discovery built on top of zeroconf
    
    Since individual sockets must be bound and connect using protocols, addresses and ports, a
    service discovery layer is utilized to map topic strings for each server client to the 
    appropriate protocol, address and port on the network. Services (zmq sockets that bind to ports) 
    are broadcast as zeroconf services using mdns (to both bonjour and avahi). Then, a listener 
    receives those broadcasts and passes them upstream so connections can be made by clients that are
    looking for those services.

    Naming conventions:
        service: Any zmq socket with an associated topic, address and port (local or remote)
        client: Any zmq socket (service) that connects to a port at an address
        server: Any zmq socket (service) that binds to a port
        directory: List of services
        servers: Directory of servers
        clients: Directory of clients

    Attributes:
        logger: Logger instance, specific to activities within the service discovery layers
        zeroconf: Zeroconf object that runs it's own thread and handles mdns broadcasts
        browser: Zeroconf object that listens for changes in service being broadcast
        node_uuid: Unique identifier for the node that houses this class object
        on_add: Application level callback for when new services are received by the browser
        on_remove: Application level callback for when removed services are received by the browser
        servers: Maintains a list of servers that are known to be active on the network
        clients: Maintains a list of clients that are known to be active on the network
    """

    def __init__(self, node_uuid, on_add, on_remove):
        """Constructor
        
        Args:
            node_uuid: Unique identifier for the node that houses this class object
            on_add: Callback for when new services are received by the browser
            on_remove: Callback for when removed services are received by the browser
        """
        # grab the logger with the same name as the node
        self.logger = logging.getLogger("Discovery")
        self.zeroconf = Zeroconf()
        self.browser = ServiceBrowser(self.zeroconf, "_colugo._tcp.local.", self)
        self.node_uuid = node_uuid
        self.on_add = on_add
        self.on_remove = on_remove
        self.servers = Directory(self.node_uuid)
        self.clients = Directory(self.node_uuid)

    def register_server(self, topic, socket_type, node_uuid, socket, address, port):
        """Informs zeroconf that a new service should be broadcast to the network

        This is typically used when a server socket is being constructed by a node.

        This should be used for zmq sockets that bind as servers only. Clients should not be 
        broadcast over the network since they simply observe.

        Args:
            topic: Topic string associated with the socket
            socket_type: ZMQ socket type (int) (default: None)
            node_uuid: Unique identifier of the local node where the socket is located
            socket: Integer where the socket is bound
            address: Address string (eg, 127.0.0.1) associated with the socket
            port: Integer where the socket is bound
        """
        service = Service(topic, address, port, socket_type, node_uuid, socket)
        # for local sockets, we need to add to the directory manually, not from the mdns callback
        # since we won't have access to the socket object for the mdns callbacks
        self.servers.add(service)
        self.zeroconf.register_service(service.get_service_info())

    def unregister_server(self, service):
        """Informs zeroconf that a service is being removed and broadcasts that to the network
        
        This is typically used when a server socket (or an entire node) is going down.

        Args:
            service: colugo.py.Service object to broadcast as being removed
        """
        self.zeroconf.unregister_service(service.get_service_info())

    def register_client(self, topic, socket_type, node_uuid, socket, address=None, port=None):
        """Add a client to the clients directory

        This will not broadcast the service over zeroconf since other nodes don't care about clients.
        TODO(pickledgator): Can server sockets detect if clients connect/disconnect? Do we care?

        Args:
            topic: Topic string associated with the socket
            socket_type: ZMQ socket type (int)
            node_uuid: Unique identifier of the local node where the socket is located
            socket: Integer where the socket is bound
            address: Address string (eg, 127.0.0.1) associated with the socket (default: None)
            port: Integer where the socket is bound (default: None)
        """
        service = Service(topic, address, port, socket_type, node_uuid, socket)
        self.clients.add(service)

    def unregister_client(self, service):
        """Remove a client from the clients directory

        Args:
            service: colugo.py.Service object to remove
        """
        # TODO(pickledgator): Do other network servers/clients care if a local client goes down?
        self.clients.remove(service)

    def service_from_zeroconf_query(self, topic, uuid):
        """Helper function to create a colguo.py.Service from a zeroconf query

        Args:
            topic: Topic string associated with the socket
            uuid: Unique identifier of the local node where the socket is located
        
        Returns:
            colugo.py.Service|None: Populated service if found on the network, otherwise None
        """
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
        """Helper function to unregister all services that are servers
        
        This is typically called when an entire node is exiting.
        """
        for s in self.servers.services:
            if s.node_uuid == self.node_uuid:
                self.unregister_server(s)

    def unregister_all_clients(self):
        """Helper function to unregister all services that are clients
        
        This is typically called when an entire node is exiting.
        """
        for c in self.clients.services:
            if c.node_uuid == self.node_uuid:
                self.unregister_client(c)

    def stop_listening(self):
        """Stop the zeroconf browser callbacks from firing.

        Techicanlly speaking, zeroconf.close() also calls this, but it turns out that when
        nodes are exiting, they spam the network that their sockets are going down and we 
        get loop back messages for the local node's sockets. Since we don't care about these 
        loopback messages when a node is closing, we just turn of the service listeners for 
        zeroconf early.
        """
        self.zeroconf.remove_all_service_listeners()

    def stop(self):
        """Stop zeroconf and clean up threads
        """
        self.unregister_all_servers()
        self.zeroconf.close()

    def topic_from_mdns_name(self, name):
        """Helper to get topic and uuid information about a service
        
        Args:
            name: mdns name to parse

        Returns:
            (String, String): Topic string and uuid string of the socket
        """
        # assumes name is rigidly structured eg, _topic.string._colugo._tcp.local.
        tokens = [t[:-1] for t in name.split("_")][1:]
        return (tokens[0], tokens[1])

    def add_service(self, zeroconf, service_type, name):
        """This function is utilized by the zeroconf.ServiceBrowser callbacks
        """
        # get details of the newly discovered service
        (topic, uuid) = self.topic_from_mdns_name(name)
        # generate our full topic object from the acquired info
        service = self.service_from_zeroconf_query(topic, uuid)
        if service:
            self.logger.debug("Service added: {}".format(name))
            # try to add the topic to the directory
            # this will fail for local topics that were already added
            if not self.servers.check_existance(service):
                if self.servers.add(service):
                    self.on_add(service)

    def remove_service(self, zeroconf, service_type, name):
        """This function is utilized by the zeroconf.ServiceBrowser callbacks
        """
        (topic, uuid) = self.topic_from_mdns_name(name)
        self.logger.debug("Service removed: {}".format(name))
        # By time this callback occurs, we can no longer access the ServiceInfo
        # for the specified service, so we can have to remove our service from the
        # Directory based on the topic only.
        # TODO(pickledgator): This wont work if we have two services with the same topic
        # within the same node, however it works fine if the two services with the same
        # topic are on different nodes (due to inclusion of the uuid in the check)
        self.servers.remove(topic, uuid)
        self.on_remove(topic)
