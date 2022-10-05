import struct
import random
from math import pi, tan
from vector import V3
import random
from sphere import *
from material import *
from light import *

MAX_RECURSION_DEPTH = 3

def char(c):
    # 1 byte
    return struct.pack('=c', c.encode('ascii'))

def word(w):
    # 2 bytes
    return struct.pack('=h', w)

def dword(d):
    # 4 bytes
    return struct.pack('=l', d)

def reflect(I, N):
    return (I - N * 2 * (N @ I)).normalize()

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


    def to_bytes(self):
        return bytes([self.b, self.g, self.r])

    def __repr__(self):
        return "color(%s, %s, %s" % (self.r, self.g, self.b)


class Raytracer(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.background_color = color(0, 0, 100)
        self.current_color = color(255, 255, 255)
        self.density = 1
        self.scene = []
        self.light = Light(V3(0, 0, 0), 2, color(255, 255, 255))
        self.clear()

    def clear(self):
        self.framebuffer = [
            [self.background_color.to_bytes() for x in range(self.width)]
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
            self.framebuffer[y][x] = c.to_bytes() if c!= None else self.current_color.to_bytes()

    def render(self):
        fov = int(pi/2)
        ar = self.width / self.height
        tana = tan(fov / 2)
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
    def cast_ray(self, origin, direction, recursion = 0):
        if recursion >= MAX_RECURSION_DEPTH:
            return self.background_color
        
        material, intersect = self.scene_intersect(origin, direction)

        if material is None:
            return self.background_color
        light_dir = (self.light.position - intersect.point).normalize()

        # reflection
        reflect_color = color(0, 0, 0)
        if material.albedo[2] > 0:
            reverse_direction = direction * -1
            reflect_dir = reflect(reverse_direction, intersect.normal)
            reflect_bias = -0.5 if reflect_dir @ intersect.normal <     0 else 0.5
            reflect_orig = intersect.point + intersect.normal * reflect_bias
            reflect_color = self.cast_ray(reflect_orig, reflect_dir, recursion + 1)
        
        reflection = reflect_color * material.albedo[2]

        shadow_bias = 1.1
        shadow_orig = intersect.point + intersect.normal * shadow_bias
        shadow_material, shadow_intersect = self.scene_intersect(shadow_orig, light_dir)
        shadow_intensity = 1

        if shadow_material:
            # dentro de sombra 
            shadow_intensity = 0.5  
        # Diffuse intensity
        d_intensity = light_dir @ intersect.normal
        diffuse = material.diffuse * d_intensity * material.albedo[0] * shadow_intensity
        # print(intersect.normal)
        # specular
        light_reflection = reflect(light_dir, intersect.normal)
        reflection_intensity = max(0, (light_reflection @ direction))
        spec_intensity = reflection_intensity ** material.spec
        specular = self.light.c * spec_intensity * material.albedo[1] * self.light.intensity

        
        
        return (diffuse + specular + reflection)

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

rubber = Material(diffuse=color(80, 0, 0), albedo=[0.9, 0.1, 0], spec=10)
ivory = Material(diffuse=color(100, 100, 80), albedo=[0.695, 0.305, 0], spec=50)
brown = Material(diffuse=color(139, 66, 21), albedo=[0.695, 0.305], spec=50)
mouth = Material(diffuse=color(249, 226, 212), albedo=[0.695, 0.305], spec=50)
mirror = Material(diffuse=color(255, 255, 255), albedo=[0, 1, 0.8], spec=1425)

r = Raytracer(800, 600)
# r.light = Light(V3(0, 0, 0), 1, color(255, 255, 255))
'''
r.scene = [
    Sphere(V3(0, 1, -10), 2, brown),
    Sphere(V3(0, -2.1, -10), 1.3, brown),
    Sphere(V3(-1.6, -5.5, -16), 0.9, brown),
    Sphere(V3(1.6, -5.5, -16), 0.9, brown),
    Sphere(V3(-3.1, -0.7, -16), 1.2, brown),
    Sphere(V3(3.1, -0.7, -16), 1.2, brown),
    Sphere(V3(-3.1, 4, -16), 1.2, brown),
    Sphere(V3(3.1, 4, -16), 1.2, brown),
    Sphere(V3(0, -0.9, -5), 0.3, mouth),
]
'''
r.light = Light(V3(-20, 20, 20), 2, color(255, 255, 255))
r.scene = [
    Sphere(V3(0, -1.5, -12), 1.5, ivory),
    # Sphere(V3(-2, -1, -12), 2, mirror),
    Sphere(V3(1, 1, -8), 1.7, rubber),
    Sphere(V3(-2, 1, -10), 2, mirror),
]
r.render()
r.write('render.bmp')