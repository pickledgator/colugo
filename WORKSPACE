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