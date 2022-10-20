import numpy 
import mmap
import struct
from color import *
from math import * 

class Envmap(object):
    def __init__(self, path):
        self.path = './Envmap/' + path
        self.read()
    
    def read(self):
        with open(self.path, "rb") as image:
            image.seek(10)
            header_size = struct.unpack("=l", image.read(4))[0]
            image.seek(18)
            self.width = struct.unpack("=l", image.read(4))[0]
            self.height = struct.unpack("=l", image.read(4))[0]

            image.seek(header_size)

            self.pixels = []
            for y in range(self.height):
                self.pixels.append([])
                for x in range(self.width):
                    b = ord(image.read(1))
                    g = ord(image.read(1))
                    r = ord(image.read(1))
                    self.pixels[y].append(
                        color(r, g, b)
                    )

    def get_color(self, direction):
        direction = direction.normalize()
        x = int(((atan2(direction.z, direction.x) / (2 * pi)) + 0.5) * self.width) 
        y = int((acos(direction.y) / pi ) * self.height)

        return self.pixels[-y][x]
'''
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
'''