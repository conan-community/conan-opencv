#!/usr/bin/env python
# -*- coding: utf-8 -*-
from conans import ConanFile, CMake, tools
from conans.model.version import Version
from conans.errors import ConanInvalidConfiguration
import os


class OpenCVConan(ConanFile):
    name = "opencv"
    version = "4.0.1"
    license = "BSD-3-Clause"
    homepage = "https://github.com/opencv/opencv"
    url = "https://github.com/conan-community/conan-opencv"
    author = "Conan Community"
    topics = ("conan", "opencv", "computer-vision", "image-processing", "deep-learning")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "contrib": [True, False],
               "jpeg": [True, False],
               "tiff": [True, False],
               "webp": [True, False],
               "png": [True, False],
               "jasper": [True, False],
               "openexr": [True, False],
               "gtk": [None, 2, 3],
               "nonfree": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "contrib": False,
                       "jpeg": True,
                       "tiff": True,
                       "webp": True,
                       "png": True,
                       "jasper": True,
                       "openexr": True,
                       "gtk": 3,
                       "nonfree": False}
    exports_sources = ["CMakeLists.txt"]
    exports = "LICENSE"
    generators = "cmake"
    description = "OpenCV is an open source computer vision and machine learning software library."
    short_paths = True
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def configure(self):
        compiler_version = Version(self.settings.compiler.version.value)
        if self.settings.compiler == "Visual Studio" and compiler_version < "14":
            raise ConanInvalidConfiguration("OpenCV 4.x requires Visual Studio 2015 and higher")

    def source(self):
        sha256 = "7b86a0ee804244e0c407321f895b15e4a7162e9c5c0d2efc85f1cadec4011af4"
        tools.get("{}/archive/{}.tar.gz".format(self.homepage, self.version), sha256=sha256)
        os.rename('opencv-%s' % self.version, self._source_subfolder)

        sha256 = "0d8acbad4b7074cfaafd906a7419c23629179d5e98894714402090b192ef8237"
        tools.get("https://github.com/opencv/opencv_contrib/archive/{}.tar.gz".format(self.version), sha256=sha256)
        os.rename('opencv_contrib-%s' % self.version, 'contrib')

        if self.settings.os != 'Android':
            tools.rmdir(os.path.join(self._source_subfolder, '3rdparty'))

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
        if self.settings.os != 'Linux':
            del self.options.gtk

    def system_requirements(self):
        if self.settings.os == 'Linux' and tools.os_info.is_linux:
            if tools.os_info.with_apt:
                installer = tools.SystemPackageTool()
                arch_suffix = ''
                if self.settings.arch == 'x86':
                    arch_suffix = ':i386'
                elif self.settings.arch == 'x86_64':
                    arch_suffix = ':amd64'
                packages = []
                if self.options.gtk == 2:
                    packages.append('libgtk2.0-dev%s' % arch_suffix)
                elif self.options.gtk == 3:
                    packages.append('libgtk-3-dev%s' % arch_suffix)
                for package in packages:
                    installer.install(package)
            elif tools.os_info.with_yum:
                installer = tools.SystemPackageTool()
                arch_suffix = ''
                if self.settings.arch == 'x86':
                    arch_suffix = '.i686'
                elif self.settings.arch == 'x86_64':
                    arch_suffix = '.x86_64'
                packages = []
                if self.options.gtk == 2:
                    packages.append('gtk2-devel%s' % arch_suffix)
                elif self.options.gtk == 3:
                    packages.append('gtk3-devel%s' % arch_suffix)
                for package in packages:
                    installer.install(package)

    def requirements(self):
        self.requires.add('zlib/1.2.11@conan/stable')
        if self.options.jpeg:
            # NOTE : use the same libjpeg implementation as jasper uses
            # otherwise, jpeg_create_decompress will fail on version check
            # self.requires.add('libjpeg-turbo/1.5.2@bincrafters/stable')
            self.requires.add('libjpeg/9c@bincrafters/stable')
        if self.options.tiff:
            self.requires.add('libtiff/4.0.9@bincrafters/stable')
        if self.options.webp:
            self.requires.add('libwebp/1.0.0@bincrafters/stable')
        if self.options.png:
            self.requires.add('libpng/1.6.34@bincrafters/stable')
        if self.options.jasper:
            self.requires.add('jasper/2.0.14@conan/stable')
        if self.options.openexr:
            self.requires.add('openexr/2.3.0@conan/stable')

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['BUILD_EXAMPLES'] = False
        cmake.definitions['BUILD_DOCS'] = False
        cmake.definitions['BUILD_TESTS'] = False
        cmake.definitions['BUILD_PERF_TEST'] = False
        cmake.definitions['WITH_IPP'] = False
        cmake.definitions['BUILD_opencv_apps'] = False
        cmake.definitions['BUILD_opencv_java'] = False

        if self.settings.compiler == 'Visual Studio':
            cmake.definitions['BUILD_WITH_STATIC_CRT'] = 'MT' in str(self.settings.compiler.runtime)
        if self.settings.os != 'Windows':
            cmake.definitions['ENABLE_PIC'] = self.options.fPIC

        # 3rd-party

        # disable builds for all 3rd-party components, use libraries from conan only
        cmake.definitions['BUILD_ZLIB'] = False
        cmake.definitions['BUILD_TIFF'] = False
        cmake.definitions['BUILD_JASPER'] = False
        cmake.definitions['BUILD_JPEG'] = False
        cmake.definitions['BUILD_PNG'] = False
        cmake.definitions['BUILD_OPENEXR'] = False
        cmake.definitions['BUILD_WEBP'] = False
        cmake.definitions['BUILD_TBB'] = False
        cmake.definitions['BUILD_IPP_IW'] = False
        cmake.definitions['BUILD_ITT'] = False
        cmake.definitions['BUILD_JPEG_TURBO_DISABLE'] = True

        cmake.definitions['WITH_JPEG'] = self.options.jpeg
        cmake.definitions['WITH_TIFF'] = self.options.tiff
        cmake.definitions['WITH_WEBP'] = self.options.webp
        cmake.definitions['WITH_PNG'] = self.options.png
        cmake.definitions['WITH_JASPER'] = self.options.jasper
        cmake.definitions['WITH_OPENEXR'] = self.options.openexr
        cmake.definitions['WITH_PROTOBUF'] = False
        cmake.definitions['WITH_FFMPEG'] = False
        cmake.definitions['WITH_QUIRC'] = False
        cmake.definitions["WITH_CAROTENE"] = False

        if self.options.openexr:
            cmake.definitions['OPENEXR_ROOT'] = self.deps_cpp_info['openexr'].rootpath

        # system libraries
        if self.settings.os == 'Linux':
            cmake.definitions['WITH_GTK'] = self.options.gtk is not None
            cmake.definitions['WITH_GTK_2_X'] = self.options.gtk == 2

        if self.options.contrib:
            cmake.definitions['OPENCV_EXTRA_MODULES_PATH'] = os.path.join(self.build_folder, 'contrib', 'modules')

        if self.options.nonfree:
            cmake.definitions['OPENCV_ENABLE_NONFREE'] = True

        if self.settings.os == 'Android':
            cmake.definitions['ANDROID_STL'] = self.settings.compiler.libcxx
            cmake.definitions['ANDROID_NATIVE_API_LEVEL'] = self.settings.os.api_level

            cmake.definitions['BUILD_PERF_TESTS'] = False
            cmake.definitions['BUILD_ANDROID_EXAMPLES'] = False

            arch = str(self.settings.arch)
            if arch.startswith(('armv7', 'armv8')):
                cmake.definitions['ANDROID_ABI'] = 'NEON'
            else:
                cmake.definitions['ANDROID_ABI'] = {'armv5': 'armeabi',
                                                    'armv6': 'armeabi-v6',
                                                    'armv7': 'armeabi-v7a',
                                                    'armv7hf': 'armeabi-v7a',
                                                    'armv8': 'arm64-v8a'}.get(arch, arch)

            if 'ANDROID_NDK_HOME' in os.environ:
                cmake.definitions['ANDROID_NDK'] = os.environ.get('ANDROID_NDK_HOME')

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        # https://github.com/opencv/opencv/issues/8010
        if str(self.settings.compiler) == 'clang' and str(self.settings.compiler.version) == '3.9':
            tools.replace_in_file(os.path.join(self._source_subfolder, 'modules', 'imgproc', 'CMakeLists.txt'),
                                  'ocv_define_module(imgproc opencv_core WRAP java python js)',
                                  'ocv_define_module(imgproc opencv_core WRAP java python js)\n'
                                  'set_source_files_properties(${CMAKE_CURRENT_LIST_DIR}/src/'
                                  'imgwarp.cpp PROPERTIES COMPILE_FLAGS "-O0")')

        # allow to find conan-supplied OpenEXR
        if self.options.openexr:
            find_openexr = os.path.join(self._source_subfolder, 'cmake', 'OpenCVFindOpenEXR.cmake')
            tools.replace_in_file(find_openexr,
                                  r'SET(OPENEXR_ROOT "C:/Deploy" CACHE STRING "Path to the OpenEXR \"Deploy\" folder")',
                                  '')
            tools.replace_in_file(find_openexr, r'set(OPENEXR_ROOT "")', '')
            tools.replace_in_file(find_openexr, 'SET(OPENEXR_LIBSEARCH_SUFFIXES x64/Release x64 x64/Debug)', '')
            tools.replace_in_file(find_openexr, 'SET(OPENEXR_LIBSEARCH_SUFFIXES Win32/Release Win32 Win32/Debug)',
                                  '')

            def openexr_library_names(name):
                # OpenEXR library may have different names, depends on namespace versioning, static, debug, etc.
                reference = str(self.requires["openexr"])
                version_name = reference.split("@")[0]
                version = version_name.split("/")[1]
                version_tokens = version.split('.')
                major, minor = version_tokens[0], version_tokens[1]
                suffix = '%s_%s' % (major, minor)
                names = ['%s-%s' % (name, suffix),
                         '%s-%s_s' % (name, suffix),
                         '%s-%s_d' % (name, suffix),
                         '%s-%s_s_d' % (name, suffix),
                         '%s' % name,
                         '%s_s' % name,
                         '%s_d' % name,
                         '%s_s_d' % name]
                return ' '.join(names)

            for lib in ['Half', 'Iex', 'Imath', 'IlmImf', 'IlmThread']:
                tools.replace_in_file(find_openexr, 'NAMES %s' % lib, 'NAMES %s' % openexr_library_names(lib))

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        cmake.patch_config_paths()

    def add_libraries_from_pc(self, library):
        pkg_config = tools.PkgConfig(library)
        libs = [lib[2:] for lib in pkg_config.libs_only_l]  # cut -l prefix
        lib_paths = [lib[2:] for lib in pkg_config.libs_only_L]  # cut -L prefix
        self.cpp_info.libs.extend(libs)
        self.cpp_info.libdirs.extend(lib_paths)
        self.cpp_info.sharedlinkflags.extend(pkg_config.libs_only_other)
        self.cpp_info.exelinkflags.extend(pkg_config.libs_only_other)

    def package_info(self):
        opencv_libs = ["gapi",
                    "stitching",
                    "photo",
                    "video",
                    "ml",
                    "calib3d",
                    "features2d",
                    "highgui",
                    "videoio",
                    "flann",
                    "imgcodecs",
                    "objdetect",
                    "imgproc",
                    "core"]

        if self.options.contrib:
            opencv_libs = [
                "aruco",
                "bgsegm",
                "bioinspired",
                "ccalib",
                "datasets",
                "dpm",
                "face",
                "freetype",
                "fuzzy",
                "hfs",
                "img_hash",
                "line_descriptor",
                "optflow",
                "phase_unwrapping",
                "plot",
                "reg",
                "rgbd",
                "saliency",
                "shape",
                "stereo",
                "structured_light",
                "superres",
                "surface_matching",
                "tracking",
                "videostab",
                "xfeatures2d",
                "ximgproc",
                "xobjdetect",
                "xphoto"] + opencv_libs

        suffix = 'd' if self.settings.build_type == 'Debug' and self.settings.compiler == 'Visual Studio' else ''
        version = self.version.replace(".", "") if self.settings.os == "Windows" else ""
        for lib in opencv_libs:
            self.cpp_info.libs.append("opencv_%s%s%s" % (lib, version, suffix))

        if self.settings.compiler == 'Visual Studio':
            arch = {'x86': 'x86',
                    'x86_64': 'x64'}.get(str(self.settings.arch))
            vc = 'vc%s' % str(self.settings.compiler.version)
            bindir = os.path.join(self.package_folder, arch, vc, 'bin')
            libdir = os.path.join(self.package_folder, arch, vc, 'lib' if self.options.shared else 'staticlib')
            self.cpp_info.bindirs.append(bindir)
            self.cpp_info.libdirs.append(libdir)

        if self.settings.os == "Linux":
            self.cpp_info.libs.extend([
                "pthread",
                "m",
                "dl"])
            if self.options.gtk == 2:
                self.add_libraries_from_pc('gtk+-2.0')
            elif self.options.gtk == 3:
                self.add_libraries_from_pc('gtk+-3.0')
        elif self.settings.os == 'Macos':
            for framework in ['OpenCL',
                              'Accelerate',
                              'CoreMedia',
                              'CoreVideo',
                              'CoreGraphics',
                              'AVFoundation',
                              'QuartzCore',
                              'Cocoa']:
                self.cpp_info.exelinkflags.append('-framework %s' % framework)
            self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags
        elif self.settings.os == 'Windows':
            self.cpp_info.libs.append('Vfw32')
        if self.settings.os == 'Android' and not self.options.shared:
            self.cpp_info.includedirs.append(os.path.join('sdk', 'native', 'jni', 'include'))
            self.cpp_info.libdirs.append(os.path.join('sdk', 'native', 'staticlibs'))
        else:
            self.cpp_info.includedirs.append(os.path.join('include', 'opencv4'))
            self.cpp_info.libdirs.append(os.path.join('lib', 'opencv4', '3rdparty'))
        if not self.options.shared:
            self.cpp_info.libs.append('ade')
