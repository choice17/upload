from PIL import Image
import numpy as np
import cv2

h, w, c = img.shape
F = [1.0,1.0]
P = [0.0,0.0]
C = [int(i) for i in [w/2-40,h/2]]
x = np.linspace(0, w-1, w)
y = np.linspace(0, h-1, h)
xv, yv = np.meshgrid(x, y)
K_barrel = [[0, -1/(h*w*2), 1/((h*w)*h*2400)],
     [0, -1/(h*w*2), 1/((h*w)*h*2400)]]
K_pincushion = [[0, -1/((h*w)), 1/((h*w)*h*320)],
     [0, -1/((h*w)), 1/((h*w)*h*320)]]
K = K_barrel
z = np.dstack([xv, yv, np.ones((h, w))]).reshape([w * h , 3]).T
zx = (z[0,:] - C[0])/F[0]
zy = (z[1,:] - C[1])/F[1]
r2 = zx * zx + zy * zy
r4 = r2 * r2
zz = z.copy()
zz[0,:] = z[0,:] + zx * (K[0][0] + K[0][1] * r2 + K[0][2] * r4) + 2 * P[0] * zx * zy + P[1] * (r2 + 2 * zx *zx)
zz[1,:] = z[1,:] + zy * (K[1][0] + K[1][1] * r2 + K[1][2] * r4) + P[0] * (r2 + 2 * zy * zy) + 2 * P[1] * zx * zy
zz[0,:] = zz[0,:] * F[0]
zz[1,:] = zz[1,:] * F[1]
print("image size",h,w,c)
print("center", C)
print(zx)
print(zy)
print(zz[0,:])
print(zz[1,:])
zz = zz.astype(int)
zf = (zz.copy() + 0.5).astype(int)
mask = (zf[0,:] > w-1) | (zf[0,:] < 0) | (zf[1,:] > h-1) | (zf[1,:] < 0)
zf[0:2, mask]  = 0
img[0,0,:] = 0
tmp = img[zf[1,:],zf[0,:],:]
img_n = tmp.reshape(h, w, c)
print(K, C)
Image.fromarray(img_n).show()
