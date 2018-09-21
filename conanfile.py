from conans import ConanFile, CMake, tools
from conans.tools import SystemPackageTool
import os


class OpenCVConan(ConanFile):
    name = "opencv"
    version = "2.4.13.5"
    license = "LGPL"
    homepage = "https://github.com/opencv/opencv"
    description = "OpenCV (Open Source Computer Vision Library)"
    url = "https://github.com/conan-community/conan-opencv.git"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "cmake"
    requires = ("zlib/1.2.11@conan/stable", "libjpeg/9b@bincrafters/stable",
                "libpng/1.6.34@bincrafters/stable", "libtiff/4.0.8@bincrafters/stable",
                "jasper/2.0.14@conan/stable")

    def source(self):
        tools.download("https://github.com/opencv/opencv/archive/%s.zip" % self.version, "opencv.zip")
        tools.unzip("opencv.zip")
        os.unlink("opencv.zip")
        tools.replace_in_file("opencv-%s/CMakeLists.txt" % self.version, "project(OpenCV CXX C)",
                                """project(OpenCV CXX C)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()""")

    def system_requirements(self):
        if self.settings.os == 'Linux' and tools.os_info.is_linux:
            if tools.os_info.with_apt:
                installer = SystemPackageTool()
                installer.update()  # Update the package database
                arch_suffix = ''
                if self.settings.arch == 'x86':
                    arch_suffix = ':i386'
                elif self.settings.arch == 'x86_64':
                    arch_suffix = ":amd64"
                for pack_name in ("libgtk2.0-dev", "pkg-config", "libpango1.0-dev", "libcairo2-dev", "libglib2.0-dev"):
                    installer.install('%s%s' % (pack_name, arch_suffix))  # Install the package

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
        cmake.definitions["WITH_OPENEXR"] = False

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
                   "ocl",
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

    def package_info(self):
        version = self.version.split(".")[:-1]  # last version number is not used
        version = "".join(version) if self.settings.os == "Windows" else ""
        debug = "d" if self.settings.build_type == "Debug" and self.settings.compiler == "Visual Studio" else ""
        for lib in self.opencv_libs:
            self.cpp_info.libs.append("opencv_%s%s%s" % (lib, version, debug))

        if self.settings.compiler == 'Visual Studio':
            libdir = os.path.join(self.package_folder, 'lib' if self.options.shared else 'staticlib')
            self.cpp_info.libdirs.append(libdir)

        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["gthread-2.0",
                                       "freetype",
                                       "fontconfig",
                                       "glib-2.0",
                                       "gobject-2.0",
                                       "pango-1.0",
                                       "pangoft2-1.0",
                                       "gio-2.0",
                                       "gdk_pixbuf-2.0",
                                        "cairo",
                                       "atk-1.0",
                                       "pangocairo-1.0",
                                       " gtk-x11-2.0",
                                       "gdk-x11-2.0",
                                       "rt",
                                       "pthread",
                                       "m",
                                       "dl"])
