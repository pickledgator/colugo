package(default_visibility = ["//visibility:public"])

load("@org_pubref_rules_protobuf//python:rules.bzl", "py_proto_library")

filegroup(
    name = "protos",
    srcs = [
        "test.proto",
    ],
)

py_proto_library(
    name = "py",
    protos = [":protos"],
    verbose = 0,
    with_grpc = False,
)