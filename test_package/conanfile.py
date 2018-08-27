#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from conans import ConanFile, CMake, tools
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def imports(self):
        self.copy("*haarcascade_*.xml", os.path.join('haarcascades'), keep_path=False)
        self.copy("*lbpcascade_*.xml", os.path.join('lbpcascades'), keep_path=False)

    def test(self):
        img_path = os.path.join(self.source_folder, "lena.jpg")
        shutil.copy(img_path, '.')
        bin_path = os.path.join("bin", "lena")
        self.run(bin_path, run_environment=True)
