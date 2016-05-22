from conan.packager import ConanMultiPackager


if __name__ == "__main__":
    builder = ConanMultiPackager(username="memsharded", channel="testing")
    builder.add_common_builds(shared_option_name="ZMQ:shared")
    builder.run()
