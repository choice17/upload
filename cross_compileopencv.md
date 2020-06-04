## install cross compiler 

## Download opencv 

```
cd ~/workspace/
$ wget https://github.com/Itseez/opencv/archive/3.4.2.zip
$ unzip 3.4.2.zip
$ cd opencv-3.4.2
$ sudo mkdir -p /usr/local/arm-opencv
```

## Configure with CMAKE-GUI

```
$ sudo apt-get install cmake-qt-gui 
$ sudo cmake-gui
```

source dir  
`source: /home/{usename}/workspace/opencv-3.4.2`  

build path  
`binaries path: /usr/local/arm-opencv`  

click configure

Setup configure options  
```
Operation system : arm-multitek-linux
Processor : arm
Compiler :
C: {CROSSCOMPILER}gcc
CXX: {CROSSCOMPILER}g++
target root: {CROSSCOMPILER}sysroot should  contain include / lib
```

Select  
```
BUILD_JASPER,
BUILD_JPEG,
BUILD_ZLLIB,
BUILD_WITH_DEBUG_INFO, 
BUILD_opencv_world  (build into a big lib)]
```

Unselect
```
BUILD_DOCS,
BUILD_PERF_TESTS
BUILD_TESTS,
BUILD_FAT_JAVA_LIB,
BUIlD_openvc_app
BUILD_SHARED_LIBS,
WITH_CUDA
WITH_PNG,
WITH_TIFF,
WITH_WEBP
```

Add install prefix
```
CMAKE_INSTALL_PREFIX = /usr/local/opencv
```

```
check for 
/usr/local/arm-opencv/3rdparty/openexr/IlmBaseConfig.h
```
`#define HAVE_PTHREAD 0` to `#define HAVE_PTHREAD 1`  

```
$ cd /usr/local/arm-opencv
$ sudo make
$ sudo make install
$ sudo cp /usr/local/arm-opencv/3rdparty/lib/* /usr/local/opencv/lib/
```

```
qemu-arm -L {CROSS_COMPILE_ROOT} demo_tf
```


