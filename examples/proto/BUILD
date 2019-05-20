package(default_visibility = ["//visibility:public"])

load("@com_google_protobuf//:protobuf.bzl", "py_proto_library")

py_proto_library(
    name = "py",
    srcs = glob(["*.proto"]),
    deps = [
        "@com_google_protobuf//:protobuf_python"
    ],
)
