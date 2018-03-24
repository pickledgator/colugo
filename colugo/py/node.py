#!/usr/bin/env python

import functools
import logging
import os
import sys
import signal
import threading
import time
from tornado import ioloop
import uuid
import zmq
from zmq.eventloop.zmqstream import ZMQStream

from colugo.py.discovery import Discovery
from colugo.py.publisher import Publisher
from colugo.py.subscriber import Subscriber
from colugo.py.request_client import RequestClient
from colugo.py.reply_server import ReplyServer
from colugo.py.repeater import Repeater

logging.basicConfig(
    format="[%(asctime)s][%(name)s](%(levelname)s) %(message)s", level=logging.DEBUG)


class Node:
    """Outer container for ioloop and zmq sockets

    Attributes:
        name: The name of the node, used to identify the logger
        logger: Logger instance, specific to activities within the node
        loop: Tornado event loop, socket send/receive, timers operate on this
        uuid: Globally (nearly) unique identifier of the node
        discovery: Contains zeroconf threads and the topic/socket directories
    """

    def __init__(self, name):
        """Constructor for the node class

        Args:
            name: Name of the node, used for the logger name
        """
        self.name = name
        self.logger = logging.getLogger(self.name)
        self.logger.info("Node {} is initializing".format(self.name))
        self.loop = ioloop.IOLoop.current()
        self.uuid = str(uuid.uuid1())
        self.discovery = Discovery(name, self.uuid, self.add_service_handler, self.remove_service_handler)
        # exit conditions
        signal.signal(signal.SIGINT, lambda sig, frame: self.loop.add_callback_from_signal(self.stop))

    def start(self):
        """Start the event loop
        """
        self.logger.info("Node {} is starting".format(self.name))
        self.loop.start()  # blocking

    def stop(self):
        """ Stop the event loop and close all open sockets
        """
        self.logger.info("Node {} is stopping".format(self.name))
        self.discovery.stop()
        self.loop.stop()

    def add_repeater(self, delay_ms, callback):
        """Helper function to add a repeater to the node using the node's event loop
            Use functools.partial(callback, arg1, arg2, etc.) to pass arguemnts to callback

        Args:
            delay_ms: Number of milliseconds between callback executions
            callback: Function to execute on repeat

        Returns:
            colugo.py.repeater object that the application layer can manipulate
        """
        self.logger.info("Adding repeater to node {} with rate {}ms".format(self.name, delay_ms))
        rep = Repeater(self.loop, delay_ms, callback)
        return rep

    def add_delayed_callback(self, delay_ms, callback):
        """Helper function to execute a callback function at a time in the future

        Args:
            delay_ms: Number of milliseconds in the future when you want the callback to fire
            callback: Function to execute
        """
        self.loop.call_later(delay_ms / 1000.0, callback)

    def add_publisher(self, topic):
        """Helper function to add a colugo.py.Publisher object to the node

        Each individual Node may only have one publisher per topic, however, multiple Nodes (local or remote)
        can have a publisher using the same topic. 

        The topic should be a string with no alpha-numeric characters and periods or / only; 
        no special characters, and especially no "_" characters.

        Args:
            topic: Topic string that identifies the socket on the network

        Returns:
            colugo.py.Publisher object, call send() to send a message
        """
        # Since the socket binds to a random open port as a server, we need to grab the port after socket creation
        sock = Publisher(self.loop, topic)
        # bind immediately so we can publish the correct address and port in the zeroconf broadcast
        sock.bind()
        self.discovery.register_server(topic, zmq.PUB, self.uuid, sock, sock.address, sock.port)
        return sock

    def add_subscriber(self, topic, callback, on_connect):
        """Helper function to add a colugo.py.Subscriber object to the node

        Each individual Node may have numerous subscribers using the same topic, and multiple Nodes (local or remote)
        can numerous subscribers using the same topic. 

        The topic should be a string with no alpha-numeric characters and periods or / only; 
        no special characters, and especially no "_" characters.

        Args:
            topic: Topic string that identifies the socket on the network
            callback: Function handler when messages are received
            on_connect: Callback handler when a connection is made with the publisher socket

        Returns:
            colugo.py.Subscriber object
        """
        sock = Subscriber(self.loop, topic, callback)
        self.discovery.register_client(topic, zmq.SUB, node_uuid=self.uuid, socket=sock)
        return sock

    def add_reply_server(self, topic, callback):
        """Helper function to add a colugo.py.ReplyServer object to the node

        Each individual Node may only have one reply server per topic, however, multiple Nodes (local or remote)
        can have a reply server using the same topic. Important note that if multiple nodes have a reply server
        with the same topic name, each request send() will go to one or the other reply server, ie, each request
        will round robin. 

        The topic should be a string with no alpha-numeric characters and periods or / only; 
        no special characters, and especially no "_" characters.

        TODO(pickledgator): Re-think the round robin pattern when multiple reply servers share the same topic.

        Args:
            topic: Topic string that identifies the socket on the network
            callback: Function handler when a request message is received

        Returns:
            colugo.py.ReplyServer object
        """
        sock = ReplyServer(self.loop, topic, callback)
        sock.bind()
        self.discovery.register_server(topic, zmq.REP, self.uuid, sock, sock.address, sock.port)
        return sock

    def add_request_client(self, topic, on_connect):
        """Helper function to add a colugo.py.RequestClient object to the node

        Each individual Node may have multiple request clients using the same topic and multiple Nodes 
        (local or remote) can have as many request clients using the same topic. Important note that 
        if multiple nodes have a reply server with the same topic name, each request send() will go 
        to one or the other reply server, ie, each request will round robin. 

        The topic should be a string with no alpha-numeric characters and periods or / only; 
        no special characters, and especially no "_" characters.

        Use send(msg, callback, timeout, on_timeout) to send a request to a connected reply server
        where timeout is in milliseconds, and on_timeout is the callback handler when a timeout on the
        reply occurs.

        Args:
            topic: Topic string that identifies the socket on the network
            on_connect: Callback handler when a connection is made with the reply server socket

        Returns:
            colugo.py.RequestClient object
        """
        sock = RequestClient(self.loop, topic, on_connect)
        self.discovery.register_client(topic, zmq.REQ, node_uuid=self.uuid, socket=sock)
        return sock

    def add_service_handler(self, service):
        """Callback handler for when the discovery thread finds a new service on the network

        This callback is used to allow client sockets to automatically connect to new services
        that appear on the network. When a new service is announced, it will iterate through 
        the local clients list and if any topics match to broadcast server topic, try to connect. 
        This should apply both local servers and remote servers.

        Args:
            service: colugo.py.Service object containing information about the new service
        """
        for client in self.discovery.clients.services:
            if service.topic == client.topic and client.socket:
                client.socket.connect(service.address, service.port)

    def remove_service_handler(self, topic):
        """Callback handler for when the discovery thread identifies that a service has been removed
        from the network.

        It's important to note that since python zeroconf has no way to obtain the full service info
        from the service after it has been removed, the only data we have available for this callback
        is the topic name (derived from the mdns name that left the network).

        TODO(pickledgator): Look into refactoring zeroconf to provide more than just the mdns name for
        add and remove callbacks within the browser.

        Args:
            topic: The topic string associated with the service that was removed from the network

        """
        for client in self.discovery.clients.services:
            if topic == client.topic and client.socket:
                self.logger.warn("Service {} removed, but still associated with local client".format(topic))
                # TODO(pickledgator): Figure out why this method fails when discovery finds a disconnect
                # Does zmq automatically call disconnect for us somehow?
                # client.socket.disconnect()
