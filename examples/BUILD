load("@org_pubref_rules_protobuf//python:rules.bzl", "py_proto_library")

py_binary(
    name = "pub",
    srcs = ["py/pub.py"],
    default_python_version = "PY3",
    srcs_version = "PY3",
    deps = [
        "//colugo:colugo_py",
    ],
)

py_binary(
    name = "sub",
    srcs = ["py/sub.py"],
    default_python_version = "PY3",
    srcs_version = "PY3",
    deps = [
        "//colugo:colugo_py",
    ],
)

py_binary(
    name = "req",
    srcs = ["py/req.py"],
    default_python_version = "PY3",
    srcs_version = "PY3",
    deps = [
        "//colugo:colugo_py",
    ],
)

py_binary(
    name = "rep",
    srcs = ["py/rep.py"],
    default_python_version = "PY3",
    srcs_version = "PY3",
    deps = [
        "//colugo:colugo_py",
    ],
)

py_binary(
    name = "pub_proto",
    srcs = ["py/pub_proto.py"],
    default_python_version = "PY3",
    srcs_version = "PY3",
    deps = [
        "//colugo:colugo_py",
        "//examples/proto:py",
        "@com_google_protobuf//:protobuf_python",
    ],
)

py_binary(
    name = "sub_proto",
    srcs = ["py/sub_proto.py"],
    default_python_version = "PY3",
    srcs_version = "PY3",
    deps = [
        "//colugo:colugo_py",
        "//examples/proto:py",
        "@com_google_protobuf//:protobuf_python",
    ],
)

py_binary(
    name = "pub_json",
    srcs = ["py/pub_json.py"],
    default_python_version = "PY3",
    srcs_version = "PY3",
    deps = [
        "//colugo:colugo_py",
    ],
)

py_binary(
    name = "sub_json",
    srcs = ["py/sub_json.py"],
    default_python_version = "PY3",
    srcs_version = "PY3",
    deps = [
        "//colugo:colugo_py",
    ],
)