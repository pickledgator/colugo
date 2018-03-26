#!/usr/bin/env python

import logging


class Directory:
    """Maintainer of discovered services on the network

    Attributes:
        logger: Logger instance, specific to activities within the service discovery layers
        node_uuid: Unique identifier of the local node where the directory is housed
        servces: List of services that are currently active on the network (servers only)
    """

    def __init__(self, node_uuid):
        """Constructor

        Args:
            node_uuid: Unique identifier of the local node where the directory is housed
        """
        self.logger = logging.getLogger("Discovery")
        self.node_uuid = node_uuid
        self.services = []

    def add(self, service):
        """Add a newly discovered service to the directory

        Args:
            service: Service object that contains information about the socket
        
        Returns:
            Bool: If add to directory was successful or not
        """
        if self.check_existance(service):
            self.logger.warn("Service {}@{} already exists!".format(service.mdns_name, service.node_uuid))
            return False
        self.services.append(service)
        return True

    def check_existance(self, service):
        """Check if a service already exists in the directory

        Uses custom colugo.py.Service comparitor to evaluate existence within directory

        Args:
            service: Service object that contains information about the socket

        Returns:
            Bool: If service exists in the directory
        """
        for s in self.services:
            # use Service eq operator to compare service definitions
            if s == service:
                return True
        return False

    def remove(self, topic, service_uuid):
        """Remove a service from the directory

        TODO(pickledgator): This breaks down if there are more than one service in the directory
        with the same topic name. Requires modifications of zeroconf-python so that the remove
        callback returns additional information besides just the mdns name. For now we can also
        check for the uuid, but this will still break down if a single node has more than one service
        with the same topic.

        Args:
            topic: Topic string of the service to be removed

        Returns:
            Bool: If remove from directory was successful or not
        """
        for s in self.services:
            # since we only have access to the topic and uuid from the mdns name
            # we can't use the colugo.py.Service comparitor here
            if s.topic == topic and s.node_uuid == service_uuid:
                self.services.remove(s)
                return True
        return False
