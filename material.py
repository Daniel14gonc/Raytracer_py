class Material:
    def __init__(self, diffuse, albedo, spec, refractive_index = 0, textures = None):
        self.diffuse = diffuse
        self.albedo = albedo
        self.spec = spec
        self.refractive_index = refractive_index
        self.textures = textures

    def texture_diffuse(self, intersect):
        self.setColor(intersect)


    def setColor(self, intersect):
        face = intersect.face
        texture = self.textures[face]
        x, y = intersect.normal_position
        self.diffuse = texture.get_color(x, y)