import cv2
import os
import numpy as np
import argparse
import time

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help="input video")
    parser.add_argument("-s", type=int, help="skip frames")
    parser.add_argument("-r", type=float, help="display ratio")
    parser.add_argument("-resize", action="store_false",help="resize")
    parser.add_argument("-crop", action="store_false",help="crop")
    parser.add_argument("-zoom", action="store_false",help="zoom")
    args = parser.parse_args()
    return args

def INFO(*args):
    print("[INFO] ", *args)

def ERR(*args):
    print("[ERROR] ", *args)

def closeAll(cap=None):
    if cap:
        cap.release()
    cv2.destroyAllWindows()

def LINE(*line):
    print("[DEUBG]", *line)

def print_video_info(cap, name=None):
    fps = cap.get(cv2.CAP_PROP_FPS)
    w, h = cap.get(3), cap.get(4)
    totalNoFrames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    durationInSeconds = float(totalNoFrames) / float(fps)
    c = int(cap.get(cv2.CAP_PROP_FOURCC))
    codec = chr(c&0xff) + chr((c>>8)&0xff) + chr((c>>16)&0xff) + chr((c>>24)&0xff) 
    
    INFO("Video name: ", name)
    INFO("Codec: ", codec)
    INFO("Resolution: H:%dx%d" % (w, h))
    INFO("Fps: ", fps)
    INFO("Total frames: ", totalNoFrames)
    INFO("Duration(s): ", durationInSeconds)
    return vid_info(name, w, h, fps, totalNoFrames, durationInSeconds, codec)

def checkVideo(fname):
    if not os.path.exists(fname):
        ERR("input video not found!")
        closeAll()
        return
    cap = cv2.VideoCapture(fname)
    if not cap.isOpened():
        ERR("Cannot open video!")
        closeAll()
    info = print_video_info(cap, fname)
    return info, cap

class vid_info(object):
    __slots__ = ('name', 'w', 'h', 'fps', 'totalNoFrames', 'durations', 'codec')

    def __init__(self, name, w, h, fps, totalNoFrames, durations, codec):
        self.name, self.w, self.h, self.fps, self.totalNoFrames, \
        self.durations, self.codec = name, w, h, fps, totalNoFrames, durations, codec

class call_back(object):
    __slots__ = ("cvWinInfo", "update", "fromPos", "to", "ti", "time_thres")

    def __init__(self):
        self.cvWinInfo = None
        self.update = 0
        self.fromPos = None
        self.to = None
        self.time_thres = 0.2
        self.ti = 0.0

    def play_cb(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.fromPos = [x, y, event, flags, param]
            self.ti = time.time()
        elif event == cv2.EVENT_LBUTTONUP:
            dur = time.time() - self.ti
            if (dur < self.time_thres):
                self.cvWinInfo = [x, y, event, flags, param]
                self.update = 1
                return    
            self.to = [x, y, event, flags, param]
            self.cvWinInfo = [self.fromPos[0] + (self.fromPos[0] -x), self.fromPos[1] + (self.fromPos[1]-y), event, flags, param]
            self.update = 2

class crop_win(object):
    __slots__ = ("w", "h", "sx", "sy", "ex", "ey", "imw", "imh",
        "center_tar_f", "dir_x", "dir_y", "center_f", "dis", "spd", "_r", "_ir", "_w", "_h")

    def __init__(self, w, h, imgw, imgh, spd):
        self.spd = 10
        self._r = float(w) / h
        self._w = self.w = w
        self._h = self.h = h
        self._ir = float(imgw) / imgh
        self.imw = imgw
        self.imh = imgh
        self.sx = int((imgw - w + 1) / 2.)
        self.sy = int((imgh - h + 1) / 2.)
        self.ex = self.sx + w - 1
        self.ey = self.sy + h - 1
        self.dis = 0
        self.center_tar_f = [0.0, 0.0]
        self.center_f = [0.0, 0.0]
        self.dir_x = 0.0
        self.dir_y = 0.0

    def _getCent(self):
        return (self.sx + self.ex) / 2., (self.sy + self.ey) / 2.

    def scale(self, r):
        center = self._getCent()
        self.w = int(self.w * r)
        self.h = int(self.h * r)
        if self._r > self._ir:
            if self.w > self.imw:
                self.w = self.imw
                self.h = int(self.imw * self._r)
        else:
            if self.h > self.imh:
                self.h = self.imh
                self.w = int(self.imh * self._r)
        self.sx = int((center[0] - (self.w + 1)/2.))
        self.ex = int(self.sx + self.w - 1)
        self.sy = int((center[1] - (self.h + 1)/2.))
        self.ey = int(self.sy + self.h - 1)
        self._withinBoundary()

    def update(self):
        if self.dis == 0:
            return
        self.center_f[0] += self.dir_x
        self.center_f[1] += self.dir_y
        self.sx = int(self.center_f[0] - (self.w + 1)/2.)
        self.ex = int(self.sx + self.w - 1)
        self.sy = int(self.center_f[1] - (self.h + 1)/2.)
        self.ey = int(self.sy + self.h - 1)
        self.dis -= self.spd
        self.dis = 0.0 if self.dis < 0.0 else self.dis
        self._withinBoundary()
        if self.dis == 0:
            self.dir_x = self.dir_y = self.dis = 0
            self.center_tar_f = [0.0, 0.0]
        

    def toPoint(self, pt, gui_w, gui_h, pt2=None):
        center = [self.w / 2., self.h / 2.]
        dx, dy = pt
        tdx, tdy = float(dx) / gui_w * self.w, float(dy) / gui_h * self.h
        if pt2 is not None:
            dx2, dy2 = pt2
            tdx2, tdy2 = float(dx2) / gui_w * self.w, float(dy2) / gui_h * self.h
            tdx, tdy = center[0] + (tdx - tdx2), center[1] + (tdy - tdy2)
        self.center_tar_f = [tdx,tdy]
        self.center_f = [float(i) for i in self._getCent()]
        difx = tdx - center[0]
        dify = tdy - center[1]
        self.dis = np.sqrt(difx ** 2 + dify**2)
        angle =  np.arctan2(difx,dify)
        self.dir_x = self.spd * np.sin(angle)
        self.dir_y = self.spd * np.cos(angle)

    def _withinBoundary(self):
        if self.sx < 0:
            self.sx = 0 if self.sx < 0 else self.sx
            self.ex = self.w - 1
        elif self.ex > self.imw - 1:
            self.sx = self.imw - self.w
            self.ex = self.imw - 1
 
        if self.sy < 0:
            self.sy = 0 if self.sy < 0 else self.sy
            self.ey = self.h - 1
        elif self.ey > self.imh - 1:
            self.sy = self.imh - self.h
            self.ey = self.imh - 1

    def move_hoz(self, val):
        self.sx += val
        self.ex += val
        if self.sx < 0:
            self.sx = 0 if self.sx < 0 else self.sx
            self.ex = self.w - 1
        elif self.ex > self.imw - 1:
            self.sx = self.imw - self.w
            self.ex = self.imw - 1
        self._stop()

    def move_ver(self, val):
        self.sy += val
        self.ey += val
        if self.sy < 0:
            self.sy = 0 if self.sy < 0 else self.sy
            self.ey = self.h - 1
        elif self.ey > self.imh - 1:
            self.sy = self.imh - self.h
            self.ey = self.imh - 1
        self._stop()

    def _stop(self):
        self.dir_x = self.dir_y = self.dis = 0
        self.center_tar_f = [0.0, 0.0]

    def __call__(self):
        return (int(self.sx), int(self.sy)), (int(self.ex), int(self.ey))

def calcFixedAspectRatio(win_dim, tar_dim):
        """
        @param: win_dim current window dim (width, height)
        @param: tar_dim target image dim (width, height)
        """
        w, h = win_dim
        tw, th = tar_dim
        if w > h:
            h_r = h ; w_r = int(h * (tw/ th))
            if w_r > w:
                h_r = int(w * (th / tw))
                w_r = w
        else: # h > w:
            w_r = w ; h_r = int(w * (th / tw))
            if h_r > h:
                h_r = h
                w_r = int(h * (tw / th))
        sz = (w_r, h_r)
        if 0 in sz:
            return 0, sz, 0, 0, 0, 0
        else:
            sx = (w >> 1) - ((w_r + 1) >> 1) ; ex = sx + w_r
            sy = (h >> 1) - ((h_r + 1) >> 1) ; ey = sy + h_r
            if sx < 0: ex -= sx ; sx = 0
            if sy < 0: ey -= sy ; sy = 0
            if ex > w: sx -= w - ex ; ex = w
            if ey > h: sy -= h - ey ; ey = h
        return 1, sz, sx, sy, ex, ey

class panel(object):
    pass

class timer_unit(object):
    __slots__ = ('ti', 'toc', 'start', 'end', 'wait')

    def __init__(self, wait_time):
        self.ti = 0
        self.toc = 0
        self.start = 0
        self.end = 0
        self.wait = wait_time

    def update(self):
        toc = time.time()
        diff = (toc - self.ti) * 1000
        wait = self.wait - diff
        wait = 1.0 if wait < 1.0 else wait
        self.ti = toc
        return int(wait)

class player(object):
    __slots__ = ('args', 'panel', 'cap', 'info')

    def __init__(self,args):
        self.args = args
        self.args
        self.panel = self.create_control_panel(args.i)

    def create_control_panel(self, name):
        cv2.namedWindow(name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(name,1280,720)
        return panel()

    def play(self, cb):
        args = self.args
        cap, info = self.cap, self.info
        is_playing = 1
        fr_cnt = 0
        if args.crop:
            info.w = int(info.w / 2)
        tar_size = [int(info.w*args.r), int(info.h*args.r)]
        if args.zoom:
            win = crop_win(info.w * args.r, info.h * args.r, info.w, info.h, 10)
            cv2.setMouseCallback(info.name, cb.play_cb)
            tar_size = [win.w, win.h]
        isResizeWin = args.resize
        skip = args.s + 1
        wait_time = 1./info.fps * skip * 1000
        skips = list(range(args.s))
        timer = timer_unit(wait_time)
        timer.update()

        while is_playing:
            ret, fr = cap.read()
            for _ in skips:
                ret, fr = cap.read()
                fr_cnt+=1
            if not ret:
                INFO("Cannot read frame %d/%d" % (fr_cnt, info.totalNoFrames))
                is_playing = 0
            if args.crop:
                fr = fr[:,:info.w,:]
            if args.zoom:
                win.update()
                st, et = win()
                fr = fr[st[1]:et[1]+1,st[0]:et[0]+1,:]
            if isResizeWin:
                try:
                    x,y,w,h = cv2.getWindowImageRect(info.name)
                except Exception as e:
                    import traceback
                    print(traceback.format_exc(), info.name)
                if (w == 0 or h == 0):
                    continue
                suc, sz, sx, sy, ex, ey = calcFixedAspectRatio([w,h],tar_size)
                if suc:
                    rfr = cv2.resize(fr, sz)
                    fr = np.zeros((h, w, 3), dtype=np.uint8)
                    fr[sy:ey, sx:ex, :] = rfr
            cv2.imshow(info.name, fr)
            wait = timer.update()
            key = cv2.waitKey(wait)
            if key == 0:
                pass
            elif key == ord('p'):
                pos = 10
                pos *= cv2.waitKey(0) - 48
                pos += cv2.waitKey(0) - 48
                pos /= 100.
                fr_cnt = int(pos * info.durations * info.fps)
                cap.set(cv2.CAP_PROP_POS_FRAMES, fr_cnt)
            elif key == ord('q'):
                is_playing = 0
            elif key == ord('k'):
                fr_cnt += int(info.fps * 20)
                cap.set(cv2.CAP_PROP_POS_FRAMES, fr_cnt)
            elif key == ord('j'):
                fr_cnt -= int(info.fps * 20)
                cap.set(cv2.CAP_PROP_POS_FRAMES, fr_cnt)
            
            if args.zoom:
                if key == ord('l'):
                   win.move_ver(-10)
                elif key == ord('.'):
                    win.move_ver(10)
                elif key == ord(','):
                    win.move_hoz(-10)
                elif key == ord('/'):
                    win.move_hoz(10)
                elif key == ord(';'):
                    win.scale(1.2)
                    tar_size = [win.w, win.h]
                elif key == ord('\''):
                    win.scale(0.8)
                    tar_size = [win.w, win.h]
                if cb.update:
                    x,y,w,h = cv2.getWindowImageRect(info.name)
                    if cb.update == 1:
                        win.toPoint(cb.cvWinInfo[0:2], w, h)
                    else:
                        win.toPoint(cb.fromPos[0:2], w, h, cb.to[0:2])
                    cb.update = 0
            fr_cnt+=1
            INFO("count", fr_cnt, info.totalNoFrames)
        return 0

    def run(self, cb):
        args = self.args
        running = 1
        while running:
            self.info, self.cap = checkVideo(args.i)
            running = 0
            running = self.play(cb)
        closeAll(self.cap)

def main():
    cb = call_back()
    player_ = player(get_args())
    player_.run(cb)

main()


