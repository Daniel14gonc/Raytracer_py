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