#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.scm import Git
from conan.tools.files import copy


class CapicxxCMakeModulesRecipe(ConanFile):
    name = "capicxx-cmake-modules"
    settings = "os", "build_type"
    author = "Matthew Russell <matthew.g.russell@gmail.com>"
    description = "CMake modules to import and use capicxx generators"

    version = "0.7.8"
    channel = "stable"

    tool_requires = "cmake/[>=3.23]"

    requires = (
        "capicxx-core-runtime/[>=3.2.3r7, include_prerelease]@covesa/stable",
        "capicxx-someip-runtime/[>=3.2.3r8, include_prerelease]@covesa/stable",
        "vsomeip/3.4.10@covesa/stable",
    )

    def build_requirements(self):
        self.tool_requires("capicxx-generators/3.2.14@covesa/prebuilt", visible=True)

    def source(self):
        git = Git(self)
        git.clone(url="https://github.com/covesa/capicxx-cmake-modules.git", target=".")
        git.checkout("v" + self.version)

    def layout(self):
        cmake_layout(self, src_folder="capicxx-cmake-modules-source")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.builddirs = ["lib/cmake"]

    def deploy(self):
        copy(self, "*", src=self.package_folder, dst=self.deploy_folder)
