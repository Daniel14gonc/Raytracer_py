import struct
import random
from vector import *

#Write utils
def char(c):
	# 1 byte
	return struct.pack('=c', c.encode('ascii'))

def word(w):
	# 2 bytes
	return struct.pack('=h', w)

def dword(d):
	# 4 bytes
	return struct.pack('=l', d)

def color(r, g, b):
	return bytes([b, g, r])

BLACK = color(0, 0, 0)
WHITE = color(255, 255, 255)

#importar esta clase en gllib
class Render(object):
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.clear()

	def clear(self):
		self.framebuffer = [
			[BLACK for x in range(self.width)]
			for y in range(self.height)
		]

		self.zBuffer = [
			[-9999 for x in range(self.width)]
			for y in range(self.height)
		]
		print(len(self.zBuffer[0]), "len")

	#no se necesita nombre al escribir a memoria de video
	def write(self, filename):
		f = open(filename, 'bw')

		# pixel header
		f.write(char('B'))
		f.write(char('M'))

		# file size 
		f.write(dword(14 + 40 + self.width * self.height * 3))

		f.write(word(0))
		f.write(word(0))

		f.write(dword(14 + 40))

		# info header
		f.write(dword(40))
		f.write(dword(self.width))
		f.write(dword(self.height))
		f.write(word(1))
		# true color
		f.write(word(24))
		f.write(dword(0))
		f.write(dword(self.width * self.height * 3))
		f.write(dword(0))
		f.write(dword(0))
		f.write(dword(0))
		f.write(dword(0))

		# pixel data

		for x in range (self.height):
			for y in range(self.width):
				f.write(self.framebuffer[x][y])

		f.close()

	def point(self, x, y):
		if (0 < x < self.width and 0 < y < self.height):
			self.framebuffer[x][y] = WHITE

	def set_current_color(self, c):
		self.current_color = c

# clase vector
