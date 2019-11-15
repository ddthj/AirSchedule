class Vec2:
    def __init__(self,*args):
        if isinstance(args[0],Vec2):
            self.data = args[0].data[:]
        elif isinstance(args[0],list):
            self.data = args[0]
        else:
            self.data = [x for x in args]
    def __getitem__(self,key):
        return self.data[key]
    def __setitem__(self,key,value):
        self.data[key] = value
    def __str__(self):
        return str(self.data)
    def __add__(self,value):
        if isinstance(value,Vec2):
            return Vec2(self[0]+value[0], self[1]+value[1])
        else:
            return Vec2(self[0]+value, self[1]+value)
    def __sub__(self,value):
        if isinstance(value,Vec2):
            return Vec2(self[0]-value[0], self[1]-value[1])
        else:
            return Vec2(self[0]-value, self[1]-value)
    def __mul__(self,value):
        if isinstance(value,Vec2):
            return Vec2(self[0]*value[0], self[1]*value[1])
        else:
            return Vec2(self[0]*value, self[1]*value)
    __rmul = __mul__
    def __truediv__(self,value):
        if isinstance(value,Vec2):
            return Vec2(self[0]/value[0] if value[0] != 0 else 0, self[1]/value[1] if value[1] != 0 else 0)
        else:
            return Vec2(self[0]/value if value != 0 else 0, self[1]/value if value != 0 else 0)
    def render(self):
        return [int(self[0]), int(self[1])]
