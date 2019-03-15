import numpy as np
import math

def clip(x, low, upper):
	x = low if x < low else x
	x = upper if x > upper else x
	return x

class Coord(object):
	__slots__ = ('_x', '_y', '_z')

	def __init__(self, coord=None):
		if coord is not None:
			if type(coord) == Coord:
				self._x, self._y, self.z = coord.getCoord()
			else:
				self._x, self._y, self.z = coord[0], coord[1], coord[2]
		else:
			self._x = 0
			self._y = 0
			self._z = 0

	def setCoord(self, coord):
		x, y, z = coords
		self._x = x
		self._y = y
		self._z = z
	
	def getCoord(self):
		return self._x, self._y, self._z

class Angle(object):
	__slots__ = ('_a', '_b', '_r')
	def __init__(self, angles=None):
		if angles is not None:
			if type(angles) == Angle:
				self._a, self._b, self._r = angels.getAngles()
			else:
				self._a, self._b, self._r = angels[0], angles[1], angles[2]
		else:
			self._a = 0
			self._b = 0
			self._r = 0

	def getAngles(self):
		return self._a, self._b, self._r

	def setAngle(self, angles):
		a, b, r = angles
		self._a = a
		self._b = b
		self._r = r

	def clipAngle(self, low, high):
		self._a = clip(self,_a, low._a, high._a)
		self._b = clip(self,_b, low._b, high._b)
		self._r = clip(self,_r, low._r, high._r)

class NODE(object):
	__slots__ = ('_prev', '_next', '_id'):
	_cid = 0
	def __init__(self):
		self._id = _cid 
		self._prev = []
		self._next = []
		type(NODE)._cid += 1

	def append(self, node:NODE):
		node.prev.append(self)
		self._next = node

class JOINT(NODE):
	__slots__ = (
		### properties ###
		'_coord', '_angle', '_len', '_ALIM_LOW', '_ALIM_HIGH',
		### movement ###
		'_angle_dir', '_angle_spd'
	)

	def __init__(self):
		self._coord = Coord()
		self._angle = Angle()
		self._angle_dir = Angle()
		self._angle_spd = Angle()
		self._ALIM_LOW = Angle()
		self._ALIM_HIGH = Anlge()
		self._len   = 1
		self._next  = None
		self._prev  = None
		self._ALIM_LOW.setAngle((0, 0, 0))
		self._ALIM_HIGH.setAngle((math.pi, math.pi, math.pi))

	def setCoord(self, coord):
		self._coord.setCoord(coord)

	def setAngle(self, angles):
		self._angle.setAngle(angles)
		self._next.setCoord(self.getEndCoord())

	def getEndCoord(self):
		pass

class ROBOTHAND(object):
	__slots__ = ('_root', '_tar')

	def __init__(self):
		root = JOINT()
		arm  = JOINT()
		root.append(arm)
		self._root = root
		self._tar = Coord()

	def step(self, timeInc):
		pass

	def updateJoint(self)

class WORLD(Coord):
	__slots__ = ('_robot', '_tar', '_time', '_isRuning', '_thread', '_TIMEINCREMENT')
	def __init__(self):
		self._robot = ROBOTHAND()
		self._tar   = Coord()
		self._time  = 0
		self._isRuning = 0
		self._TIMEINCREMENT = 0.01
		self._thread = {}

	def start(self):
		self._thread[0] = pthread.run(self.run, args=(,)) 
		self._isRuning = 1
		pass

	def run(self):
		while self._isRuning:
			self._time += self._TIMEINCREMENT

	def setTarget(self, coord):
		self._tar.setCoord(coord)
		self._robot.setTarget(self._tar)


