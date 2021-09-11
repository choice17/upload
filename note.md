## note

* 2021/9/11

L1 norm encourages sparsity and L2 norm push weights to zero.

https://www.kaggle.com/residentmario/l1-norms-versus-l2-norms
https://stats.stackexchange.com/questions/45643/why-l1-norm-for-sparse-models

* 2021/9/11

tflite micro has better performance on memory usage/ library package size
tflite has better control on speed
tflite package size can be reduced by comment out unused ops. and other datatype.

* 2021/5/11

@ build from source opencv with ffmpeg in linux  
ref : https://stackoverflow.com/questions/12427928/configure-and-build-opencv-to-custom-ffmpeg-install
```
// modify ffmpeg cmake in opencv
diff --git a/cmake/OpenCVFindLibsVideo.cmake b/cmake/OpenCVFindLibsVideo.cmake
index 13b62ac..bab9df3 100644
--- a/cmake/OpenCVFindLibsVideo.cmake
+++ b/cmake/OpenCVFindLibsVideo.cmake
@@ -228,6 +228,12 @@ if(WITH_FFMPEG)
     if(FFMPEG_libavresample_FOUND)
       ocv_append_build_options(FFMPEG FFMPEG_libavresample)
     endif()
+   CHECK_MODULE(libavcodec HAVE_FFMPEG)
+   CHECK_MODULE(libavformat HAVE_FFMPEG)
+   CHECK_MODULE(libavutil HAVE_FFMPEG)
+   CHECK_MODULE(libswscale HAVE_FFMPEG)
+   CHECK_MODULE(libswresample HAVE_FFMPEG)
+   CHECK_MODULE(libavresample HAVE_FFMPEG)
     if(HAVE_FFMPEG)
       try_compile(__VALID_FFMPEG
           "${OpenCV_BINARY_DIR}"

#!/bin/bash
// export ld library path and pkgconfig path
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/Applications/ffmpeg/lib
export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:$HOME/Applications/ffmpeg/lib/pkgconfig
export PKG_CONFIG_LIBDIR=$PKG_CONFIG_LIBDIR:$HOME/Applications/ffmpeg/lib

// cmake opencv
cmake \
    -D BUILD_EXAMPLES=ON \
    -D BUILD_TESTS=OFF \
    -D OPENCV_EXTRA_EXE_LINKER_FLAGS="-Wl,-rpath,$HOME/Applications/ffmpeg/lib" \
    -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=$HOME/Applications/opencv \
    /path/to/opencv

// configure ffmpeg 
cd ./ffmpeg_src
./configure --enable-avresample --prefix=$(pwd)/linux_install --disable-doc --pkgconfigdir=$(pwd)/linux_install/lib/pkgconfig --enable-shared --enable-avresample
```




* 2021/4/9

@ mouse control in python
@ win32api
```
import win32api
import time
import math

for i in range(500):
    x = int(500+math.sin(math.pi*i/100)*500)
    y = int(500+math.cos(i)*100)
    win32api.SetCursorPos((x,y))
    time.sleep(.01)
A click using ctypes:
```

@ ctypes
```
import ctypes

# see http://msdn.microsoft.com/en-us/library/ms646260(VS.85).aspx for details
ctypes.windll.user32.SetCursorPos(100, 20)
ctypes.windll.user32.mouse_event(2, 0, 0, 0,0) # left down
ctypes.windll.user32.mouse_event(4, 0, 0, 0,0) # left up
```

@ get screen resolution
```
from win32api import GetSystemMetrics
print("Width =", GetSystemMetrics(0))
print("Height =", GetSystemMetrics(1))
```

* 2021/4/7

@ assembly in c
1. https://gcc.gnu.org/onlinedocs/gcc/Extended-Asm.html
2. http://ibiblio.org/gferg/ldp/GCC-Inline-Assembly-HOWTO.html

@ model pruning
1. Pruning through channel-wise sparsity-induced regularization https://openaccess.thecvf.com/content_ICCV_2017/papers/Liu_Learning_Efficient_Convolutional_ICCV_2017_paper.pdf
implementation code ref.
https://github.com/EstherBear/implementation-of-network-slimming/blob/master/prune/resnetprune.py#L21
2. Pruning through variance-aware cross-layer regularization (For ResNet)
https://arxiv.org/pdf/1909.04485.pdf
3. RepVgg refactor parameter after training
https://arxiv.org/abs/2101.03697

* 2021/4/5  

@ hdmi to sunview - cropped (overscan option)  
fix (not work for me though)  
-> Zoom : turn off overscan  
-> HDMI true black : On

* 2021/3/11

@ fddb-evaluation kit  
score = area(det) AND area(label) / area(det) union area(label)  
continuous score = summation i->N ( score_i )  
discrete score = summation i->N ( score_i > 0.5 )  



