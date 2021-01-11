## Package Deprecation Notice

[CCI](https://github.com/conan-io/conan-center-index) has taken ownership of the public Conan package for this library, which can be found at the following links:

https://github.com/conan-io/conan-center-index/
https://conan.io/center/opencv

Bincrafters will keep this version of the package on Github and Bintray, however it will no longer be maintained or supported.
Users are advised to update their projects to use the official Conan package maintained by the library author immediately.


[![Download](https://api.bintray.com/packages/conan-community/conan/opencv%3Aconan/images/download.svg) ](https://bintray.com/conan-community/conan/opencv%3Aconan/_latestVersion)
[![Build Status Travis](https://travis-ci.org/conan-community/conan-opencv.svg)](https://travis-ci.org/conan-community/conan-opencv)
[![Build Status AppVeyor](https://ci.appveyor.com/api/projects/status/github/conan-community/conan-opencv?svg=true)](https://ci.appveyor.com/project/ConanCIintegration/conan-opencv)

## Conan package recipe for [*opencv*](https://github.com/opencv/opencv)

OpenCV (Open Source Computer Vision Library) is an open source computer vision and machine learning software library.

The packages generated with this **conanfile** can be found on [Bintray](https://bintray.com/conan-community/conan/opencv%3Aconan).


## Issues

If you wish to report an issue or make a request for a package, please do so here:

[Issues Tracker](https://github.com/conan-community/community/issues)


## For Users

### Basic setup

    $ conan install opencv/4.3.0@conan/stable

### Project setup

If you handle multiple dependencies in your project is better to add a *conanfile.txt*

    [requires]
    opencv/4.3.0@conan/stable

    [generators]
    cmake

Complete the installation of requirements for your project running:

    $ mkdir build && cd build && conan install ..

Note: It is recommended that you run conan install from a build directory and not the root of the project directory.  This is because conan generates *conanbuildinfo* files specific to a single build configuration which by default comes from an autodetected default profile located in ~/.conan/profiles/default .  If you pass different build configuration options to conan install, it will generate different *conanbuildinfo* files.  Thus, they should not be added to the root of the project, nor committed to git.


## Build and package

The following command both runs all the steps of the conan file, and publishes the package to the local system cache.  This includes downloading dependencies from "build_requires" and "requires" , and then running the build() method.

    $ conan create . conan/stable


### Available Options
| Option        | Default | Possible Values  | Description |
| ------------- |:----------------- |:------------:| ----- |
| shared      | False |  [True, False] | Build shared libraries only |
| fPIC      | True |  [True, False] | Compile with -fPIC (Linux only) |
| contrib      | False |  [True, False] | Build OpenCV contrib from sources |
| jpeg      | True |  [True, False] | Build with libjpeg |
| jpegturbo | False |  [True, False] | Build with libjpeg-turbo |
| tiff      | True |  [True, False] | Build with libtiff |
| webp      | True |  [True, False] | Build with libwebp |
| png      | True |  [True, False] | Build with libpng |
| jpeg2000      | "openjpeg" |  ["jasper", "openjpeg", None] | Build with openjpeg / jasper / without jpeg support |
| openexr      | True |  [True, False] | Build with openexr |
| gtk      | None |  [None, 2, 3] | Build with system GTK-2.0 or GTK-3 |
| nonfree | False | [True, False] | Include non-free features in the build. This is required to use patented algorithms such as SIFT, SURF or KinectFusion. |
| dc1394      | True |  [True, False] | Build with DC1394 (DCAM) |
| carotene      | False |  [True, False] | Use NVidia carotene acceleration library for ARM platform |
| cuda      | False |  [True, False] | Include NVidia Cuda Runtime support |
| protobuf      | True |  [True, False] | Build with libprotobuf |
| freetype      | True |  [True, False] | Build with freetype |
| harfbuzz      | True |  [True, False] | Build with harfbuzz |
| eigen      | True |  [True, False] | Include Eigen2/Eigen3 support |
| glog      | True |  [True, False] | Build with glog |
| gflags      | True |  [True, False] | Build with gflags |
| gstreamer      | False |  [True, False] | Include Gstreamer support |
| openblas      | False |  [True, False] | Build with openblas |
| ffmpeg      | False |  [True, False] | Build with ffmpeg |
| lapack      | False |  [True, False] | Build with lapack |
| quirc       | True |  [True, False] | Build with QR-code decoding library |


## Add Remote

Conan Community has its own Bintray repository, however, we are working to distribute all package in the Conan Center:

    $ conan remote add conan-center "https://conan.bintray.com"


## Conan Recipe License

NOTE: The conan recipe license applies only to the files of this recipe, which can be used to build and package opencv.
It does *not* in any way apply or is related to the actual software being packaged.

[MIT](LICENSE)
