#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conan import ConanFile
import os


class CapicxxDeploymentConan(ConanFile):
    name = "capicxx-conan-deployment"
    package_type = "application"
    settings = "os", "compiler", "build_type", "arch"
    author = "Matthew Russell <matthew.g.russell@gmail.com>"
    description = "Build and deploy configured AMF components"

    version = "1.0.0"

    requires = ("amf-ping/[>=2.1]@kheaactua/stable",)

    default_options = {
        "vsomeip/*:base_path": os.getenv("VSOMEIP_BASE_PATH"),
    }

    python_requires = "capicxx-conan-helpers/[>=0.1]@covesa/stable"
    python_requires_extend = "capicxx-conan-helpers.CapiConan"

    generators = ("VirtualRunEnv", "VirtualBuildEnv")
