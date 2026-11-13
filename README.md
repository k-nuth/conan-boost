# Boost Conan recipe

Knuth-maintained Boost packaging, based on Conan Center Index.

The pristine imported recipe is kept in `upstream/boost`; the working recipe is
in `recipes/boost`. `upstream.json` identifies the exact source revision.
Conan package name, options and CMake component names retain upstream compatibility.

The initial import supports the same versions as CCI. Boost 1.92 support, focused
profiles, tests, CI and upstream comparison tools are prepared separately.

Recipe code retains the upstream MIT license. Boost itself is distributed under
the Boost Software License, carried by the downloaded source and Conan package.
