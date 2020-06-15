#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from conans import ConanFile, CMake, tools
import os
import shutil
import sys

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def imports(self):
        self.copy("*haarcascade_*.xml", os.path.join('bin', 'haarcascades'), keep_path=False)
        self.copy("*lbpcascade_*.xml", os.path.join('bin', 'lbpcascades'), keep_path=False)

    def test(self):
        if tools.cross_building(self.settings):
            return
        img_path = os.path.join(self.source_folder, "lena.jpg")
        shutil.copy(img_path, 'bin')
        with tools.chdir('bin'):
            self.run('lena.exe' if self.settings.os == 'Windows' else './lena', run_environment=True)
            test_images = []
            if self.options["opencv"].jpeg:
                test_images.append('lena.jpg')
            if self.options["opencv"].libtiff != False:
                test_images.append('normal.tiff')
                if self.options["libtiff"].lzma != False:
                    test_images.append('lzma.tiff')
                if self.options['libtiff'].jbig != False:
                    test_images.append('jbig.tiff')
            for image in test_images:
                self.run(('load-image.exe' if self.settings.os == 'Windows' else './load-image') + ' ' + image, run_environment=True)
