from multiprocessing import Process, Queue, Pipe, Lock
import time
import numpy as np
import signal
"""
1. Process will copy all the args into new workspace
2. Signal Value can only be shared thru Queue, Pipe
3.a Sync through Lock
3.b Pipe.conn.poll()
3.c Queue.qsize()
4. queue add data inc the memory at the sender
5. Value Array can also share memory
6. Pipe send recv is faster than queue
"""


class Player(object):

	def __init__(self):
		self.data = np.ones((3000,1000,3),dtype=np.float)
		self.a = 0
		self.b = 0
		self.c = 0
		self.q = Queue()
		self.q2 = Queue()
		self.q3 = Queue()
		self.qK = Queue()
		self.pp, self.pc = Pipe()


	def run(q, idx, ti, x, r, l, qk):
		print('enter run with ', idx)
		a = 0; b = 0;
		while qk.qsize()==0:
			l.acquire()
			if idx == 0:
				for i in range(r):
					a += x
				q.put(("a is %d,"%a,a))
				time.sleep(ti)
			else:
				for i in range(r):
					b += x
				q.put(("b is %d,"%b,b))
				time.sleep(ti)
			l.release()
		print("exit ",idx)

	def getrun(q, q2, q3, pc, qk):
		d = 0
		iii = 3
		while qk.qsize()==0:
			time.sleep(1)
			if q.qsize() != 1:
				_c, c = q.get()
				print(_c, c)
				d += c
				q2.put(d)
			if q3.qsize() < 5:
				q3.put(np.random.randint(0,255,(2,2,2)))
			if q3.qsize() == iii:
				pc.send(np.random.randint(0,255,(1,10)))

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

	def play(self, pp):
		"""
		Process calls os.fork() and copy the whole workspace(self) to child
		if you want to use target=self.function
		Use it with care
		"""
		l = Lock()
		p1 = Process(target=Player.run, args=(self.q, 0, 0.5, 1, 5, l, self.qK))
		p2 = Process(target=Player.run, args=(self.q, 1, 1, 2, 5, l, self.qK))
		p3 = Process(target=Player.getrun, args=(self.q, self.q2, self.q3, self.pc, self.qK))
		p1.daemon = True
		p2.daemon = True
		p3.daemon = True
		p1.start()
		p2.start()
		p3.start()
		a = 0
		signal.signal(signal.SIGINT, self._handler(p1, p2, p3))
		time.sleep(1)
		while True:
			if self.pp.poll():
			#if ll.acquire(timeout=0.1):
				print(a, self.pp.recv())
			else:
				time.sleep(1)
			print('loop a',a)
			a += 1
			if a == 15:
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
			if a > 20:
				print(p1.is_alive())
				print(p2.is_alive())
				print(p3.is_alive())
				print(p1, p1.exitcode)
				print(p2, p2.exitcode)
				print(p3, p3.exitcode)
				break
			if self.q2.qsize() != 0:
				d = self.q2.get()
				print("d = ", d)
			if self.q3.qsize() == 5:
				print('clean up q3')
				e = self.q3.get()
				e += self.q3.get()
				e += self.q3.get()
				e += self.q3.get()
				print(np.sum(e[:]))
		self.pp.close()
		self.pc.close()
		pp.send(1)
		print("[INFO] EXIT loop")
				


def main():
	a = Player()
	a.play
	pp, pc = Pipe()
	p = Process(target=a.play, args=(pc,))
	p.start()
	while not pp.poll():
		time.sleep(1)
	p.join()
	print("[EXIT]", p.exitcode)

if __name__ == '__main__':
	main()