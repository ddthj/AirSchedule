import pygame
from vector import Vec2
#converts from m into hh:mm
def string_time(time):
    hours = time // 60 * 100
    minutes = time % 60
    return "{:04d}".format(hours+minutes)

#Box elements are the building blocks of the gui
class box:
    def __init__(self,parent,**kwargs):
        #sets render layer, higher layers render on top of lower layers
        self.layer = kwargs.get("layer",parent.layer+1) if parent != None else kwargs.get("layer", 0)
        #Where the box sits relative to the parent, center, top, bottom, left, right
        self.align = kwargs.get("align","center")
        #offset from alignment, aka padding
        self.offset = Vec2(kwargs.get("offset",(0,0)))
        self.size = Vec2()
