load("@com_google_protobuf//:protobuf.bzl", "py_proto_library")

py_binary(
    name = "pub",
    srcs = ["py/pub.py"],
    deps = [
        "//colugo:colugo_py",
    ],
)

py_binary(
    name = "sub",
    srcs = ["py/sub.py"],
    deps = [
        "//colugo:colugo_py",
    ],
)

py_binary(
    name = "req",
    srcs = ["py/req.py"],
    deps = [
        "//colugo:colugo_py",
    ],
)

py_binary(
    name = "rep",
    srcs = ["py/rep.py"],
    deps = [
        "//colugo:colugo_py",
    ],
)

py_binary(
    name = "pub_proto",
    srcs = ["py/pub_proto.py"],
    deps = [
        "//colugo:colugo_py",
        "//examples/proto:py",
    ],
)

py_binary(
    name = "sub_proto",
    srcs = ["py/sub_proto.py"],
    deps = [
        "//colugo:colugo_py",
        "//examples/proto:py",
    ],
)

py_binary(
    name = "pub_json",
    srcs = ["py/pub_json.py"],
    deps = [
        "//colugo:colugo_py",
    ],
)

py_binary(
    name = "sub_json",
    srcs = ["py/sub_json.py"],
    deps = [
        "//colugo:colugo_py",
    ],
)
