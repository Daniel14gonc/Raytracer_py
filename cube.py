from intersect import *
from vector import *

class Cube(object):
    def __init__(self, center, width, material):
        self.center = center
        self.width = width
        self.material = material

    def get_bounding_box(self):
        minx = self.center.x - (self.width / 2)
        maxx = self.center.x + (self.width / 2)

        miny = self.center.y - (self.width / 2)
        maxy = self.center.y + (self.width / 2)

        minz = self.center.z - (self.width / 2)
        maxz = self.center.z + (self.width / 2)

        return V3(minx, miny, minz), V3(maxx, maxy, maxz)


    def ray_intersect(self, origin, direction):
        min, max = self.get_bounding_box()

        #print(min, max)

        tmin = (min.x - origin.x) / direction.x
        tmax = (max.x - origin.x) / direction.x

        origminx = tmin
        # max.x = tmax


        if tmin > tmax:
            tmin, tmax = tmax, tmin

        tymin = (min.y - origin.y) / direction.y
        tymax = (max.y - origin.y) / direction.y

        # min.y = tymin
        # max.y = tymax

        if tymin > tymax:
            tymin, tymax = tymax, tymin

        if tmin > tymax or tymin > tmax:
            return None

        if tymin > tmin:
            tmin = tymin

        if tymax < tmax:
            tmax = tymax

        tzmin = (min.z - origin.z) / direction.z
        tzmax = (max.z - origin.z) / direction.z

        origz = tzmin
        # max.z = tzmax

        if tzmin > tzmax:
            tzmin, tzmax = tzmax, tzmin
        
        if tmin > tzmax or tzmin > tmax:
            return None

        if tzmin > tmin:
            tmin = tzmin

        if tzmax < tmax:
            tmax = tzmax

        if tmin > tmax:
            return None



        normal = None

        impact = origin + (direction * tmin)
        x, y, z = round(impact.x, 2), round(impact.y, 2), round(impact.z, 2) 
        impact = V3(x, y, z)
        
        # back
        if x >= min.x and y >= min.y and z == min.z:
            normal = V3(0, 0, -1)

        # front
        elif x >= min.x and y >= min.y and z == max.z:
            normal = V3(0, 0, 1)
        
        # bottom
        elif x >= min.x and y == min.y and z >= min.z:
            normal = V3(0, -1, 0)
        
        # top
        elif x >= min.x and y == max.y and z >= min.z:
            normal = V3(0, 1, 0)
        
        # left
        elif x == min.x and y >= min.y and z >= min.z:
            normal = V3(-1, 0, 0)

        # right
        elif x == max.x and y >= min.y and z >= min.z:
            normal = V3(1, 0, 0)
        
        return Intersect(
            distance=tmin, 
            point=impact,
            normal=normal
        )
