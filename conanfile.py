from conans import ConanFile, CMake, tools
import os
import shutil


class OpenCVConan(ConanFile):
    name = "opencv"
    version = "3.4.5"
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
               "gtk": [None, 2, 3],
               "lapack": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "contrib": False,
                       "jpeg": True,
                       "tiff": True,
                       "webp": True,
                       "png": True,
                       "jasper": True,
                       "openexr": True,
                       "gtk": None,
                       "lapack": False}
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    description = "OpenCV (Open Source Computer Vision Library) is an open source computer vision and machine " \
                  "learning software library."
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    short_paths = True
    deprecated = "opencv/3.4.12@"

    def source(self):
        tools.get("https://github.com/opencv/opencv/archive/%s.zip" % self.version)
        os.rename('opencv-%s' % self.version, self._source_subfolder)

        tools.get("https://github.com/opencv/opencv_contrib/archive/%s.zip" % self.version)
        os.rename('opencv_contrib-%s' % self.version, 'contrib')

        shutil.rmtree(os.path.join(self._source_subfolder, '3rdparty'))

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
        if self.options.lapack:
            self.requires.add('lapack/3.7.1@conan/stable')

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
        cmake.definitions["WITH_CAROTENE"] = False
        cmake.definitions['WITH_QUIRC'] = False
        cmake.definitions['WITH_LAPACK'] = self.options.lapack

        cmake.definitions['WITH_DSHOW'] = self.settings.compiler == 'Visual Studio'

        if self.options.openexr:
            cmake.definitions['OPENEXR_ROOT'] = self.deps_cpp_info['openexr'].rootpath
        if self.options.lapack:
            cmake.definitions['LAPACK_LIBRARIES'] = ';'.join(self.deps_cpp_info['lapack'].libs)
            cmake.definitions['LAPACK_LINK_LIBRARIES'] = ';'.join(self.deps_cpp_info['lapack'].lib_paths)
            cmake.definitions['LAPACK_INCLUDE_DIR'] = ';'.join(self.deps_cpp_info['lapack'].include_paths)
            cmake.definitions['LAPACK_CBLAS_H'] = 'cblas.h'
            cmake.definitions['LAPACK_LAPACKE_H'] = 'lapacke.h'
            cmake.definitions['LAPACK_IMPL'] = 'LAPACK/Generic'
        if self.options.contrib:
            # OpenCV doesn't use find_package for freetype & harfbuzz, so let's specify them
            if self.options.freetype:
                cmake.definitions['FREETYPE_FOUND'] = True
                cmake.definitions['FREETYPE_LIBRARIES'] = ';'.join(self.deps_cpp_info['freetype'].libs)
                cmake.definitions['FREETYPE_INCLUDE_DIRS'] = ';'.join(self.deps_cpp_info['freetype'].include_paths)
            if self.options.harfbuzz:
                cmake.definitions['HARFBUZZ_FOUND'] = True
                cmake.definitions['HARFBUZZ_LIBRARIES'] = ';'.join(self.deps_cpp_info['harfbuzz'].libs)
                cmake.definitions['HARFBUZZ_INCLUDE_DIRS'] = ';'.join(self.deps_cpp_info['harfbuzz'].include_paths)
            if self.options.gflags:
                cmake.definitions['GFLAGS_LIBRARY_DIR_HINTS'] = ';'.join(self.deps_cpp_info['gflags'].lib_paths)
                cmake.definitions['GFLAGS_INCLUDE_DIR_HINTS'] = ';'.join(self.deps_cpp_info['gflags'].include_paths)
            if self.options.glog:
                cmake.definitions['GLOG_LIBRARY_DIR_HINTS'] = ';'.join(self.deps_cpp_info['glog'].lib_paths)
                cmake.definitions['GLOG_INCLUDE_DIR_HINTS'] = ';'.join(self.deps_cpp_info['glog'].include_paths)

        # system libraries
        if self.settings.os == 'Linux':
            cmake.definitions['WITH_GTK'] = self.options.gtk is not None
            cmake.definitions['WITH_GTK_2_X'] = self.options.gtk == 2

        if self.options.contrib:
            cmake.definitions['OPENCV_EXTRA_MODULES_PATH'] = os.path.join(self.build_folder, 'contrib', 'modules')

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

    opencv_libs = ["stitching",
                   "superres",
                   "videostab",
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

    def package(self):
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
        suffix = 'd' if self.settings.build_type == 'Debug' and self.settings.compiler == 'Visual Studio' else ''
        version = self.version.replace(".", "") if self.settings.os == "Windows" else ""
        for lib in self.opencv_libs:
            self.cpp_info.libs.append("opencv_%s%s%s" % (lib, version, suffix))

        opencv_lib = 'lib' if self.options.shared else 'staticlib'
        opencv_arch = {'x86': 'x86',
                       'x86_64': 'x64',
                       'armv7': 'ARM',
                       'armv8': 'ARM'}.get(str(self.settings.arch), None)
        opencv_runtime = None
        if self.settings.compiler == 'Visual Studio':
            opencv_runtime = 'vc%s' % str(self.settings.compiler.version)

        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            opencv_runtime = 'mingw'

        if opencv_runtime:
            bindir = os.path.join(self.package_folder, opencv_arch, opencv_runtime, 'bin')
            libdir = os.path.join(self.package_folder, opencv_arch, opencv_runtime, opencv_lib)
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
