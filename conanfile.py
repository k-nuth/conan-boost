#
# Copyright (c) 2016-2020 Knuth Project.
#
# This file is part of Knuth Project.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

#TODO(fernando): Remove Boost.Test, use doctest or catch2 instead.

import os
import sys
from conans import ConanFile, tools
from kthbuild import KnuthConanFile


# From from *1 (see below, b2 --show-libraries), also ordered following linkage order
# see https://github.com/Kitware/CMake/blob/master/Modules/FindBoost.cmake to know the order

lib_list = ['math', 'wave', 'container', 'exception', 'graph', 'headers', 'iostreams', 'locale', 'log',
            'program_options', 'random', 'regex', 'mpi', 'serialization', 
            'coroutine', 'fiber', 'context', 'contract', 'timer', 'thread', 'chrono', 'date_time',
            'atomic', 'filesystem', 'system', 'graph_parallel', 'python',
            'stacktrace', 'test', 'type_erasure']

# class KnuthConanBoost(KnuthCxx11ABIFixer):
class KnuthConanBoost(KnuthConanFile):
    def recipe_dir(self):
        return os.path.dirname(os.path.abspath(__file__))

    name = "boost"
    version = "1.72.0"

    settings = "os", "arch", "compiler", "build_type"
    folder_name = "boost_%s" % version.replace(".", "_")
    description = "Boost provides free peer-reviewed portable C++ source libraries"

    # The current python option requires the package to be built locally, to find default Python
    # implementation
    options = {
        "shared": [True, False],
        "header_only": [True, False],
        "fPIC": [True, False],
        "use_bzip2": [True, False],
        "use_icu": [True, False],
        "use_zlib": [True, False],
        "cppstd": ['98', '11', '14', '17', '20'],
        "verbose": [True, False],
        "microarchitecture": "ANY",
        "fix_march": [True, False],
        "march_id": "ANY",
        "cxxflags": "ANY",
        "cflags": "ANY",
        "glibcxx_supports_cxx11_abi": "ANY",
    }

    options.update({"without_%s" % libname: [True, False] for libname in lib_list})

    # default_options = ["shared=False", "header_only=False", "fPIC=True"]
    # default_options.extend(["without_%s=False" % libname for libname in lib_list if libname != "python"])
    # default_options.append("without_python=True")
    # default_options = tuple(default_options)

    default_options = tuple(["shared=False", "header_only=False", "fPIC=True",

        "use_bzip2=False", "use_icu=True", "use_zlib=False", 
        "cppstd=17",
        "verbose=False",
        "microarchitecture=_DUMMY_",
        "fix_march=False",
        "march_id=_DUMMY_",
        "cxxflags=_DUMMY_",
        "cflags=_DUMMY_",
        "glibcxx_supports_cxx11_abi=_DUMMY_",

        "without_python=True", 
        "without_atomic=True", 
        "without_chrono=True", 
        "without_container=True", 
        "without_context=True", 
        "without_contract=True", 
        "without_coroutine=True", 
        "without_date_time=False", 
        "without_exception=True", 
        "without_fiber=True", 
        "without_filesystem=False", 
        "without_graph=True", 
        "without_graph_parallel=True", 
        "without_headers=True", 
        "without_iostreams=False", 
        "without_locale=False", 
        "without_log=False", 
        "without_math=True", 
        "without_mpi=True", 
        "without_program_options=False", 
        "without_random=True", 
        "without_regex=True", 
        "without_serialization=True", 
        "without_stacktrace=True", 
        "without_system=False", 
        "without_test=False", 
        "without_thread=True", 
        "without_timer=True", 
        "without_type_erasure=True", 
        "without_wave=True"])

    url = "https://github.com/k-nuth/conan-boost"
    license = "Boost Software License - Version 1.0. http://www.boost.org/LICENSE_1_0.txt"
    short_paths = True
    no_copy_source = False

    #exports_sources = "src/*"
    #exports = ["FindBoost.cmake", "OriginalFindBoost*"]
    exports = "conan_*", "ci_utils/*"
    build_policy = "missing" # "always"

    libs_by_option = {
        "atomic": ["atomic"],
        "chrono": ["chrono"],
        "container": ["container"],
        "context": ["context"],
        "coroutine": ["coroutine"],
        "date_time": ["date_time"],
        "exception": ["exception"],
        "fiber": ["fiber"],
        "filesystem": ["filesystem"],
        "graph": ["graph"],
        "graph_parallel": ["graph_parallel"],
        "headers": ["headers"],
        "iostreams": ["iostreams"],
        "locale": ["locale"],
        "log": ["log", "log_setup"],
        "math": ["math_c99", "math_c99f", "math_c99l", "math_tr1", "math_tr1f", "math_tr1l"],
        "mpi": ["mpi"],
        "program_options": ["program_options"],
        "random": ["random"],
        "regex": ["regex"],
        "serialization": ["serialization", "wserialization"],
        "stacktrace": ["stacktrace"],
        "system": ["system"],
        "test": ["unit_test_framework", "prg_exec_monitor", "test_exec_monitor"],
        "thread": ["thread"],
        "timer": ["timer"],
        "type_erasure": ["type_erasure"],
        "wave": ["wave"]
    }


    @property
    def use_zip_bzip2(self):
        return not self.options.without_iostreams and not self.options.header_only

    @property
    def use_icu(self):
        return not self.options.header_only and (not self.options.without_regex or not self.options.without_locale)

    @property
    def msvc_mt_build(self):
        return "MT" in str(self.settings.compiler.runtime)

    @property
    def fPIC_enabled(self):
        if self.settings.compiler == "Visual Studio":
            return False
        else:
            return self.options.fPIC

    @property
    def is_shared(self):
        if self.settings.compiler == "Visual Studio" and self.msvc_mt_build:
            return False
        else:
            return self.options.shared

    def requirements(self):
        # self.output.info('def requirements(self):')
        
        if self.options.use_bzip2 and self.use_zip_bzip2:
            self.requires("bzip2/1.0.6@bitprim/stable")
            self.options["bzip2"].shared = self.is_shared #False
            #TODO(fernando): what about fPIC?
            
        if self.options.use_zlib and self.use_zip_bzip2:
            self.requires("zlib/1.2.11@bitprim/stable")
            self.options["zlib"].shared = self.is_shared #False
            #TODO(fernando): what about fPIC?

        if self.options.use_icu and self.use_icu:
            self.requires("icu/64.2@kth/stable")
            self.options["icu"].shared = self.is_shared #False
            #TODO(fernando): what about fPIC?

            # self.requires("libiconv/1.15@bitprim/stable")
            # self.options["libiconv"].shared = self.is_shared #False

    def config_options(self):
        KnuthConanFile.config_options(self)

    def configure(self):
        KnuthConanFile.configure(self)

    # def package_id(self):
    #     if self.options.header_only:
    #         self.info.requires.clear()
    #         self.info.settings.clear()

    def package_id(self):
        KnuthConanFile.package_id(self)
        # self.output.info('def package_id(self):')
        if self.options.header_only:
            self.info.header_only()
        # else:
        #     #For Knuth Packages libstdc++ and libstdc++11 are the same
        #     if self.settings.compiler == "gcc" or self.settings.compiler == "clang":
        #         if str(self.settings.compiler.libcxx) == "libstdc++" or str(self.settings.compiler.libcxx) == "libstdc++11":
        #             self.info.settings.compiler.libcxx = "ANY"

    def source(self):
        # self.output.info('def source(self):')
        zip_name = "%s.zip" % self.folder_name if sys.platform == "win32" else "%s.tar.gz" % self.folder_name
        #url = "http://sourceforge.net/projects/boost/files/boost/%s/%s/download" % (self.version, zip_name)
        url = "https://dl.bintray.com/boostorg/release/%s/source/%s" % (self.version, zip_name)
        self.output.info("Downloading %s..." % url)
        tools.download(url, zip_name)

        tools.unzip(zip_name)
        os.unlink(zip_name)

    ##################### BUILDING METHODS ###########################

    def build(self):
        # self.output.info('def build(self):')
        if self.options.header_only:
            self.output.warn("Header only package, skipping build")
            return


        if self.options.use_icu and self.use_icu:
            boost_build_folder = os.path.join(self.build_folder, self.folder_name)

            self.output.info(self.build_folder)
            self.output.info(boost_build_folder)

            replace_str = "int main() { return 0; }"
            # REGEX_TEST="libs/regex/build/has_icu_test.cpp"
            # LOCALE_TEST="libs/locale/build/has_icu_test.cpp"
            regex_test = os.path.join(boost_build_folder, 'libs', 'regex', 'build', 'has_icu_test.cpp')
            locale_test = os.path.join(boost_build_folder, 'libs', 'locale', 'build', 'has_icu_test.cpp')

            self.output.info(regex_test)
            self.output.info(locale_test)


            # with open(regex_test, 'r') as fin:
            #     print(fin.read())

            # with open(locale_test, 'r') as fin:
            #     print(fin.read())

            with open(regex_test, "w") as f:
                f.write(replace_str)

            with open(locale_test, "w") as f:
                f.write(replace_str)

            # with open(regex_test, 'r') as fin:
            #     print(fin.read())

            # with open(locale_test, 'r') as fin:
            #     print(fin.read())


        b2_exe = self.bootstrap()
        flags = self.get_build_flags()
        # Help locating bzip2 and zlib
        # self.create_user_config_jam(self.build_folder)

        # JOIN ALL FLAGS
        b2_flags = " ".join(flags)

        # command = "b2" if self.settings.os == "Windows" else "./b2"

        # full_command = "cd %s && %s %s -j%s" % (
        #     self.FOLDER_NAME,
        #     command,
        #     b2_flags,
        #     tools.cpu_count())
        # self.output.warn(full_command)

        # envs = self.prepare_deps_options_env()
        # with tools.environment_append(envs):
        #     self.run(full_command)#, output=False)


        full_command = "%s %s -j%s --abbreviate-paths -d2" % (b2_exe, b2_flags, tools.cpu_count())
        # -d2 is to print more debug info and avoid travis timing out without output
        sources = os.path.join(self.source_folder, self.folder_name)
        full_command += ' --debug-configuration --build-dir="%s"' % self.build_folder
        self.output.warn(full_command)

        with tools.vcvars(self.settings) if self.settings.compiler == "Visual Studio" else tools.no_op():
            with tools.chdir(sources):
                # to locate user config jam (BOOST_BUILD_PATH)
                with tools.environment_append({"BOOST_BUILD_PATH": self.build_folder}):
                    # To show the libraries *1
                    # self.run("%s --show-libraries" % b2_exe)
                    self.run(full_command)

    def get_build_flags(self):
        # flags = []

        if tools.cross_building(self.settings):
            flags = self.get_build_cross_flags()
        else:
            flags = []

            if self.settings.compiler == "Visual Studio":
                flags.append("toolset=msvc-%s" % self._msvc_version())
            elif self.settings.compiler == "gcc":
                # For GCC we only need the major version otherwhise Boost doesn't find the compiler
                #flags.append("toolset=%s-%s"% (self.settings.compiler, self._gcc_short_version(self.settings.compiler.version)))
                flags.append("toolset=gcc")
            elif str(self.settings.compiler) in ["clang"]:
                flags.append("toolset=%s-%s"% (self.settings.compiler, self.settings.compiler.version))

            if self.settings.arch == 'x86' and 'address-model=32' not in flags:
                flags.append('address-model=32')
            elif self.settings.arch == 'x86_64' and 'address-model=64' not in flags:
                flags.append('address-model=64')


        if self.settings.compiler == "gcc":
            flags.append("--layout=system")

        if self.settings.compiler == "Visual Studio" and self.settings.compiler.runtime:
            flags.append("runtime-link=%s" % ("static" if self.msvc_mt_build else "shared"))

        # if self.settings.os == "Windows" and self.settings.compiler == "gcc":
        #     flags.append("threading=multi")
        flags.append("threading=multi")
        flags.append("link=%s" % ("static" if not self.is_shared else "shared"))
        flags.append("variant=%s" % str(self.settings.build_type).lower())
        flags.append("--reconfigure")

        if self.options.use_icu and self.use_icu and not self.options.without_locale:
            flags.append("boost.locale.iconv=off")
            flags.append("boost.locale.posix=off")



    # #   # Just from icu
    #     print("--------- FROM icu -------------")
    # #   print(self.deps_cpp_info["icu"].include_paths)
    # #   print(self.deps_cpp_info["icu"].lib_paths)
    # #   print(self.deps_cpp_info["icu"].bin_paths)
    #     print(self.deps_cpp_info["icu"].libs)
    # #   print(self.deps_cpp_info["icu"].defines)
    # #   print(self.deps_cpp_info["icu"].cflags)
    # #   print(self.deps_cpp_info["icu"].cppflags)
    # #   print(self.deps_cpp_info["icu"].sharedlinkflags)
    # #   print(self.deps_cpp_info["icu"].exelinkflags)

        # if self.use_icu:
        if self.options.use_icu and self.use_icu:
            flags.append("-sICU_PATH=%s" % (self._get_icu_path(),))
            # flags.append("-sICU_LINK=${ICU_LIBS[@]}")


        if self.options.use_bzip2 and self.use_zip_bzip2:
            flags.append("-sBZIP2_LIBPATH=%s" % (self.deps_cpp_info["bzip2"].lib_paths[0].replace('\\', '/'),))
            flags.append("-sBZIP2_INCLUDE=%s" % (self.deps_cpp_info["bzip2"].include_paths[0].replace('\\', '/'),))
        else:
            flags.append("-sNO_BZIP2=1")

        if self.options.use_zlib and self.use_zip_bzip2:
            flags.append("-sZLIB_LIBPATH=%s" % (self.deps_cpp_info["zlib"].lib_paths[0].replace('\\', '/'),))
            flags.append("-sZLIB_INCLUDE=%s" % (self.deps_cpp_info["zlib"].include_paths[0].replace('\\', '/'),))
        else:
            flags.append("-sNO_ZLIB=1")
        
        #TODO(fernando): Add support for LZMA/xz 
        flags.append("-sNO_LZMA=1")

        
        
        if self.options.cppstd == '98':
            flags.append("cxxstd=98")
        elif self.options.cppstd == '11':
            flags.append("cxxstd=11")
        elif self.options.cppstd == '14':
            flags.append("cxxstd=14")
        elif self.options.cppstd == '17':
            flags.append("cxxstd=17")
        elif self.options.cppstd == '20':
            flags.append("cxxstd=20")
        

        # option_names = {
        #     "--without-atomic": self.options.without_atomic,
        #     "--without-chrono": self.options.without_chrono,
        #     "--without-container": self.options.without_container,
        #     "--without-context": self.options.without_context,
        #     "--without-coroutine": self.options.without_coroutine,
        #     "--without-date_time": self.options.without_date_time,
        #     "--without-exception": self.options.without_exception,
        #     "--without-fiber": self.options.without_fiber,
        #     "--without-filesystem": self.options.without_filesystem,
        #     "--without-graph": self.options.without_graph,
        #     "--without-graph_parallel": self.options.without_graph_parallel,
        #     "--without-iostreams": self.options.without_iostreams,
        #     "--without-locale": self.options.without_locale,
        #     "--without-log": self.options.without_log,
        #     "--without-math": self.options.without_math,
        #     "--without-mpi": self.options.without_mpi,
        #     "--without-program_options": self.options.without_program_options,
        #     "--without-random": self.options.without_random,
        #     "--without-regex": self.options.without_regex,
        #     "--without-serialization": self.options.without_serialization,
        #     "--without-stacktrace": self.options.without_stacktrace,
        #     "--without-system": self.options.without_system,
        #     "--without-test": self.options.without_test,
        #     "--without-thread": self.options.without_thread,
        #     "--without-timer": self.options.without_timer,
        #     "--without-type_erasure": self.options.without_type_erasure,
        #     "--without-wave": self.options.without_wave
        # }
        # for option_name, activated in option_names.items():
        #     if activated:
        #         flags.append(option_name)

        for libname in lib_list:
            if getattr(self.options, "without_%s" % libname):
                flags.append("--without-%s" % libname)

        # CXX FLAGS
        cxx_flags = []
        # fPIC DEFINITION
        if self.fPIC_enabled:
            cxx_flags.append("-fPIC")

        # try:
        #     if self.settings.compiler in [ "gcc", "clang" ]:
        #         cxx_flags.append("-std=c++11")  # always C++11 (at minimum)

        #     if self.settings.compiler != "Visual Studio":
        #         cxx_flags.append("-Wno-deprecated-declarations")

        #     if self.settings.compiler == "gcc":
        #         if float(self.settings.compiler.version) >= 5:
        #             flags.append("define=_GLIBCXX_USE_CXX11_ABI=1")
        #         else:
        #             flags.append("define=_GLIBCXX_USE_CXX11_ABI=0")

        #     if "clang" in str(self.settings.compiler):
        #         if str(self.settings.compiler.libcxx) == "libc++":
        #             cxx_flags.append("-stdlib=libc++")
        #             cxx_flags.append("-std=c++11")
        #             flags.append('linkflags="-stdlib=libc++"')
        #         else:
        #             cxx_flags.append("-stdlib=libstdc++")
        #             cxx_flags.append("-std=c++11")
        # except BaseException as e:
        #     self.output.warn(str(e))


        if self.settings.compiler == "Visual Studio":
            cxx_flags.append("/DBOOST_CONFIG_SUPPRESS_OUTDATED_MESSAGE")

            # Related with:
            # https://github.com/boostorg/iostreams/issues/60
            # https://github.com/boostorg/iostreams/pull/57/files
            # Not fixed in Boost Iostreams 1.68.0
            #   Maybe fixed in 1.69.0
            # cxx_flags.append("/D_SILENCE_FPOS_SEEKPOS_DEPRECATION_WARNING")
            

        # Standalone toolchain fails when declare the std lib
        if self.settings.os != "Android":
            try:
                # if self.settings.compiler in [ "gcc", "clang", "apple-clang" ]:
                #     cxx_flags.append("-std=c++11")  # always C++11 (at minimum)

                if self.settings.compiler != "Visual Studio":
                    cxx_flags.append("-Wno-deprecated-declarations")

                # if self.settings.compiler == "gcc":
                #     if float(self.settings.compiler.version) >= 5:
                #         flags.append("define=_GLIBCXX_USE_CXX11_ABI=1")
                #     else:
                #         flags.append("define=_GLIBCXX_USE_CXX11_ABI=0")

                # if self.settings.compiler == "gcc":
                #     if str(self.settings.compiler.libcxx) == "libstdc++":
                #         flags.append("define=_GLIBCXX_USE_CXX11_ABI=0")
                #     elif str(self.settings.compiler.libcxx) == "libstdc++11":
                #         flags.append("define=_GLIBCXX_USE_CXX11_ABI=1")


                if self.settings.compiler == "gcc":
                    if float(str(self.settings.compiler.version)) >= 5:
                        flags.append("define=_GLIBCXX_USE_CXX11_ABI=1")
                    else:
                        flags.append("define=_GLIBCXX_USE_CXX11_ABI=0")
                elif self.settings.compiler == "clang":
                    if str(self.settings.compiler.libcxx) == "libstdc++" or str(self.settings.compiler.libcxx) == "libstdc++11":
                        flags.append("define=_GLIBCXX_USE_CXX11_ABI=1")

                if "clang" in str(self.settings.compiler):
                    if str(self.settings.compiler.libcxx) == "libc++":
                        cxx_flags.append("-stdlib=libc++")
                        flags.append('linkflags="-stdlib=libc++"')
                    else:
                        cxx_flags.append("-stdlib=libstdc++")
            except:
                pass
            # except BaseException as e:
            #     self.output.warn(str(e))


        # cxx_flags = 'cxxflags="%s"' % " ".join(cxx_flags) if cxx_flags else ""
        # flags.append(cxx_flags)
        # flags.append("--without-python")


        if self.options.verbose:
            flags.append("-d 2") #Verbosity (from 1 to 13)

        cxx_flags = 'cxxflags="%s"' % " ".join(cxx_flags) if cxx_flags else ""
        flags.append(cxx_flags)

        return flags

    def get_build_cross_flags(self):
        arch = self.settings.get_safe('arch')
        flags = []
        self.output.info("Cross building, detecting compiler...")
        flags.append('architecture=%s' % ('arm' if arch.startswith('arm') else arch))
        bits = {"x86_64": "64", "armv8": "64"}.get(str(self.settings.arch), "32")
        flags.append('address-model=%s' % bits)
        if self.settings.get_safe('os').lower() in ('linux', 'android'):
            flags.append('binary-format=elf')

        if arch.startswith('arm'):
            if 'hf' in arch:
                flags.append('-mfloat-abi=hard')
            flags.append('abi=aapcs')
        elif arch in ["x86", "x86_64"]:
            pass
        else:
            raise Exception("I'm so sorry! I don't know the appropriate ABI for "
                            "your architecture. :'(")

        self.output.info("Cross building flags: %s" % flags)
        # "android" "appletv" "bsd" "cygwin" "darwin" "freebsd" "haiku" "hpux" "iphone" "linux"
        # "netbsd" "openbsd" "osf" "qnx" "qnxnto" "sgi" "solaris" "unix" "unixware" "windows" "vms" "vxworks" "elf"

        target = {"Windows": "windows",
                  "Macos": "darwin",
                  "Linux": "linux",
                  "Android": "android",
                  "iOS": "iphone",
                  "watchOS": "iphone",
                  "tvOS": "appletv",
                  "freeBSD": "freebsd"}.get(str(self.settings.os), None)

        if not target:
            raise Exception("Unknown target for %s" % self.settings.os)

        flags.append("target-os=%s" % target)
        return flags

    def create_user_config_jam(self, folder):
        """To help locating the zlib and bzip2 deps"""
        self.output.warn("Patching user-config.jam")

        compiler_command = os.environ.get('CXX', None)

        contents = ""
        # if self.use_zip_bzip2:
        #     contents = "\nusing zlib : 1.2.11 : <include>%s <search>%s ;" % (
        #         self.deps_cpp_info["zlib"].include_paths[0].replace('\\', '/'),
        #         self.deps_cpp_info["zlib"].lib_paths[0].replace('\\', '/'))

        #     # if self.settings.os == "Linux" or self.settings.os == "Macos":
        #     #     contents += "\nusing bzip2 : 1.0.6 : <include>%s <search>%s ;" % (
        #     #         self.deps_cpp_info["bzip2"].include_paths[0].replace('\\', '/'),
        #     #         self.deps_cpp_info["bzip2"].lib_paths[0].replace('\\', '/'))

        #     contents += "\nusing bzip2 : 1.0.6 : <include>%s <search>%s ;" % (
        #         self.deps_cpp_info["bzip2"].include_paths[0].replace('\\', '/'),
        #         self.deps_cpp_info["bzip2"].lib_paths[0].replace('\\', '/'))

        # if self.use_icu:
        #     contents += "\nusing icu : 60.2 : <include>%s <search>%s ;" % (
        #         self.deps_cpp_info["icu"].include_paths[0].replace('\\', '/'),
        #         self.deps_cpp_info["icu"].lib_paths[0].replace('\\', '/'))

        toolset, version, exe = self.get_toolset_version_and_exe()
        exe = compiler_command or exe  # Prioritize CXX
        # Specify here the toolset with the binary if present if don't empty parameter : :
        contents += '\nusing "%s" : "%s" : ' % (toolset, version)
        contents += ' "%s"' % exe.replace("\\", "/")

        contents += " : \n"
        if "AR" in os.environ:
            contents += '<archiver>"%s" ' % tools.which(os.environ["AR"]).replace("\\", "/")
        if "RANLIB" in os.environ:
            contents += '<ranlib>"%s" ' % tools.which(os.environ["RANLIB"]).replace("\\", "/")
        if "CXXFLAGS" in os.environ:
            contents += '<cxxflags>"%s" ' % os.environ["CXXFLAGS"]
        if "CFLAGS" in os.environ:
            contents += '<cflags>"%s" ' % os.environ["CFLAGS"]
        if "LDFLAGS" in os.environ:
            contents += '<ldflags>"%s" ' % os.environ["LDFLAGS"]
        contents += " ;"

        self.output.warn(contents)
        filename = "%s/user-config.jam" % folder
        tools.save(filename,  contents)

    def get_toolset_version_and_exe(self):
        compiler_version = str(self.settings.compiler.version)
        compiler = str(self.settings.compiler)
        if self.settings.compiler == "Visual Studio":
            # cversion = self.settings.compiler.version
            # _msvc_version = "14.1" if cversion == "15" else "%s.0" % cversion
            return "msvc", self._msvc_version(), ""
        elif not self.settings.os == "Windows" and compiler == "gcc" and compiler_version[0] >= "5":
            # For GCC >= v5 we only need the major otherwise Boost doesn't find the compiler
            # The NOT windows check is necessary to exclude MinGW:
            if not tools.which("g++-%s" % compiler_version[0]):
                # In fedora 24, 25 the gcc is 6, but there is no g++-6 and the detection is 6.3.1
                # so b2 fails because 6 != 6.3.1. Specify the exe to avoid the smart detection
                executable = "g++"
            else:
                executable = ""
            return compiler, compiler_version[0], executable
        elif str(self.settings.compiler) in ["clang", "gcc"]:
            # For GCC < v5 and Clang we need to provide the entire version string
            return compiler, compiler_version, ""
        elif self.settings.compiler == "apple-clang":
            return "clang", compiler_version, ""
        elif self.settings.compiler == "sun-cc":
            return "sunpro", compiler_version, ""
        else:
            return compiler, compiler_version, ""

    ##################### BOOSTRAP METHODS ###########################

        # toolset = "darwin" if self.settings.os == "Macos" else self.settings.compiler
        
        # # command = "bootstrap" if self.settings.os == "Windows" else "./bootstrap.sh --with-toolset=%s" % self.settings.compiler
        # command = ""
        # if self.settings.os == "Windows":
        #     if self.settings.compiler == "gcc":
        #         command = "bootstrap gcc"
        #     else:
        #         command = "bootstrap"
        # else:
        #     command = "./bootstrap.sh --with-toolset=%s" % toolset
        
        # try:
        #     self.run("cd %s && %s" % (self.FOLDER_NAME, command))

        #     self.run("cd %s && type bootstrap.log" % self.FOLDER_NAME
        #             if self.settings.os == "Windows"
        #             else "cd %s && cat bootstrap.log" % self.FOLDER_NAME)

        # except:
        #     self.run("cd %s && type bootstrap.log" % self.FOLDER_NAME
        #             if self.settings.os == "Windows"
        #             else "cd %s && cat bootstrap.log" % self.FOLDER_NAME)
        #     raise



    # circumvent_boost_icu_detection()
    # {
    #     # Boost expects a directory structure for ICU which is incorrect.
    #     # Boost ICU discovery fails when using prefix, can't fix with -sICU_LINK,
    #     # so we rewrite the two 'has_icu_test.cpp' files to always return success.

    #     local SUCCESS="int main() { return 0; }"
    #     local REGEX_TEST="libs/regex/build/has_icu_test.cpp"
    #     local LOCALE_TEST="libs/locale/build/has_icu_test.cpp"

    #     echo $SUCCESS > $REGEX_TEST
    #     echo $SUCCESS > $LOCALE_TEST

    #     # echo "Hack: ICU detection modified, will always indicate found."
    # }


    def _get_icu_path(self):
        return os.path.normpath(self.deps_cpp_info["icu"].lib_paths[0] + os.sep + os.pardir)
        

    def _get_boostrap_toolset(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            # comp_ver = self.settings.compiler.version
            # return "vc%s" % ("141" if comp_ver == "15" else comp_ver)
            return self._msvc_version_boostrap()

        with_toolset = {"apple-clang": "darwin"}.get(str(self.settings.compiler),
                                                     str(self.settings.compiler))
        return with_toolset

    def bootstrap(self):
        # folder = os.path.join(self.source_folder, self.folder_name, "tools", "build")
        folder = os.path.join(self.source_folder, self.folder_name)

        if self.options.use_icu and self.use_icu and self.settings.os != "Windows":
            self.output.info('icu_path: %s' % (self._get_icu_path(),))
            with_icu_str = '--with-icu=%s' % (self._get_icu_path(),)
        else:
            with_icu_str = ''

        try:
            bootstrap = "bootstrap.bat" if tools.os_info.is_windows else "./bootstrap.sh"
            with tools.vcvars(self.settings) if self.settings.compiler == "Visual Studio" else tools.no_op():
                self.output.info("Using %s %s" % (self.settings.compiler, self.settings.compiler.version))
                with tools.chdir(folder):

                    # ./bootstrap.sh \
                    #     "--prefix=$PREFIX" \
                    #     "--with-icu=$ICU_PREFIX"

                    # self.output.info('self._get_boostrap_toolset(): %s' % (self._get_boostrap_toolset(),))


                    cmd = "%s %s %s" % (bootstrap, self._get_boostrap_toolset(), with_icu_str)

                    self.output.info(cmd)
                    self.run(cmd)
        except Exception as exc:
            self.output.warn(str(exc))
            if os.path.join(folder, "bootstrap.log"):
                self.output.warn(tools.load(os.path.join(folder, "bootstrap.log")))
            raise
        return os.path.join(folder, "b2.exe") if tools.os_info.is_windows else os.path.join(folder, "b2")

    ####################################################################

    def package(self):
        # # Copy findZLIB.cmake to package
        # self.copy("FindBoost.cmake", ".", ".")
        # self.copy("OriginalFindBoost*", ".", ".")

        # self.copy(pattern="*", dst="include/boost", src="%s/boost" % self.FOLDER_NAME)
        # self.copy(pattern="*.a", dst="lib", src="%s/stage/lib" % self.FOLDER_NAME)
        # self.copy(pattern="*.so", dst="lib", src="%s/stage/lib" % self.FOLDER_NAME)
        # self.copy(pattern="*.so.*", dst="lib", src="%s/stage/lib" % self.FOLDER_NAME)
        # self.copy(pattern="*.dylib*", dst="lib", src="%s/stage/lib" % self.FOLDER_NAME)
        # self.copy(pattern="*.lib", dst="lib", src="%s/stage/lib" % self.FOLDER_NAME)
        # self.copy(pattern="*.dll", dst="bin", src="%s/stage/lib" % self.FOLDER_NAME)


        # This stage/lib is in source_folder... Face palm, looks like it builds in build but then
        # copy to source with the good lib name
        out_lib_dir = os.path.join(self.folder_name, "stage", "lib")
        self.copy(pattern="*", dst="include/boost", src="%s/boost" % self.folder_name)
        if not self.is_shared:
            self.copy(pattern="*.a", dst="lib", src=out_lib_dir, keep_path=False)
        self.copy(pattern="*.so", dst="lib", src=out_lib_dir, keep_path=False, symlinks=True)
        self.copy(pattern="*.so.*", dst="lib", src=out_lib_dir, keep_path=False, symlinks=True)
        self.copy(pattern="*.dylib*", dst="lib", src=out_lib_dir, keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src=out_lib_dir, keep_path=False)
        self.copy(pattern="*.dll", dst="bin", src=out_lib_dir, keep_path=False)

        # When first call with source do not package anything
        if not os.path.exists(os.path.join(self.package_folder, "lib")):
            return

        self.renames_to_make_cmake_find_package_happy()

    def renames_to_make_cmake_find_package_happy(self):
        # CMake findPackage help
        renames = []
        for libname in os.listdir(os.path.join(self.package_folder, "lib")):
            new_name = libname
            libpath = os.path.join(self.package_folder, "lib", libname)
            if self.settings.compiler == "Visual Studio":
                if new_name.startswith("lib"):
                    if os.path.isfile(libpath):
                        new_name = libname[3:]
                if "-s-" in libname:
                    new_name = new_name.replace("-s-", "-")
                elif "-sgd-" in libname:
                    new_name = new_name.replace("-sgd-", "-gd-")

            for arch in ["x", "a", "i", "s", "m", "p"]:  # Architectures
                for addr in ["32", "64"]:  # Model address
                    new_name = new_name.replace("-%s%s-" % (arch, addr), "-")

            renames.append([libpath, os.path.join(self.package_folder, "lib", new_name)])

        for original, new in renames:
            if original != new and not os.path.exists(new):
                self.output.info("Rename: %s => %s" % (original, new))
                os.rename(original, new)

    # def package_info(self):

    #     if not self.options.header_only and self.is_shared:
    #         self.cpp_info.defines.append("BOOST_ALL_DYN_LINK")
    #     else:
    #         self.cpp_info.defines.append("BOOST_USE_STATIC_LIBS")

    #     if self.options.header_only:
    #         return

    #     #Select binaries to package looking at the options
    #     libs = []
    #     for option, option_value in self.options.items():
    #         if option.startswith("without_") and option_value == "False":
    #             libs.extend(self.libs_by_option[option.replace("without_", "")])

        



    #     # if self.settings.compiler != "Visual Studio":
    #     if self.settings.os != "Windows":
    #         self.cpp_info.libs.extend(["boost_%s" % lib for lib in libs])
    #         # self.cpp_info.libs = self.collect_libs()

    #         print("self.cpp_info.libs")
    #         print(self.cpp_info.libs)
            
    #         print("self.collect_libs()")
    #         print(self.collect_libs())

    #     else:
    #         # http://www.boost.org/doc/libs/1_55_0/more/getting_started/windows.html
    #         version = "_".join(self.version.split(".")[0:2])
    #         if self.settings.compiler == "Visual Studio":
    #             win_libs = []
    #             visual_version = self._msvc_version()
    #             runtime = "mt" # str(self.settings.compiler.runtime).lower()
    #             arch = "x64"

    #             abi_tags = []
    #             if self.settings.compiler.runtime in ("MTd", "MT"):
    #                 abi_tags.append("s")

    #             if self.settings.build_type == "Debug":
    #                 abi_tags.append("gd")

    #             abi_tags = ("-%s" % "".join(abi_tags)) if abi_tags else ""

                
    #             suffix = "vc%s-%s%s-%s-%s" %  (visual_version.replace(".", ""), runtime, abi_tags, arch, version)
    #             prefix = "lib" if not self.is_shared else ""

    #             win_libs.extend(["%sboost_%s-%s" % (prefix, lib, suffix) for lib in libs if lib not in ["exception", "test_exec_monitor"]])
    #             win_libs.extend(["libboost_exception-%s" % suffix, "libboost_test_exec_monitor-%s" % suffix])

    #             #self.output.warn("EXPORTED BOOST LIBRARIES: %s" % win_libs)
    #             self.cpp_info.libs.extend(win_libs)
    #             self.cpp_info.defines.extend(["BOOST_ALL_NO_LIB"]) # DISABLES AUTO LINKING! NO SMART AND MAGIC DECISIONS THANKS!
    #         else:
    #             win_libs = []
    #             mingw_version = self._mingw_version()
    #             runtime = "mt" # str(self.settings.compiler.runtime).lower()
    #             arch = "x64"

    #             abi_tags = []

    #             if self.settings.build_type == "Debug":
    #                 abi_tags.append("d")
    #                 # abi_tags.append("gd")

    #             abi_tags = ("-%s" % "".join(abi_tags)) if abi_tags else ""

    #             suffix = "mgw%s-%s%s-%s-%s" %  (mingw_version.replace(".", ""), runtime, abi_tags, arch, version)
    #             #prefix = "lib" if not self.is_shared else ""
    #             prefix = ""

    #             win_libs.extend(["%sboost_%s-%s" % (prefix, lib, suffix) for lib in libs if lib not in ["exception", "test_exec_monitor"]])
    #             win_libs.extend(["boost_exception-%s" % suffix, "boost_test_exec_monitor-%s" % suffix])

    #             #self.output.warn("EXPORTED BOOST LIBRARIES: %s" % win_libs)
    #             self.cpp_info.libs.extend(win_libs)
    #             self.cpp_info.defines.extend(["BOOST_ALL_NO_LIB"]) # DISABLES AUTO LINKING! NO SMART AND MAGIC DECISIONS THANKS!


    def package_info(self):
        gen_libs = tools.collect_libs(self)

        self.cpp_info.libs = [None for _ in range(len(lib_list))]

        # The order is important, reorder following the lib_list order
        missing_order_info = []
        for real_lib_name in gen_libs:
            for pos, alib in enumerate(lib_list):
                if os.path.splitext(real_lib_name)[0].split("-")[0].endswith(alib):
                    self.cpp_info.libs[pos] = real_lib_name
                    break
            else:
                self.output.info("Missing in order: %s" % real_lib_name)
                missing_order_info.append(real_lib_name)  # Assume they do not depend on other

        self.cpp_info.libs = [x for x in self.cpp_info.libs if x is not None] + missing_order_info

        if self.options.without_test:  # remove boost_unit_test_framework
            self.cpp_info.libs = [lib for lib in self.cpp_info.libs if "unit_test" not in lib]

        #Fernando: Removing prg_exec_monitor and test_exec_monitor from libraries 
        self.cpp_info.libs = [lib for lib in self.cpp_info.libs if "prg_exec_monitor" not in lib]
        self.cpp_info.libs = [lib for lib in self.cpp_info.libs if "test_exec_monitor" not in lib]

        if self.settings.os == "Linux" or self.settings.os == "FreeBSD":
            self.cpp_info.libs.append("rt")

        self.output.info("LIBRARIES: %s" % self.cpp_info.libs)
        self.output.info("Package folder: %s" % self.package_folder)

        if not self.options.header_only and self.is_shared:
            self.cpp_info.defines.append("BOOST_ALL_DYN_LINK")
        else:
            self.cpp_info.defines.append("BOOST_USE_STATIC_LIBS")

        if not self.options.header_only:
            if not self.options.without_python:
                if not self.is_shared:
                    self.cpp_info.defines.append("BOOST_PYTHON_STATIC_LIB")

            if self.settings.compiler == "Visual Studio":
                # DISABLES AUTO LINKING! NO SMART AND MAGIC DECISIONS THANKS!
                self.cpp_info.defines.extend(["BOOST_ALL_NO_LIB"])

        if self.settings.compiler == "Visual Studio":
            self.cpp_info.defines.extend(["BOOST_CONFIG_SUPPRESS_OUTDATED_MESSAGE"])

        if not self.options.without_locale:
            self.cpp_info.defines.append("BOOST_LOCALE_HIDE_AUTO_PTR")

            # Related with:
            # https://github.com/boostorg/iostreams/issues/60
            # https://github.com/boostorg/iostreams/pull/57/files
            # Not fixed in Boost Iostreams 1.68.0
            #   Maybe fixed in 1.69.0
            # self.cpp_info.defines.extend(["_SILENCE_FPOS_SEEKPOS_DEPRECATION_WARNING"])




#     def prepare_deps_options_env(self):
#         ret = {}
# #         if self.settings.os == "Linux" and "bzip2" in self.requires:
# #             include_path = self.deps_cpp_info["bzip2"].include_paths[0]
# #             lib_path = self.deps_cpp_info["bzip2"].lib_paths[0]
# #             lib_name = self.deps_cpp_info["bzip2"].libs[0]
# #             ret["BZIP2_BINARY"] = lib_name
# #             ret["BZIP2_INCLUDE"] = include_path
# #             ret["BZIP2_LIBPATH"] = lib_path

#         return ret



    def _msvc_version(self):
        if self.settings.compiler.version == "16":
            return "14.2"
        if self.settings.compiler.version == "15":
            return "14.1"

        return "%s.0" % self.settings.compiler.version

    def _msvc_version_boostrap(self):
        if self.settings.compiler.version == "16":
            return "vc142"
        if self.settings.compiler.version == "15":
            return "vc141"

        return "vc%s" % self.settings.compiler.version


    # def _mingw_version(self):
    #     return "%s" % self.settings.compiler.version

    # def _gcc_short_version(self, version):
    #     return str(version)[0]

