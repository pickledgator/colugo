load("@colugo_pip_deps//:requirements.bzl", "requirement")

py_library(
    name = "colugo_py",
    srcs = [
        "py/directory.py",
        "py/discovery.py",
        "py/node.py",
        "py/publisher.py",
        "py/repeater.py",
        "py/reply_server.py",
        "py/request_client.py",
        "py/service.py",
        "py/subscriber.py",
        "py/zsocket.py",
    ],
    visibility = ["//visibility:public"],
    deps = [
        requirement("pyzmq"),
        requirement("tornado"),
        requirement("zeroconf"),
    ],
)

py_test(
    name='test_socket',
    srcs=[
        'py/test/test_socket.py',
    ],
    deps=[
        ':colugo_py',
    ],
    size = 'small',
)
