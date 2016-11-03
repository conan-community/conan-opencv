from conans import ConanFile, CMake, tools
from conans.tools import os_info, SystemPackageTool
import os


class OpenCVConan(ConanFile):
    name = "OpenCV"
    version = "2.4.13"
    license = "LGPL"
    url = "https://github.com/memsharded/conan-opencv.git"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "cmake"

    def source(self):
        tools.download("https://github.com/Itseez/opencv/archive/2.4.13.zip", "opencv.zip")
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
  
        if pack_names:
            installer = SystemPackageTool()
            installer.update() # Update the package database
            for pack_name in pack_names:
                installer.install(pack_name) # Install the package

    def build(self):
        cmake = CMake(self.settings)
        shared = "-DBUILD_SHARED_LIBS=ON" if self.options.shared else "-DBUILD_SHARED_LIBS=OFF"
        cmake_flags = ("%s -DBUILD_EXAMPLES=OFF -DBUILD_DOCS=OFF -DBUILD_TESTS=OFF -DBUILD_opencv_apps=OFF -DBUILD_PERF_TESTS=OFF"
                        % (shared) )
        if self.settings.compiler == "Visual Studio":
            cmake_flags +=  " -DBUILD_WITH_STATIC_CRT=ON" if "MT" in str(self.settings.compiler.runtime) else " -DBUILD_WITH_STATIC_CRT=OFF"
 
        self.run('cmake opencv-%s %s %s' % (self.version, cmake_flags, cmake.command_line))
        self.run("cmake --build . %s" % cmake.build_config)

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
        version = self.version.replace(".", "") if self.settings.os == "Windows" else ""
        for lib in self.opencv_libs:
            self.cpp_info.libs.append("opencv_%s%s" % (lib, version))

        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.libs.extend(["IlmImf", "libjasper", "libjpeg", "libpng", "libtiff", "zlib"])

        if self.settings.os == "Linux":     
            if not self.options.shared:
                other_libs = self.collect_libs()
                for other_lib in ["IlmImf", "libjasper", "libjpeg", "libpng", "libtiff"]:
                    if other_lib in other_libs:
                        self.cpp_info.libs.append(other_lib)
                    else:
                        self.cpp_info.libs.append(other_lib.replace("lib", ""))

            self.cpp_info.libs.extend(["gthread-2.0", "freetype", "fontconfig", "glib-2.0", "gobject-2.0", "pango-1.0", "pangoft2-1.0", "gio-2.0", "gdk_pixbuf-2.0",
                                        "cairo", "atk-1.0", "pangocairo-1.0"," gtk-x11-2.0", "gdk-x11-2.0", "rt", "pthread", "m", "dl", "z"])
	    
                    
