#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conan import ConanFile


class CapiConan:

    @property
    def enable_asan(conanfile):
        return (
            conanfile.settings.compiler.sanitizer == "asan"
            if hasattr(conanfile.settings.compiler, "sanitizer")
            else False
        )

    @property
    def enable_msan(conanfile):
        return (
            conanfile.settings.compiler.sanitizer == "msan"
            if hasattr(conanfile.settings.compiler, "sanitizer")
            else False
        )

    @property
    def enable_lsan(conanfile):
        return (
            conanfile.settings.compiler.sanitizer == "lsan"
            if hasattr(conanfile.settings.compiler, "sanitizer")
            else False
        )

    @property
    def enable_tsan(conanfile):
        return (
            conanfile.settings.compiler.sanitizer == "tsan"
            if hasattr(conanfile.settings.compiler, "sanitizer")
            else False
        )

    @property
    def enable_ubsan(conanfile):
        return (
            conanfile.settings.compiler.sanitizer == "ubsan"
            if hasattr(conanfile.settings.compiler, "sanitizer")
            else False
        )

    def ecm_sanitizers(conanfile, cmake_toolchain):
        sanitizers = []
        if conanfile.enable_asan:
            sanitizers.append("address")
        if conanfile.enable_msan:
            sanitizers.append("memory")
        if conanfile.enable_lsan:
            sanitizers.append("leak")
        if conanfile.enable_tsan:
            sanitizers.append("thread")
        if conanfile.enable_ubsan:
            sanitizers.append("undefined")
        if len(sanitizers):
            cmake_toolchain.cache_variables["ECM_ENABLE_SANITIZERS"] = ";".join(
                sanitizers
            )


class CapiConanHelpersConan(ConanFile):
    name = "capicxx-conan-helpers"
    version = "0.1.0"
    license = "MIT"
    description = "Helper functions for conan"
    package_type = "python-require"

# vim: ts=4 sw=4 expandtab ffs=unix ft=python foldmethod=marker :
