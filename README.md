# Colugo [![Build Status](https://travis-ci.org/pickledgator/colugo.svg?branch=master)](https://travis-ci.org/pickledgator/colugo)

Colugo is a [0MQ](http://zeromq.org/) wrapper that provides an asynchronous application layer networking structure, abstracting the complexities of the low level C reference implementation of libzmq and adding additional functionality and robustness.

Colugo adds capability on top of zmq in the following ways:
* Service discovery using zeroconf
* Support for listening timeouts in rep-req patterns
* Non-dependence on any particular serialization of messages
* Automated logging and playback of message streams (TODO)
* Service monitoring (TODO)
* Scheduling helpers

## Dependencies
Colugo has the following python dependencies:
* [pyzmq](https://github.com/zeromq/pyzmq)
* [Tornado](https://github.com/tornadoweb/tornado)
* [Zeroconf](https://github.com/jstasiak/python-zeroconf)
* [Protobuf](https://github.com/google/protobuf) (optional)

Colugo has the following system-level dependencies:
* [Bazel](https://github.com/bazelbuild/bazel)

## Installation

### OSX
First start with system dependencies for our build system
```shell
brew install bazel
pip3 install virtualenv
```

Then, clone the project and setup a virtual env to work within
```shell
git clone https://github.com/pickledgator/colugo
cd colugo
virtualenv env
source env/bin/activate
```

Then, kick off bazel to pull down dependencies and setup the toolchains
```shell
bazel build examples/...
```

### Linux
TODO

## Usage
Every Colugo application can implement or inherit from the Node class, which contains the tornado event loop and references to the service discovery threads. You may add any number of supported zmq sockets (see below for supported socket types) to each node and setup callback functions for sending/receiving messages over those sockets.

### Example Publisher
```python
from colugo.py.node import Node

class PublisherExample(Node):
    def __init__(self, name):
        Node.__init__(self, name)
        self.publisher = self.add_publisher("pub.topic")
        self.repeater = self.add_repeater(1000, self.callback)

    def callback(self):
        self.publisher.send("Message")

if __name__ == "__main__":

    pub_test_node = PublisherExample("PubExample")
    # this will block while there is work to be done by the ioloop
    pub_test_node.start()
```

### Example Subscriber
```python
from colugo.py.node import Node

class SubscriberExample(Node):
    def __init__(self, name):
        super(SubscriberExample, self).__init__(name)
        self.subscriber = self.add_subscriber("pub.topic", self.callback)

    def callback(self, message):
        self.logger.info("Received message: {}".format(message))

if __name__ == "__main__":

    sub_example_node = SubscriberExample("SubscriberExample")
    # this will block while there is work to be done by the ioloop
    sub_example_node.start()
```

### Example Request Client
```python
from colugo.py.node import Node

class RequestClientExample(Node):
    def __init__(self, name):
        Node.__init__(self, name)
        self.request_client = self.add_request_client("rpc.topic", self.connect_handler)
        self.counter = 0
        
    def connect_handler(self):
        self.request_sender()

    def request_sender(self):
        self.logger.info("Sending request: Message {}".format(self.counter))
        self.request_client.send("Message {}".format(self.counter), self.reply_callback, timeout_handler = self.request_timeout)
        self.counter += 1

    def request_timeout(self):
        self.logger.error("Request timed out")

    def reply_callback(self, message):
        self.logger.info("Got reply: {}".format(message))
        self.add_delayed_callback(1000, self.request_sender)

if __name__ == "__main__":

    req_example_node = RequestClientExample("RequestClient")
    req_example_node.start()
```

### Example Reply Server
```python
from colugo.py.node import Node

class ReplyServerExample(Node):
    def __init__(self, name):
        Node.__init__(self, name)
        self.reply_server = self.add_reply_server("rpc.topic", self.request_callback)

    def request_callback(self, message, reply):
        self.logger.info("Got request message: {}".format(message))
        reply(message)

if __name__ == "__main__":

    rep_example_node = ReplyServerExample("ReplyServer")
    rep_example_node.start()
```

Additional examples using json and protobuf serialiation are included in the examples folder.

## Future
* Investigate replacing Tornado with asyncio
* Add more unit tests
* Add integration tests
* Add authentification and security
* C++ implementation
* Go implementation
