# #!/usr/bin/env python
# # -*- coding: utf-8 -*-

from conan.packager import ConanMultiPackager

if __name__ == "__main__":
    builder = ConanMultiPackager(username="bitprim", channel="stable", archs=["x86_64"])
    builder.add_common_builds(shared_option_name="boost:shared", pure_c=False)

    filtered_builds = []
    for settings, options, env_vars, build_requires in builder.builds:
        if (settings["build_type"] == "Release" or settings["build_type"] == "Debug") \
            and not options["boost:shared"] \
            and (not "compiler.libcxx" in settings or settings["compiler.libcxx"] == "libstdc++"):

            filtered_builds.append([settings, options, env_vars, build_requires])

    builder.builds = filtered_builds
    builder.run()
