#!/usr/bin/env python

import os
import sys
# local path to library
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import socket
from tornado.ioloop import IOLoop
import time
import unittest
from zeroconf import (
    ServiceBrowser,
    ServiceInfo,
    ServiceStateChange,
    Zeroconf,
)


class TestBonjour(unittest.TestCase):
    def test_register(self):
        zconf = Zeroconf()
        desc = {'path': '/~nic/'}
        info = ServiceInfo("_http._tcp.local.",
                           "test._http._tcp.local.",
                           socket.inet_aton("127.0.0.1"), 80, 0, 0,
                           desc, "ash-2.local.")
        zconf.register_service(info)
        get_info = zconf.get_service_info("_http._tcp.local.", "test._http._tcp.local.")
        self.assertEqual(info.name, get_info.name)
        self.assertEqual(info.address, get_info.address)
        self.assertEqual(info.port, get_info.port)
        zconf.unregister_service(info)
        zconf.close()

    def on_service_change(self, zeroconf, service_type, state_change, name):
        print("service_type: {}, name: {}, state_change: {}".format(service_type, name, state_change))
        if state_change == ServiceStateChange.Added:
            self.assertEqual(name, "test._http._tcp.local.")
            self.assertEqual(state_change, ServiceStateChange.Added)
        else:
            self.assertEqual(name, "test._http._tcp.local.")
            self.assertEqual(state_change, ServiceStateChange.Removed)
            zeroconf.close()

    def test_browser(self):
        zconf = Zeroconf()
        browser = ServiceBrowser(zconf, "_http._tcp.local.", handlers=[self.on_service_change])
        info = ServiceInfo("_http._tcp.local.",
                           "test._http._tcp.local.",
                           socket.inet_aton("127.0.0.1"), 80, 0, 0,
                           {'path': '/~nic/'}, "ash-2.local.")
        zconf.register_service(info)
        zconf.unregister_service(info)

if __name__ == '__main__':
    unittest.main()


#!/usr/bin/env python3

""" Example of announcing a service (in this case, a fake HTTP server) """

# import logging
# import socket
# import sys
# from time import sleep

# from zeroconf import ServiceInfo, Zeroconf

# if __name__ == '__main__':
#     logging.basicConfig(level=logging.DEBUG)
#     if len(sys.argv) > 1:
#         assert sys.argv[1:] == ['--debug']
#         logging.getLogger('zeroconf').setLevel(logging.DEBUG)

#     desc = {'path': '/~paulsm/'}

#     info = ServiceInfo("_http._tcp.local.",
#                        "Paul's Test Web Site._http._tcp.local.",
#                        socket.inet_aton("127.0.0.1"), 80, 0, 0,
#                        desc, "ash-2.local.")

#     zeroconf = Zeroconf()
#     print("Registration of a service, press Ctrl-C to exit...")
#     zeroconf.register_service(info)
#     try:
#         while True:
#             sleep(0.1)
#     except KeyboardInterrupt:
#         pass
#     finally:
#         print("Unregistering...")
#         zeroconf.unregister_service(info)
#         zeroconf.close()
