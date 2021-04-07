## note

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



