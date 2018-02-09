from conans import ConanFile, CMake, tools
from conans.tools import os_info, SystemPackageTool
import os


class OpenCVConan(ConanFile):
    name = "OpenCV"
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
                "jasper/2.0.14@conan/testing")

    def source(self):
        tools.download("https://github.com/opencv/opencv/archive/2.4.13.5.zip", "opencv.zip")
        tools.unzip("opencv.zip")
        os.unlink("opencv.zip")
        tools.replace_in_file("opencv-%s/CMakeLists.txt" % self.version, "project(OpenCV CXX C)",
                                """project(OpenCV CXX C)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()""")
     
    def system_requirements(self):
        pack_names = None
        if os_info.linux_distro == "ubuntu":
            pack_names = "libgtk2.0-dev", "pkg-config"
            installer = SystemPackageTool()
            installer.update() # Update the package database
            for pack_name in pack_names:
                installer.install(pack_name) # Install the package

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_EXAMPLES"] = "OFF"
        cmake.definitions["BUILD_DOCS"] = "OFF"
        cmake.definitions["BUILD_TESTS"] = "OFF"
        cmake.definitions["BUILD_opencv_apps"] = "OFF"
        cmake.definitions["BUILD_ZLIB"] = "OFF"
        cmake.definitions["BUILD_JPEG"] = "OFF"
        cmake.definitions["BUILD_PNG"] = "OFF"
        cmake.definitions["BUILD_TIFF"] = "OFF"
        cmake.definitions["BUILD_JASPER"] = "OFF"

        if self.settings.compiler == "Visual Studio":
            if "MT" in str(self.settings.compiler.runtime):
                cmake.definitions["BUILD_WITH_STATIC_CRT"] = "ON"
            else: 
                cmake.definitions["BUILD_WITH_STATIC_CRT"] = "OFF"
        cmake.configure(source_folder='opencv-%s' % self.version)
        cmake.build()

    opencv_libs = ["contrib","stitching", "nonfree", "superres", "ocl", "ts", "videostab", "gpu", "photo", "objdetect", 
                   "legacy", "video", "ml", "calib3d", "features2d", "highgui", "imgproc", "flann", "core"]

    def package(self):
        self.copy("*.h*", "include", "opencv-%s/include" % self.version)
        self.copy("*.h*","include/opencv2","opencv2") #opencv2/opencv_modules.hpp is generated
        for lib in self.opencv_libs:
            self.copy("*.h*", "include", "opencv-%s/modules/%s/include" % (self.version, lib))
        self.copy("*.lib", "lib", "lib", keep_path=False)
        self.copy("*.a", "lib", "lib", keep_path=False) 
        self.copy("*.dll", "bin", "bin", keep_path=False)
        self.copy("*.dylib", "lib", "lib", keep_path=False)
        self.copy("*.so", "lib", "lib", keep_path=False)
        self.copy("*.xml", "data", "opencv-%s/data" % (self.version))
        self.copy("*opencv.pc", keep_path=False)
        if not self.options.shared:
            self.copy("*.lib", "lib", "3rdparty/lib", keep_path=False)
            self.copy("*.a", "lib", "3rdparty/lib", keep_path=False)

    def package_info(self):
        version = self.version.split(".")[:-1]  # last version number is not used
        version = "".join(version) if self.settings.os == "Windows" else ""
        for lib in self.opencv_libs:
            self.cpp_info.libs.append("opencv_%s%s" % (lib, version))

        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.libs.extend(["IlmImf"])

        if self.settings.os == "Linux":     
            if not self.options.shared:
                other_libs = self.collect_libs()
                for other_lib in ["IlmImf"]:
                    if other_lib in other_libs:
                        self.cpp_info.libs.append(other_lib)
                    else:
                        self.cpp_info.libs.append(other_lib.replace("lib", ""))

            self.cpp_info.libs.extend(["gthread-2.0", "freetype", "fontconfig", "glib-2.0", "gobject-2.0", "pango-1.0", "pangoft2-1.0", "gio-2.0", "gdk_pixbuf-2.0",
                                        "cairo", "atk-1.0", "pangocairo-1.0"," gtk-x11-2.0", "gdk-x11-2.0", "rt", "pthread", "m", "dl"])
