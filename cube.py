from intersect import *
from vector import *

class Cube(object):
    def __init__(self, center, width, material):
        self.center = center
        self.width = width
        self.material = material
        self.set_bounding_box()

    def set_bounding_box(self):
        minx = self.center.x - (self.width / 2)
        maxx = self.center.x + (self.width / 2)

        miny = self.center.y - (self.width / 2)
        maxy = self.center.y + (self.width / 2)

        minz = self.center.z - (self.width / 2)
        maxz = self.center.z + (self.width / 2)

        self.min = V3(minx, miny, minz)
        self.max = V3(maxx, maxy, maxz)


    def ray_intersect(self, origin, direction):
        min, max = self.min, self.max

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

        face = 0
        
        # back
        if x >= min.x and y >= min.y and z == min.z:
            face = 0
            normal = V3(0, 0, -1)

        # front
        elif x >= min.x and y >= min.y and z == max.z:
            face = 1
            normal = V3(0, 0, 1)
        
        # bottom
        elif x >= min.x and y == min.y and z >= min.z:
            face = 2
            normal = V3(0, -1, 0)
        
        # top
        elif x >= min.x and y == max.y and z >= min.z:
            face = 3
            normal = V3(0, 1, 0)
        
        # left
        elif x == min.x and y >= min.y and z >= min.z:
            face = 4
            normal = V3(-1, 0, 0)

        # right
        elif x == max.x and y >= min.y and z >= min.z:
            face = 5
            normal = V3(1, 0, 0)
        
        normalized_position = self.normal_position(impact, face)

        return Intersect(
            distance=tmin, 
            point=impact,
            normal=normal,
            face = face,
            normal_position = normalized_position
        )

    def normal_position(self, point, face):
        return self.get_position(point, face)
        
    
    def get_position(self, point, face):
        initial_horizontal, initial_vertical = self.get_box(face)
        return self.get_normal_points(point, initial_horizontal, initial_vertical, face)

    def get_normal_points(self, point, initial_horizontal, initial_vertical, face):
        x, y = self.get_points(point, face)
        x_normal = (x - initial_horizontal) / self.width
        y_normal = (y - initial_vertical) / self.width
        return abs(x_normal), abs(y_normal)

    def get_points(self, point, face):
        if face == 0 or face == 1:
            return point.x, point.y
        
        if face == 2 or face == 3:
            return point.x, point.z

        if face == 4 or face == 5:
            return point.z, point.y

    def get_box(self, face):
        if face == 0:
            return self.center.x + (self.width / 2), self.center.y - (self.width / 2)

        if face == 1:
            return self.center.x - (self.width / 2), self.center.y - (self.width / 2)
        
        if face == 2:
            return self.center.x - (self.width / 2), self.center.z - (self.width / 2)
        
        if face == 3:
            return self.center.x - (self.width / 2), self.center.z + (self.width / 2)
        
        if face == 4:
            return self.center.z - (self.width / 2), self.center.y - (self.width / 2)

        if face == 5:
            return self.center.z + (self.width / 2), self.center.y - (self.width / 2)


