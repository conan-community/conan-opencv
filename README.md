[![Download](https://api.bintray.com/packages/conan-community/conan/opencv%3Aconan/images/download.svg)](https://bintray.com/conan-community/conan/opencv%3Aconan/_latestVersion)
[![Build status](https://ci.appveyor.com/api/projects/status/github/ConanCIintegration/conan-opencv?svg=true)](https://ci.appveyor.com/project/ConanCIintegration/conan-opencv)
[![Build Status](https://travis-ci.org/conan-community/conan-opencv.svg)](https://travis-ci.org/conan-community/conan-opencv)
# Conan OpenCV

 ![logo](logo.png)

Conan package for OpenCV library. https://opencv.org/

The packages generated with this **conanfile** can be found in [Bintray](https://bintray.com/conan-community/conan/opencv%3Aconan).

## Basic setup

    $ conan install opencv/2.4.13@conan/stable

## Project setup

If you handle multiple dependencies in your project is better to add a *conanfile.txt*

    [requires]
    opencv/2.4.13@conan/stable

    [options]
    opencv:shared=True # False
    opencv:fPIC=True # False (only available for Linux and Macos)

    [generators]
    cmake

## Issues

If you wish to report an issue for Conan Community related to this package or any other, please do so here:

[Conan Community Issues](https://github.com/conan-community/community/issues)

## Wish List

If you wish to make a request for Conan Community creating a new package, please do so here:

[Conan Wish List](https://github.com/conan-io/wishlist)


## License

[MIT](LICENSE)
