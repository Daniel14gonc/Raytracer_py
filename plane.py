from intersect import *
from vector import *

class Plane(object):
    def __init__(self, center, width, length, material):
        self.center = center
        self.width = width
        self.length = length
        self.material = material

    
    def ray_intersect(self, origin, direction):

        # Fraccion que hay que recorrer a donde esta el plano
        d = (self.center.y - origin.y) / direction.y
        impact = origin + (direction * d)
        normal = V3(0, -1, 0)

        if d <= 0 or impact.x > self.center.x + (self.width / 2) or impact.x < self.center.x - (self.width / 2) or impact.z > self.center.z + (self.length / 2) or impact.z < self.center.z - (self.length / 2):
            return None

        return Intersect(
            distance=d, 
            point=impact,
            normal=normal
        )
