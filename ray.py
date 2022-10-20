import struct
import random
from math import pi, tan
from cube import Cube
from vector import V3
import random
from sphere import *
from material import *
from light import *
from plane import *
from envmap import *
from cube import *
from texture import *

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
    return (I - (N * 2 * (N @ I))).normalize()

def refract(I, N, roi):
    # Indice de refraccion de donde viene la luz
    etai = 1

    etat = roi

    cosi = (I @ N) * -1

    if cosi < 0:
        cosi *= -1
        etai *= -1
        etat *= -1
        N *= -1

    eta = etai / etat

    k = 1 - eta ** 2 * (1 - cosi ** 2)

    if k < 0:
        return V3(0, 0, 0)

    cost = k ** 0.5

    return ((I * eta) + (N * (eta * cosi - cost))).normalize()


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
                    j = ((2 * (y + 0.5) / self.height) - 1) * tana
                    
                    origin = V3(0, 0, 0)
                    # direction = V3(i, j, 1).normalize()
                    direction = V3(i, j, -1).normalize()
                    c = self.cast_ray(origin, direction)
                    self.point(x, y, c)

    def get_background(self, direction):
        if self.envmap:
            # return color from envmap
            return self.envmap.get_color(direction)
        
        return self.background_color

    # Encargada de retornar color final
    def cast_ray(self, origin, direction, recursion = 0):
        if recursion >= MAX_RECURSION_DEPTH:
            return self.get_background(direction)
        
        material, intersect = self.scene_intersect(origin, direction)

        if material is None:
            return self.get_background(direction)

        albedo_first_value = material.albedo[0]
        albedo_second_value = material.albedo[2]
        albedo_third_value = material.albedo[3]
        if material.textures:
            if material.diffuse.r < 250 and material.diffuse.g < 250 and material.diffuse.b < 250:
                albedo_third_value = 0
            else:
                albedo_first_value = 0

        light_dir = (self.light.position - intersect.point).normalize()
        
        # Shadow
        shadow_bias = 1.1
        shadow_orig = intersect.point + intersect.normal * shadow_bias
        shadow_material, shadow_intersect = self.scene_intersect(shadow_orig, light_dir)

        shadow_intensity = 1

        if shadow_material:
            # dentro de sombra 
            shadow_intensity = 0.5  
        
        # Diffuse intensity
        d_intensity = light_dir @ intersect.normal
        diffuse = material.diffuse * d_intensity * albedo_first_value * shadow_intensity
        
        # specular
        light_reflection = reflect(light_dir, intersect.normal)
        reflection_intensity = max(0, (light_reflection @ direction))
        spec_intensity = reflection_intensity ** material.spec
        specular = self.light.c * spec_intensity * material.albedo[1] * self.light.intensity

    
        # reflection
        reflect_color = color(0, 0, 0)
        if albedo_second_value > 0:
            reflect_dir = reflect(direction, intersect.normal)
            reflect_bias = -0.5 if reflect_dir @ intersect.normal < 0 else 0.5
            reflect_orig = intersect.point + (intersect.normal * reflect_bias)
            reflect_color = self.cast_ray(reflect_orig, reflect_dir, recursion + 1)
        
        reflection = reflect_color * albedo_second_value

        refract_color = color(0, 0, 0)
        if albedo_third_value > 0:
            refract_dir = refract(direction, intersect.normal, material.refractive_index)
            refract_bias = -0.5 if refract_dir @ intersect.normal < 0 else 0.5
            refract_orig = intersect.point + intersect.normal * refract_bias
            refract_color = self.cast_ray(refract_orig, refract_dir, recursion + 1)
        
        refraction = refract_color * albedo_third_value
        
        return (diffuse + specular + reflection + refraction)

    # Encargada de definir contra qué chocó
    def scene_intersect(self, origin, direction):
        z_buffer = 9999999
        material = None
        intersect = None
        for o in self.scene:
            object_intersect = o.ray_intersect(origin, direction)
            
            if object_intersect:
                if object_intersect.distance > 0 and object_intersect.distance < z_buffer:
                    z_buffer = object_intersect.distance
                    material = o.material
                    intersect = object_intersect
        
        if material and material.textures:
            material.texture_diffuse(intersect)

        return material, intersect

# Agua refractive_index -> 1.3

rubber = Material(diffuse=color(80, 0, 0), albedo=[0.9, 0.1, 0, 0], spec=10)
ivory = Material(diffuse=color(100, 100, 80), albedo=[0.695, 0.305, 0.1, 0], spec=50)
brown = Material(diffuse=color(139, 66, 21), albedo=[0.695, 0.305, 0, 0], spec=50)
mouth = Material(diffuse=color(249, 226, 212), albedo=[0.695, 0.305, 0, 0], spec=50)
mirror = Material(diffuse=color(255, 255, 255), albedo=[0, 1, 0.8, 0], spec=1425)
glass = Material(diffuse=color(150, 180, 200), albedo=[0, 0.5, 0.1, 0.8], spec=125, refractive_index=1.5)
cube = Material(diffuse=color(80, 0, 0), albedo=[0.9, 0.1, 0, 0], spec=10, 
    textures=[ Texture('m2.bmp') if i == 3 else Texture('m1.bmp') for i in range(6)])

cube2 = Material(diffuse=color(150, 180, 200), albedo=[1, 0.5, 0.1, 0.8], spec=125, refractive_index=1, 
    textures=[ Texture('leaves.bmp') if i == 3 else Texture('leaves.bmp') for i in range(6)])

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
    # Sphere(V3(0, 2.5, -15), 1.5, ivory),
    # Sphere(V3(0, 0, -5), 0.5, mirror),
    # Sphere(V3(-3, 2.5, -8), 1.7, rubber),
    # Sphere(V3(-2, 1, -7), 2, mirror),
    # Plane(V3(0, 2.5, -6), 2, 2, mirror),
    Cube(V3(-2, 2, -8), 1, cube2),
    Cube(V3(-2, 2, -9), 1, cube2),
    # Cube(V3(-2, -2, -8), 1, cube),
    # Cube(V3(0, 1, -10), 1, ivory)
]

# r.envmap = None
r.envmap = Envmap('./envmap.bmp')

r.render()
r.write('render.bmp')