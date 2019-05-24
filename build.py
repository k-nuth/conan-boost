# #!/usr/bin/env python
# # -*- coding: utf-8 -*-

from conan.packager import ConanMultiPackager

if __name__ == "__main__":
    builder = ConanMultiPackager(username="kth", channel="stable", archs=["x86_64"]
                                 , remotes="https://api.bintray.com/conan/k-nuth/kth, https://api.bintray.com/conan/bitprim/bitprim")

    builder.add_common_builds(shared_option_name="boost:shared", pure_c=False)

    filtered_builds = []

    # for settings, options, env_vars, build_requires in builder.builds:
    for settings, options, env_vars, build_requires, reference in builder.items:
        if (settings["build_type"] == "Release" or settings["build_type"] == "Debug") \
            and not options["boost:shared"] \
            and (not "compiler.libcxx" in settings or settings["compiler.libcxx"] != "libstdc++11"):

            filtered_builds.append([settings, options, env_vars, build_requires])

    builder.builds = filtered_builds
    builder.run()
