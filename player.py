import subprocess as sp
import cv2
import traceback
import threading
import queue
import numpy.core as np 
import tkinter as tk
import time
class PLAYER:
	def __init__(self, url):
		self.setup(url)

	def setup(self,url):
		self.url = url
		self.scale = '1280:1024'
		self.ffmpeg_cmd = 'ffmpeg -y -v fatal -i {URL} -an -sn -c:v mjpeg -pix_fmt yuv420p -vf scale={SCALE} -f image2pipe -'.format(URL=self.url,SCALE=self.scale)
		self.is_play = True
	def play(self):
		self.create_thread()
		self.daemon_thread()
		self.play_thread()
		self.play_cvCreateWindow()
		image = None
		ti = time.time()
		while self.is_play:
				

			self.play_checkCloseWindow()
			try:
				image = self.play_getImageDecode()
				#image = self.play_parseImage(content)
			except Exception:
				print(traceback.format_exc())
				image = None

			if image is not None:
				cv2.imshow(self.url,image)
				print(1006, time.time()-ti)
				ti = time.time()	

			if cv2.waitKey(5) == ord('q'):
				self.is_play = False

	def play_getImageDecode(self):
		try:
			image = self.q[1].get(True)
		except:
			image = None
		return image

	def getDatafromPipe(self,queue_in):
		self.pipe = sp.Popen(self.ffmpeg_cmd, stdout=sp.PIPE, shell=True, bufsize=10**8)
		print(self.ffmpeg_cmd)
		buff = b''
		ti = time.time()
		while self.is_play:
					
			try:
				proc_buff = self.pipe.stdout.read(10**5)
				buff = b''.join([buff,proc_buff])
				
				while True:
					jpg_start_idx = buff.find(b'\xff\xd8')
					jpg_end_idx = buff.find(b'\xff\xd9')
					#print(1003,jpg_start_idx,jpg_end_idx,jpg_end_idx-jpg_start_idx)
					if jpg_start_idx > -1 and jpg_end_idx > -1:
						jpg_end_idx += 2
						jpg_buff = buff[jpg_start_idx:jpg_end_idx]
						buff = buff[jpg_end_idx:]
						#print(1004,jpg_buff[:5],jpg_buff[-5:])
						print(1005, time.time()-ti, queue_in.qsize())
						ti = time.time()
						queue_in.put(jpg_buff)
						
					else:
						buff = buff[jpg_start_idx:]
						break
			except Exception:
				print(traceback.format_exc())
				pass
			
			if self.pipe.poll() is not None:
				self.is_play = False

	def create_thread(self):
		self.q = [queue.Queue(),queue.Queue()]
		self.thread = {}
		self.thread[0] = threading.Thread(target=self.getDatafromPipe,args=(self.q[0],))
		self.thread[1] = threading.Thread(target=self.play_getDatafromPipe,args=(self.q[1],))

	def daemon_thread(self):
		self.thread[0].setDaemon(True)
		self.thread[1].setDaemon(True)

	def play_thread(self):
		self.thread[0].start()
		self.thread[1].start()

	def play_cvCreateWindow(self):
		cv2.namedWindow(self.url,cv2.WINDOW_NORMAL)

	def play_checkCloseWindow(self):
		if cv2.getWindowProperty(self.url,-1) != -1:
			self.is_play = False

	def play_getDatafromPipe(self,queue_in):
		while self.is_play:
			try:
				image_bytes = self.q[0].get(False)
				image = self.play_parseImage(image_bytes)
				queue_in.put(image)	
			except:
				image_bytes = None
			
		#return image_bytes

	def play_parseImage(self,image_bytes):
		if image_bytes is not None:
			image_bs = np.array(bytearray(image_bytes),dtype='uint8')
			#print(1001,image_bytes[:5],image_bytes[-5:])
			#print(1002,image_bs[:5],image_bs[-5:])
			image = cv2.imdecode(image_bs,cv2.IMREAD_COLOR)
			#print('sucess parse')
			return image
		else:
			return None


url = 'rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov'
player = PLAYER(url)
player.play()