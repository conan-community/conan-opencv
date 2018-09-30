from conans import ConanFile, CMake, tools
import os
import shutil


class OpenCVConan(ConanFile):
    name = "opencv"
    version = "3.4.3"
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
               "jasper": [True, False],
               "openexr": [True, False],
               "gtk": [None, 2, 3]}
    default_options = "shared=False",\
                      "fPIC=True",\
                      "contrib=True",\
                      "jpeg=True",\
                      "tiff=True",\
                      "webp=True",\
                      "png=True",\
                      "jasper=True",\
                      "openexr=True",\
                      "gtk=3"
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

        if self.options.contrib:
            tools.get("https://github.com/opencv/opencv_contrib/archive/%s.zip" % self.version)
            os.rename('opencv_contrib-%s' % self.version, 'contrib')

        # https://github.com/opencv/opencv/issues/8010
        if str(self.settings.compiler) == 'clang' and str(self.settings.compiler.version) == '3.9':
            tools.replace_in_file(os.path.join(self.source_subfolder, 'modules', 'imgproc', 'CMakeLists.txt'),
            'ocv_define_module(imgproc opencv_core WRAP java python js)',
            'ocv_define_module(imgproc opencv_core WRAP java python js)\n'
            'set_source_files_properties(${CMAKE_CURRENT_LIST_DIR}/src/imgwarp.cpp PROPERTIES COMPILE_FLAGS "-O0")')
        shutil.rmtree(os.path.join(self.source_subfolder, '3rdparty'))

        # allow to find conan-supplied OpenEXR
        if self.options.openexr:
            find_openexr = os.path.join(self.source_subfolder, 'cmake', 'OpenCVFindOpenEXR.cmake')
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

    def configure_cmake(self):
        cmake = CMake(self)

        cmake.definitions['CMAKE_INSTALL_LIBDIR'] = 'lib'
        cmake.definitions['CMAKE_INSTALL_BINDIR'] = 'bin'
        cmake.definitions['CMAKE_INSTALL_INCLUDEDIR'] = 'include'

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
        cmake.definitions['WITH_OPENEXR'] = self.options.openexr
        cmake.definitions['WITH_PROTOBUF'] = False
        cmake.definitions['WITH_FFMPEG'] = False

        if self.options.openexr:
            cmake.definitions['OPENEXR_ROOT'] = self.deps_cpp_info['openexr'].rootpath

        # system libraries
        if self.settings.os == 'Linux':
            cmake.definitions['WITH_GTK'] = self.options.gtk is not None
            cmake.definitions['WITH_GTK_2_X'] = self.options.gtk == 2

        if self.options.contrib:
            cmake.definitions['OPENCV_EXTRA_MODULES_PATH'] = os.path.join(self.build_folder, 'contrib', 'modules')

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

    def add_libraries_from_pc(self, library):
        pkg_config = tools.PkgConfig(library)
        libs = [lib[2:] for lib in pkg_config.libs_only_l]  # cut -l prefix
        lib_paths = [lib[2:] for lib in pkg_config.libs_only_L]  # cut -L prefix
        self.cpp_info.libs.extend(libs)
        self.cpp_info.libdirs.extend(lib_paths)
        self.cpp_info.sharedlinkflags.extend(pkg_config.libs_only_other)
        self.cpp_info.exelinkflags.extend(pkg_config.libs_only_other)

    def package_info(self):
        suffix = 'd' if self.settings.build_type == 'Debug' and self.settings.compiler == 'Visual Studio' else ''
        version = self.version.replace(".", "") if self.settings.os == "Windows" else ""
        for lib in self.opencv_libs:
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
