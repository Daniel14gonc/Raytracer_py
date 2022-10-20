import struct
from color import *
class Texture:
    
    def __init__(self,path):
        self.path= './Textures/' + path
        self.width=0
        self.heigth=0
        self.read()
    
    def read(self):
        with open(self.path,"rb") as image:
            image.seek(10)
            header_size = struct.unpack("=l",image.read(4))[0]
            image.seek(18)
            self.width = struct.unpack("=l",image.read(4))[0]
            self.heigth = struct.unpack("=l",image.read(4))[0]
            image.seek(header_size)
            self.pixels=[]
            
            for y in range(self.heigth):
                self.pixels.append([])
                for x in range(self.width):
                    b= ord(image.read(1))
                    g= ord(image.read(1))
                    r= ord(image.read(1))
                    
                    self.pixels[y].append(color(r,g,b))
            
    def get_color(self,tx,ty):
        x=round(tx*(self.width-1))
        y=round(ty*(self.heigth-1))
        
        return self.pixels[y][x]