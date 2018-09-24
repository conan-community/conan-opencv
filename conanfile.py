from conans import ConanFile, CMake, tools
from conans.tools import SystemPackageTool
import os
import shutil


class OpenCVConan(ConanFile):
    name = "opencv"
    version = "2.4.13.5"
    license = "LGPL"
    homepage = "https://github.com/opencv/opencv"
    description = "OpenCV (Open Source Computer Vision Library)"
    url = "https://github.com/conan-community/conan-opencv.git"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "jpeg": [True, False],
               "png": [True, False],
               "tiff": [True, False],
               "jasper": [True, False],
               "openexr": [True, False]}
    default_options = "shared=False",\
                      "fPIC=True",\
                      "jpeg=True",\
                      "png=True",\
                      "tiff=True",\
                      "jasper=True",\
                      "openexr=True"
    generators = "cmake"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def requirements(self):
        self.requires.add('zlib/1.2.11@conan/stable')
        if self.options.jpeg:
            self.requires.add('libjpeg/9b@bincrafters/stable')
        if self.options.png:
            self.requires.add('libpng/1.6.34@bincrafters/stable')
        if self.options.tiff:
            self.requires.add('libtiff/4.0.8@bincrafters/stable')
        if self.options.jasper:
            self.requires.add('jasper/2.0.14@conan/stable')
        if self.options.openexr:
            self.requires.add('openexr/2.3.0@conan/stable')

    def source(self):
        tools.download("https://github.com/opencv/opencv/archive/%s.zip" % self.version, "opencv.zip")
        tools.unzip("opencv.zip")
        os.unlink("opencv.zip")
        tools.replace_in_file("opencv-%s/CMakeLists.txt" % self.version, "project(OpenCV CXX C)",
                              """project(OpenCV CXX C)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()""")

        # allow to find conan-supplied OpenEXR
        if self.options.openexr:
            find_openexr = os.path.join('opencv-%s' % self.version, 'cmake', 'OpenCVFindOpenEXR.cmake')
            tools.replace_in_file(find_openexr,
                                  r'SET(OPENEXR_ROOT "C:/Deploy" CACHE STRING "Path to the OpenEXR \"Deploy\" folder")',
                                  '')
            tools.replace_in_file(find_openexr, r'set(OPENEXR_ROOT "")', '')
            tools.replace_in_file(find_openexr, 'SET(OPENEXR_LIBSEARCH_SUFFIXES x64/Release x64 x64/Debug)', '')
            tools.replace_in_file(find_openexr, 'SET(OPENEXR_LIBSEARCH_SUFFIXES Win32/Release Win32 Win32/Debug)', '')

            def openexr_library_names(name):
                # OpenEXR library may have different names, depends on namespace versioning, static, debug, etc.
                version = self.requires["openexr"].conan_reference.version
                version_tokens = version.split('.')
                major, minor = version_tokens[0], version_tokens[1]
                suffix = '%s_%s' % (major, minor)
                names = [name,
                         '%s-%s' % (name, suffix),
                         '%s-%s_s' % (name, suffix),
                         '%s-%s_d' % (name, suffix),
                         '%s-%s_s_d' % (name, suffix),
                         '%s_s' % name,
                         '%s_s_d' % name]
                return ' '.join(names)

            for lib in ['Half', 'Iex', 'Imath', 'IlmImf', 'IlmThread']:
                tools.replace_in_file(find_openexr, 'NAMES %s' % lib, 'NAMES %s' % openexr_library_names(lib))

        shutil.rmtree(os.path.join('opencv-%s' % self.version, '3rdparty'))

    def system_requirements(self):
        if self.settings.os == 'Linux' and tools.os_info.is_linux:
            if tools.os_info.with_apt:
                installer = SystemPackageTool()
                arch_suffix = ''
                if self.settings.arch == 'x86':
                    arch_suffix = ':i386'
                elif self.settings.arch == 'x86_64':
                    arch_suffix = ":amd64"
                packages = ["libgtk2.0-dev%s" % arch_suffix]
                for package in packages:
                    installer.install(package)

    def configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_EXAMPLES"] = False
        cmake.definitions["BUILD_DOCS"] = False
        cmake.definitions["BUILD_TESTS"] = False
        cmake.definitions["BUILD_opencv_apps"] = False
        cmake.definitions['BUILD_opencv_java'] = False
        cmake.definitions["BUILD_ZLIB"] = False
        cmake.definitions["BUILD_JPEG"] = False
        cmake.definitions["BUILD_PNG"] = False
        cmake.definitions["BUILD_TIFF"] = False
        cmake.definitions["BUILD_JASPER"] = False
        cmake.definitions["BUILD_OPENEXR"] = False

        cmake.definitions['WITH_CUDA'] = False
        cmake.definitions['WITH_CUFFT'] = False
        cmake.definitions['WITH_CUBLAS'] = False
        cmake.definitions['WITH_NVCUVID'] = False
        cmake.definitions['WITH_FFMPEG'] = False
        cmake.definitions["WITH_GSTREAMER"] = False
        cmake.definitions["WITH_OPENCL"] = False

        cmake.definitions['WITH_JPEG'] = self.options.jpeg
        cmake.definitions['WITH_PNG'] = self.options.png
        cmake.definitions['WITH_TIFF'] = self.options.tiff
        cmake.definitions['WITH_JASPER'] = self.options.jasper
        cmake.definitions['WITH_OPENEXR'] = self.options.openexr

        if self.settings.compiler == "Visual Studio":
            cmake.definitions["BUILD_WITH_STATIC_CRT"] = "MT" in str(self.settings.compiler.runtime)
        cmake.configure(source_folder='opencv-%s' % self.version)

        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    opencv_libs = ["contrib",
                   "stitching",
                   "nonfree",
                   "superres",
                   "ts",
                   "videostab",
                   "gpu",
                   "photo",
                   "objdetect",
                   "legacy",
                   "video",
                   "ml",
                   "calib3d",
                   "features2d",
                   "highgui",
                   "imgproc",
                   "flann",
                   "core"]

    def package(self):
        cmake = self.configure_cmake()
        cmake.install()

    def add_libraries_from_pc(self, library):
        pkg_config = tools.PkgConfig(library)
        libs = [lib[2:] for lib in pkg_config.libs_only_l]  # cut -l prefix
        lib_paths = [lib[2:] for lib in pkg_config.libs_only_L]  # cut -L prefix
        self.cpp_info.libs.extend(libs)
        self.cpp_info.libdirs.extend(lib_paths)
        self.cpp_info.sharedlinkflags.extend(pkg_config.libs_only_other)
        self.cpp_info.exelinkflags.extend(pkg_config.libs_only_other)

    def package_info(self):
        version = self.version.split(".")[:-1]  # last version number is not used
        version = "".join(version) if self.settings.os == "Windows" else ""
        debug = "d" if self.settings.build_type == "Debug" and self.settings.compiler == "Visual Studio" else ""
        for lib in self.opencv_libs:
            self.cpp_info.libs.append("opencv_%s%s%s" % (lib, version, debug))

        if self.settings.compiler == 'Visual Studio':
            libdir = 'lib' if self.options.shared else 'staticlib'
            arch = {'x86': 'x86',
                    'x86_64': 'x64'}.get(str(self.settings.arch))
            if self.settings.compiler.version == '12':
                libdir = os.path.join(self.package_folder, arch, 'vc12', libdir)
                bindir = os.path.join(self.package_folder, arch, 'vc12', 'bin')
            elif self.settings.compiler.version == '14':
                libdir = os.path.join(self.package_folder, arch, 'vc14', libdir)
                bindir = os.path.join(self.package_folder, arch, 'vc14', 'bin')
            else:
                libdir = os.path.join(self.package_folder, libdir)
                bindir = os.path.join(self.package_folder, 'bin')
            self.cpp_info.bindirs.append(bindir)
            self.cpp_info.libdirs.append(libdir)

        if self.settings.os == "Linux":
            self.add_libraries_from_pc('gtk+-2.0')
            self.cpp_info.libs.extend(["rt", "pthread", "m", "dl"])
        elif self.settings.os == "Macos":
            frameworks = ["Cocoa"]
            for framework in frameworks:
                self.cpp_info.exelinkflags.append("-framework %s" % framework)
            self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags
