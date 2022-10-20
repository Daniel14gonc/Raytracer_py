class Intersect:
    def __init__(self, distance, point, normal, face = None, normal_position = None):
        self.distance = distance
        self.point = point
        self.normal = normal
        self.face = face
        self.normal_position = normal_position