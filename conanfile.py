from conans import ConanFile, CMake, tools
from conans.tools import os_info, SystemPackageTool
import os


class OpenCVConan(ConanFile):
    name = "opencv"
    version = "3.4.2"
    license = "LGPL"
    homepage = "https://github.com/opencv/opencv"
    url = "https://github.com/conan-community/conan-opencv.git"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "contrib": [True, False],
               "jpeg": [True, False],
               "tiff": [True, False],
               "webp": [True, False],
               "png": [True, False],
               "jasper": [True, False]}
    default_options = "shared=False",\
                      "fPIC=True",\
                      "contrib=False",\
                      "jpeg=True",\
                      "tiff=True",\
                      "webp=True",\
                      "png=True",\
                      "jasper=True"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    description = "OpenCV (Open Source Computer Vision Library) is an open source computer vision and machine " \
                  "learning software library."
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"
    short_paths = True

    def source(self):
        tools.get("https://github.com/opencv/opencv/archive/%s.zip" % self.version)
        os.rename('opencv-%s' % self.version, self.source_subfolder)

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def system_requirements(self):
        if os_info.linux_distro == "ubuntu":
            installer = SystemPackageTool()
            installer.update() # Update the package database
            for pack_name in ("libgtk2.0-dev", "pkg-config", "libpango1.0-dev", "libcairo2-dev",
                              "libglib2.0-dev "):
                installer.install(pack_name) # Install the package

    def requirements(self):
        self.requires.add('zlib/1.2.11@conan/stable')
        if self.options.jpeg:
            self.requires.add('libjpeg-turbo/1.5.2@bincrafters/stable')
        if self.options.tiff:
            self.requires.add('libtiff/4.0.9@bincrafters/stable')
        if self.options.webp:
            self.requires.add('libwebp/1.0.0@bincrafters/stable')
        if self.options.png:
            self.requires.add('libpng/1.6.34@bincrafters/stable')
        if self.options.jasper:
            self.requires.add('jasper/2.0.14@conan/stable')

    def configure_cmake(self):
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
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
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

        cmake.configure(build_folder=self.build_subfolder)
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    opencv_libs = ["stitching",
                   "superres",
                   "videostab",
                   "photo",
                   "objdetect",
                   "video",
                   "ml",
                   "calib3d",
                   "features2d",
                   "imgcodecs",
                   "videoio",
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

        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.libs.extend(["IlmImf"])

        if self.settings.compiler == 'Visual Studio':
            arch = {'x86': 'x86',
                    'x86_64': 'x64'}.get(str(self.settings.arch))
            vc = 'vc%s' % str(self.settings.compiler.version)
            bindir = os.path.join(self.package_folder, arch, vc, 'bin')
            libdir = os.path.join(self.package_folder, arch, vc, 'lib' if self.options.shared else 'staticlib')
            self.cpp_info.bindirs.append(bindir)
            self.cpp_info.libdirs.append(libdir)

        if self.settings.os == "Linux":     
            if not self.options.shared:
                other_libs = self.collect_libs()
                for other_lib in ["IlmImf"]:
                    if other_lib in other_libs:
                        self.cpp_info.libs.append(other_lib)
                    else:
                        self.cpp_info.libs.append(other_lib.replace("lib", ""))

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
                                       "gtk-x11-2.0",
                                       "gdk-x11-2.0",
                                       "rt",
                                       "pthread",
                                       "m",
                                       "dl"])
