# -----------------------------
# BAZEL PYTHON AND PIP

git_repository(
    name = "io_bazel_rules_python",
    remote = "https://github.com/bazelbuild/rules_python.git",
    commit = "115e3a0dab4291184fdcb0d4e564a0328364571a", # Feb 23, 2018
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

http_archive(
    name = "com_google_protobuf",
    sha256 = "826425182ee43990731217b917c5c3ea7190cfda141af4869e6d4ad9085a740f",
    strip_prefix = "protobuf-3.5.1",
    urls = ["https://github.com/google/protobuf/archive/v3.5.1.tar.gz"], # Dec 20, 2017
)

git_repository(
  name = "org_pubref_rules_protobuf",
  remote = "https://github.com/pubref/rules_protobuf",
  tag = "v0.8.1",
)

load("@org_pubref_rules_protobuf//cpp:rules.bzl", "cpp_proto_repositories")

cpp_proto_repositories(
    excludes = ["com_google_protobuf"],
)

load("@org_pubref_rules_protobuf//python:rules.bzl", "py_proto_repositories")

py_proto_repositories(
    omit_cpp_repositories = True,
    excludes = ["com_google_protobuf"],
)

# TODO(pickledgator): This is required for :protobuf_python for now but according to:
# https://github.com/google/protobuf/pull/4204
# its actually only used in :protobuf_src, so there's an open issue on bazel similarly related to fixing it: 
# https://github.com/bazelbuild/bazel/issues/1952

new_http_archive(
    name = "six_archive",
    build_file = "thirdparty/six.BUILD",
    sha256 = "105f8d68616f8248e24bf0e9372ef04d3cc10104f1980f54d57b2ce73a5ad56a",
    url = "https://pypi.python.org/packages/source/s/six/six-1.10.0.tar.gz#md5=34eed507548117b2ab523ab14b2f8b55",
)

bind(
    name = "six",
    actual = "@six_archive//:six",
)