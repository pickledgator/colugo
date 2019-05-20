load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@bazel_tools//tools/build_defs/repo:git.bzl", "git_repository")

# -----------------------------
# BAZEL PYTHON AND PIP

git_repository(
    name = "io_bazel_rules_python",
    remote = "https://github.com/bazelbuild/rules_python.git",
    commit = "fdbb17a4118a1728d19e638a5291b4c4266ea5b8", # May 14, 2019
)

load("@io_bazel_rules_python//python:pip.bzl", "pip_repositories")
pip_repositories()

load("@io_bazel_rules_python//python:pip.bzl", "pip_import")
pip_import(
   name = "colugo_pip_deps",
   requirements = "//:requirements.txt",
)

load("@colugo_pip_deps//:requirements.bzl", "pip_install")
pip_install()

# -----------------------------
# PROTOBUF

# Includes proto_library, cc_proto_library and py_proto_library skylark rules
http_archive(
    name = "com_google_protobuf",
    strip_prefix = "protobuf-3.8.0-rc1",
    urls = ["https://github.com/protocolbuffers/protobuf/archive/v3.8.0-rc1.tar.gz"], # May 1, 2019
    sha256 = "d399f651dbdc5f9116a2da199a808c815c0aeeb8d0b46e3213eee5a41263aeff",
)
load("@com_google_protobuf//:protobuf_deps.bzl", "protobuf_deps")
protobuf_deps()

http_archive(
    name = "six_package",
    build_file = "//third-party/six.BUILD",
    sha256 = "0ce7aef70d066b8dda6425c670d00c25579c3daad8108b3e3d41bef26003c852",
    url = "https://github.com/benjaminp/six/archive/1.12.0.tar.gz",
    strip_prefix = "six-1.12.0",
)

bind(
    name = "six",
    actual = "@six_package//:six",
)

# -----------------------------
# Skylark Tools
# Used internally by protobuf

http_archive(
    name = "bazel_skylib",
    strip_prefix = "bazel-skylib-0.8.0",
    urls = ["https://github.com/bazelbuild/bazel-skylib/archive/0.8.0.tar.gz"], # Mar 20, 2019
    sha256 = "2ea8a5ed2b448baf4a6855d3ce049c4c452a6470b1efd1504fdb7c1c134d220a",
)
# Verify we're using the right version of bazel
load("@bazel_skylib//lib:versions.bzl", "versions")
versions.check(minimum_bazel_version = "0.25.2")
