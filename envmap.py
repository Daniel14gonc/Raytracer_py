import numpy 
import mmap
import struct
from math import atan2, pi, acos

class color(object):
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    # Mult color con color y con float
    def __mul__(self, other):
        r = self.r
        g = self.g
        b = self.b
        if type(other) == int or type(other) == float:
            b = self.b * other
            g = self.g * other
            r = self.r * other
        else:
            b *= other.b
            g *= other.g
            r *= other.r
        
        r = int(min(255, max(r, 0)))
        g = int(min(255, max(g, 0)))
        b = int(min(255, max(b, 0)))
        return color(r, g, b)
    
    # Mult color con color y con float
    def __add__(self, other):
        r = self.r
        g = self.g
        b = self.b
        if type(other) == int or type(other) == float:
            b = self.b + other
            g = self.g + other
            r = self.r + other
        else:
            b += other.b
            g += other.g
            r += other.r
        
        r = int(min(255, max(r, 0)))
        g = int(min(255, max(g, 0)))
        b = int(min(255, max(b, 0)))
        return color(r, g, b)

class Envmap(object):
    def __init__(self, path):
        self.path = path
        self.read()
    
    def read(self):
        with open(self.path) as image:
            m = mmap(image.fileno(), 0, access = mmap.ACCESS_READ)
            ba = bytearray(m)
            header_size = struct.unpack("=l", ba[10:14][0])
            self.width = struct.unpack("=l", ba[18:22][0])
            self.height = struct.unpack("=l", ba[22:26][0])
            all_bytes = ba[header_size:]
            self.pixels = numpy.frombuffer(all_bytes, dtype="uint8")

    def get_color(self, direction):
        x = int(atan2(direction.z, direction.x) / (2 * pi) + 0.5) * self.width
        y = int(acos(-direction.y / pi) * self.height)

        index = (y * self.width + x) * 3
        c = self.pixels[index].astype(numpy.uint8)
        return color(c[2], c[1], c[0])