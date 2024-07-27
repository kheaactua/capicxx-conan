import re

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.scm import Git
from conan.tools.files import copy, apply_conandata_patches, export_conandata_patches


class CapicxxSomeipRuntimeConan(ConanFile):
    name = "capicxx-someip-runtime"
    package_type = "shared-library"
    settings = "os", "compiler", "build_type", "arch"
    license = "https://github.com/COVESA/capicxx-someip-runtime/blob/master/LICENSE"
    author = "https://github.com/COVESA/capicxx-someip-runtime/blob/master/AUTHORS"
    url = "https://github.com/covesa/capicxx-someip-runtime.git"
    description = "Middleware for CommonAPI"
    topics = ("tcp", "C++", "networking")

    version = "3.2.3r8"

    options = {
        "verbose_makefile": [True, False],
    }
    default_options = {
        "verbose_makefile": False,
    }

    requires = {
        "vsomeip/[>=3.4]@covesa/stable",
        "capicxx-core-runtime/[>=3.2.3r7, include_prerelease]@covesa/stable",
    }

    tool_requires = "gtest/[>=1.10]", "extra-cmake-modules/[>=6.2]"

    python_requires = "capicxx-conan-helpers/[>=0.1]@covesa/stable"
    python_requires_extend = "capicxx-conan-helpers.CapiConan"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(
            self,
            src_folder="capicxx-someip-runtime-source",
            build_folder=f"bld-{self.settings.os}".lower(),
        )

    def source(self):
        git = Git(self)
        git.clone(url=self.url, target=".")
        tag = re.sub(r"r", "-r", self.version)
        git.checkout(tag)

        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)

        if self.settings.os == "Neutrino":
            tc.cache_variables["PKG_CONFIG_EXECUTABLE"] = ""
        tc.cache_variables["CMAKE_VERBOSE_MAKEFILE"] = self.options.verbose_makefile

        if self.settings.os != "Neutrino":
            tc.cache_variables["CMAKE_EXPORT_COMPILE_COMMANDS"] = True

        self.ecm_sanitizers(tc)

        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["CommonAPI-SomeIP"]
        self.cpp_info.builddirs = ["lib/cmake"]

    def deploy(self):
        copy(self, "*", src=self.package_folder, dst=self.deploy_folder)
