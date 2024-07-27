#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.scm import Git
from conan.tools.files import (
    get,
    copy,
    apply_conandata_patches,
    export_conandata_patches,
)


class VSomeIPConan(ConanFile):
    name = "vsomeip"
    package_type = "shared-library"
    settings = "os", "compiler", "build_type", "arch"
    license = "https://github.com/COVESA/vsomeip/blob/master/LICENSE"
    author = "https://github.com/COVESA/vsomeip/blob/master/AUTHORS"
    url = "https://github.com/covesa/vsomeip.git"
    description = "An implementation of Scalable service-Oriented MiddlewarE over IP"
    topics = ("tcp", "C++", "networking")

    version = "3.4.10"

    options = {
        "verbose_makefile": [True, False],
        "multiple_routingmanagers": [True, False],
        "install_routingmanager": [True, False],
        "disable_security": [True, False],
        "enable_signal_handling": [True, False],
        "base_path": [None, "ANY"],
    }
    default_options = {
        "disable_security": True,
        "verbose_makefile": False,
        "multiple_routingmanagers": True,
        "install_routingmanager": True,
        "enable_signal_handling": True,
        "base_path": None,
        "boost/*:shared": False,
        "boost/*:fPIC": False,
        "boost/*:without_context": True,
        "boost/*:without_fiber": True,
        "boost/*:without_coroutine": True,
        "boost/*:without_mpi": True,
    }

    requires = ("boost/[>=1.82]",)

    python_requires = "capicxx-conan-helpers/[>=0.1]@covesa/stable"
    python_requires_extend = "capicxx-conan-helpers.CapiConan"

    @property
    def base_path(self):
        return self.options.base_path if self.options.base_path else None

    def export_sources(self):
        export_conandata_patches(self)

    def build_requirements(self):
        self.tool_requires("extra-cmake-modules/[>=6.2.0]", run=True)

    def requirements(self):
        if self.settings.os == "Linux":
            self.requires("benchmark/[>=1.8]")
            self.default_options["boost/*:with_stacktrace_backtrace"] = True

        # Used in testing code, this shouldn't be pushed upstream.
        self.requires("fmt/[>=10.2]")

    def layout(self):
        cmake_layout(
            self,
            src_folder="vsomeip-source",
            build_folder=f"bld-{self.settings.os}".lower(),
        )

    def source(self):
        git = Git(self)

        git.clone(url=self.url, target=".")
        tag = self.version

        git.checkout(tag)

        apply_conandata_patches(self)

        # vsomeip wants googletest as source
        get(
            self,
            **self.conan_data["gtest-sources"]["1.10.0"],
            strip_root=True,
            destination=os.path.join("..", "gtest"),
        )

    def generate(self):
        # Without this, we won't find benchmark
        cd = CMakeDeps(self)
        cd.generate()

        tc = CMakeToolchain(self)

        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0093"] = "NEW"

        # Not sure why, but boost when imported by Conan doesn't have
        # BOOST_VERSION_MACRO defined (despite using CMake>1.15), this was also
        # reported at
        # https://github.com/conan-io/conan-center-index/issues/22249 .  Adding
        # it back in.  Being careful about how I build the version string such
        # that custom forks of the conan boost recipes will still work
        bc = self.dependencies["boost"].ref.version
        boost_version_macro = (
            f"{bc.major.value:<02}{bc.minor.value:<02}{bc.patch.value:<02}"
        )
        tc.cache_variables["Boost_VERSION_MACRO"] = f'"{boost_version_macro}"'

        tc.cache_variables[
            "ENABLE_MULTIPLE_ROUTING_MANAGERS"
        ] = self.options.multiple_routingmanagers
        tc.cache_variables[
            "ENABLE_SIGNAL_HANDLING"
        ] = self.options.enable_signal_handling
        tc.cache_variables[
            "VSOMEIP_INSTALL_ROUTINGMANAGERD"
        ] = self.options.install_routingmanager
        tc.cache_variables["DISABLE_SECURITY"] = self.options.disable_security

        if self.settings.os == "Neutrino":
            tc.cache_variables["PKG_CONFIG_EXECUTABLE"] = ""

        tc.cache_variables["CMAKE_VERBOSE_MAKEFILE"] = self.options.verbose_makefile

        tc.cache_variables["GTEST_ROOT"] = os.path.join(
            self.source_folder, "..", "gtest"
        )

        if self.base_path is not None:
            tc.cache_variables["VSOMEIP_BASE_PATH"] = self.base_path

        if self.settings.os != "Neutrino":
            tc.cache_variables["CMAKE_EXPORT_COMPILE_COMMANDS"] = True

            # Covesa variant:
            if self.enable_asan:
                tc.cache_variables["ENABLE_ADDRESS_SANITIZER"] = True
            if self.enable_lsan:
                tc.cache_variables["ENABLE_LEAK_SANITIZER"] = True
            if self.enable_tsan:
                tc.cache_variables["ENABLE_THREAD_SANITIZER"] = True
            if self.enable_ubsan:
                tc.cache_variables["ENABLE_UNDEFINED_SANITIZER"] = True

        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.builddirs = ["lib/cmake"]
        self.cpp_info.libs = ["vsomeip3", "vsomeip3-sd", "vsomeip3-e2e"]
        if not self.options.multiple_routingmanagers:
            self.cpp_info.libs.append("vsomeip3-cfg")

        if self.settings.os == "Windows":
            self.cpp_info.systm_libs.extend(["winmm", "ws2_32"])
        elif self.settings.os == "Neutrino":
            self.cpp_info.system_libs.extend(["socket", "regex"])

    def deploy(self):
        copy(
            self,
            "*",
            src=self.package_folder,
            dst=self.deploy_folder,
            excludes=["*.json"],
        )
