import struct
import random
from math import pi, tan
from vector import V3
import random
from sphere import *
from material import *
from light import *

def char(c):
    # 1 byte
    return struct.pack('=c', c.encode('ascii'))

def word(w):
    # 2 bytes
    return struct.pack('=h', w)

def dword(d):
    # 4 bytes
    return struct.pack('=l', d)

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
        

    def to_bytes(self):
        return bytes([self.b, self.g, self.r])

    def __repr__(self):
        return "color(%s, %s, %s" % (self.r, self.g, self.b)


class Raytracer(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.background_color = color(0, 0, 0).to_bytes()
        self.current_color = color(255, 255, 255).to_bytes()
        self.density = 1
        self.scene = []
        self.light = Light(V3(0, 0, 0), 1)
        self.clear()

    def clear(self):
        self.framebuffer = [
            [self.background_color for x in range(self.width)]
            for y in range(self.height)
        ]

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

    def point(self, x, y, c=None):
        if y >= 0 and y < self.height and x >= 0 and x < self.width:
            self.framebuffer[y][x] = c if c!= None else self.current_color


    def render(self):
        fov = int(pi/2)
        ar = self.width / self.height
        tana = tan(fov / 2)
        print(tana)
        for y in range(self.height):
            for x in range(self.width):    
                r = random.uniform(0, 1)
                if r < self.density:
                    i = ((2 * (x + 0.5) / self.width) - 1) * ar * tana
                    j = (1 - (2 * (y + 0.5) / self.height)) * tana
                    
                    origin = V3(0, 0, 0)
                    direction = V3(i, j, -1).normalize()
                    c = self.cast_ray(origin, direction)
                    self.point(x, y, c)
                

    # Encargada de retornar color final
    def cast_ray(self, origin, direction):
        material, intersect = self.scene_intersect(origin, direction)

        if material is None:
            return self.background_color
        ligth_dir = (self.light.position - intersect.point).normalize()
        intensity = ligth_dir @ intersect.normal
        color = material.diffuse * intensity
        
        return color.to_bytes()

    # Encargada de definir contra qué chocó
    def scene_intersect(self, origin, direction):
        z_buffer = 99999
        material = None
        intersect = None
        for o in self.scene:
            object_intersect = o.ray_intersect(origin, direction)
            
            if object_intersect:
                if object_intersect.distance < z_buffer:
                    z_buffer = object_intersect.distance
                    material = o.material
                    intersect = object_intersect
        
        return material, intersect

red = Material(diffuse=color(255, 0, 0))
white = Material(diffuse=color(255, 255, 255))

r = Raytracer(800, 600)
r.light = Light(V3(0, 0, 0), 1)
r.scene = [
    Sphere(V3(2, 0, -16), 2, red),
    Sphere(V3(-2.8, 0, -10), 2, white)
]
r.render()
r.write('render.bmp')