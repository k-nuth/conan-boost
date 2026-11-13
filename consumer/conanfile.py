from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os


class Consumer(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["TEST_NATIVE"] = not self.dependencies["boost"].options.header_only
        tc.cache_variables["EXPECTED_BOOST_VERSION"] = sum(int(x) * scale for x, scale in zip(str(self.dependencies["boost"].ref.version).split("."), (100000, 100, 1)))
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            exe = "boost_consumer.exe" if self.settings.os == "Windows" else "boost_consumer"
            self.run(os.path.join(self.cpp.build.bindir, exe), env="conanrun")
