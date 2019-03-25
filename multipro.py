from multiprocessing import Process, Queue, Pipe
import time
import numpy as np
import signal


class Player(object):

	def __init__(self):
		self.data = np.ones((3000,2000,3),dtype=np.float)
		self.a = 0
		self.b = 0
		self.c = 0
		self.q = Queue()
		self.q2 = Queue()
		self.qK = Queue()

	def run(q, idx, ti, x, qk):
		print('enter run with ', idx)
		a = 0; b = 0;
		while qk.qsize()==0:
			if idx == 0:
				a += x
				q.put(("a is %d,"%a,a))
				time.sleep(ti)
			else:
				b += x
				q.put(("b is %d,"%b,b))
				time.sleep(ti)
		print("exit ",idx)

	def getrun(q, q2, qk):
		d = 0
		while qk.qsize()==0:
			time.sleep(1)
			if q.qsize() != 1:
				_c, c = q.get()
				print(_c, c)
				d += c
				q2.put(d)	
		print("exit, get run")

	def _handler(self, p1, p2, p3):
		def  handler(sig, frame):
			print('Got signal: ', sig)
			p1.terminate()
			p2.terminate()
			p3.terminate()
			p1.join()
			p2.join()
			p3.join()
			#self.qK.put(1)
		return handler

	def play(self):
		#parent_conn, child_conn = Pipe()
		p1 = Process(target=Player.run, args=(self.q, 0, 0.5, 1, self.qK))
		p2 = Process(target=Player.run, args=(self.q, 1, 1, 2, self.qK))
		p3 = Process(target=Player.getrun, args=(self.q, self.q2, self.qK))
		p1.daemon = True
		p2.daemon = True
		p3.daemon = True
		p1.start()
		p2.start()
		p3.start()
		a = 0
		signal.signal(signal.SIGINT, self._handler(p1, p2, p3))
		while True:
			time.sleep(1)
			a += 1
			if a == 5:
				"""method 1"""
				self.qK.put(1)
				time.sleep(0.5)
				"""method 2 force kill"""
				p1.terminate()
				p2.terminate()
				p3.terminate()
				p1.join()
				p2.join()
				p3.join()
			if a == 10:
				print(p1.is_alive())
				print(p2.is_alive())
				print(p3.is_alive())
				print(p1, p1.exitcode)
				print(p2, p2.exitcode)
				print(p3, p3.exitcode)
				break
			if self.q2.qsize() != 0:
				d = self.q2.get()
				print("d = %d" % d)



def main():
	a = Player()
	a.play
	p = Process(target=a.play)
	p.start()
	print(p.exitcode)

if __name__ == '__main__':
	main()