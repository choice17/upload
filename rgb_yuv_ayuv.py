import numpy as np


def rgb2yuv(rgb):
	R, G, B = rgb
	Y = R * .299 + G * .587 + B * .114;
	U = R * -.169 + G * -.332 + B * .500 + 128.;
	V = R * .500 + G * -.419 + B * -.0813 + 128.;
	return Y,U,V

def yuv2ayuv(yuv):
	y, u, v = yuv
	A = 7
	Y = y * 31 * 100 / 255 / 100
	U = u * 15 * 100 / 255 / 100
	V = v * 15 * 100 / 255 / 100
	return int(A), int(Y), int(U), int(V)

def ayuv2yuv(ayuv):
	a, y, u, v = ayuv
	Y = y * 100 * 255 / 31 / 100
	U = u * 100 * 255 / 15 / 100 - 128
	V = v * 100 * 255 / 15 / 100 - 128
	return Y,U,V

def yuv2rgb(yuv):
	
	Y, U, V = yuv
	R = Y + 1.4075 * V 
	G = Y - 0.3455 * U - 0.7169 * V
	B = Y + 1.7790 * U
	'''
	Y, U, V = yuv
	Y = 1.164*(Y-16)
	R = Y + 1.596 * V 
	G = Y - 0.813 * U - 0.391 * V
	B = Y + 2.018 * U
	'''
	return int(R),int(G),int(B)

def main():
	rgb = [[255,255,255],[0,0,0],[255,0,0],[0,255,0],[0,0,255]]
	for i in rgb:
		R,G,B = i
		print(0,i)
		YUV = rgb2yuv([R,G,B])
		print(1,YUV)
		AYUV = yuv2ayuv(YUV)
		print(2,AYUV)

		YUV = ayuv2yuv(AYUV)
		print(-2,YUV)

		RGB = yuv2rgb(YUV)
		print (-1, RGB,'================')

if __name__=='__main__':
	main()



	