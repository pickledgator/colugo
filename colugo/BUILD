load("@colugo_pip_deps//:requirements.bzl", "requirement")

py_library(
    name = "colugo_py",
    srcs = [
        "py/discovery.py",
        "py/node.py",
        "py/publisher.py",
        "py/repeater.py",
        "py/reply_server.py",
        "py/request_client.py",
        "py/zsocket.py",
        "py/subscriber.py",
    ],
    visibility = ["//visibility:public"],
    deps = [
        requirement("pyzmq"),
        requirement("tornado"),
        requirement("zeroconf"),
    ],
)
