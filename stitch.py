import cv2
import os
import argparse
import numpy as np

def info(*args):
	print("[INFO] ", *args)

def openVideo(video, type="r", fps=30, fourcc="XVID", resoln=(1920,1080)):
	if type == "w":
		info(f"Open videwriter:{video} with {resoln}")
		return cv2.VideoWriter(video, cv2.VideoWriter_fourcc(*fourcc), fps, resoln)
	else:
		return cv2.VideoCapture(video)

def stitch(vids, dst, opt):
	resize_rate = opt.rate
	mks = opt.marker
	lh, lw = opt.layout
	i = 0
	bg = (25,25,25)
	fg = (175,225,175)
	frs, frNr = [None for _ in vids], [None for _ in vids]

	totalNoFrames = int(vids[0].get(cv2.CAP_PROP_FRAME_COUNT))
	iw, ih = vids[0].get(3), vids[0].get(4)
	dw, dh = int(iw * resize_rate), int(ih * resize_rate)
	sx, sy, ex, ey = 0, dh-40, 150, dh
	polygons = np.array([[[sx, sy], [ex, sy], [ex, ey], [sx, ey]]])

	layout = np.zeros((lh*dh,lw*dw,3),dtype=np.uint8)
	layout_index = [(li,lj) for li in range(lh) for lj in range(lw)]
	#code = compile(f"layout[{lh_st}:{lh_ed},{lw_st}:{lw_ed},:] = frir",'sumstring','exec')

	while True:
		fi = 0
		for vid in vids:
			ret, frs[fi] = vid.read()
			if not ret:
				fi = -1
				break
			fi += 1
		if fi < 0: break
		info(f"Progress {i+1}/{totalNoFrames}")
		frNr = [cv2.resize(fi, (dw, dh)) for fi in frs]
		fi = 0
		for frir, mk in zip(frNr, mks):
			cv2.fillPoly(frir, polygons, bg, 1)
			cv2.putText(frir, mk, (2, dh-5), 1, 3, fg, 3)
			li, lj = layout_index[fi]
			lh_st, lh_ed = li*dh, li*dh+dh
			lw_st, lw_ed = lj*dw, lj*dw+dw
			#print(f"layout[{lh_st}:{lh_ed},{lw_st}:{lw_ed},:] = frir {li,lj}")
			layout[lh_st:lh_ed,lw_st:lw_ed,:] = frir
			fi +=1
		dst.write(layout)
		i += 1
	for vid in vids:
		vid.release()
	dst.release()

def main(args):
	print(f"{args}")
	vidnames = args.src if isinstance(args.src, list) else [args.src]
	assert len(vidnames) >= 2
	assert len(vidnames) == len(args.marker)
	assert args.layout[0]*args.layout[1] >= len(vidnames)

	for vidname in vidnames:
		assert os.path.exists(vidname)
	vids = [openVideo(v) for v in vidnames]

	fps0 = float(vids[0].get(cv2.CAP_PROP_FPS))
	w0, h0 = vids[0].get(3), vids[0].get(4)

	for vid in vids:
		fps = vid.get(cv2.CAP_PROP_FPS)
		w1, h1 = vid.get(3), vid.get(4)
		assert fps0 == fps
		assert w0 == w1
		assert h0 == h1

	dstname = args.dst
	rate = args.rate
	dw, dh = int(rate*w0), int(rate*h0)
	lh, lw = args.layout

	info(f"fps {fps0} WxH {w0} {h0}")
	info(f"target WxH {dw}x{dh} ===> {lh*dh}x{lw*dw}")
	cap = openVideo(dstname, "w", fps0, fourcc="XVID", resoln=(lw*dw,lh*dh))
	stitch(vids, cap, args)
	info(f"video is saved at {dstname}!")

def get_args():
  parser = argparse.ArgumentParser()
  parser.add_argument("-src", type=str, nargs='+', help="array for input video source")
  parser.add_argument("-dst")
  parser.add_argument("-rate", type=float)
  parser.add_argument("-layout", type=int, default=[1,2], nargs='+', help="video stitch layout HxW")
  parser.add_argument("-marker", type=str, nargs='+')


if __name__ == '__main__':
  args = get_args()
  main(args)


