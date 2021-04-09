## note

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



