import pygame
from vector import Vec2
#converts from m into hh:mm
def string_time(time):
    hours = time // 60 * 100
    minutes = time % 60
    return "{:04d}".format(hours+minutes)

#Box elements are the building blocks of the gui, they can either be boxes with/without fill or text
class element:
    def __init__(self,parent=None,**kwargs):
        #sets render layer, higher layers render on top of lower layers
        self.layer = kwargs.get("layer",parent.layer+1) if parent != None else kwargs.get("layer", 0)
        #color of the element
        self.color = kwargs.get("color", [0, 0, 0])
        #Where the box sits relative to the parent, center, top, bottom, left, right, none
        self.align = kwargs.get("align","center")
        #offset from alignment, aka padding
        self.offset = Vec2(kwargs.get("offset",(0,0)))
        #size of box
        self.size = Vec2(kwargs.get("size", (0,0)))
        #width of box border, filled in if 0
        self.width = kwargs.get("width", 0)
        #size of box relative to parent, overrides self.size
        #axis-independent as well, can have a size for x and a ratio for y
        self.ratio = Vec2(kwargs.get("ratio", (0,0)))
        #If text is provided it will be the only part of the element rendered (no color fill or border
        self.text = kwargs.get("text","")
        self.font = kwargs.get("font", None)

        #parent/child organization
        self.children = kwargs.get("children", [])
        self.parent = parent
        if parent != None:
            parent.children.append(self)
    
    def siz(self):
        if self.parent != None:
            return Vec2(self.parent.siz()[0] * self.ratio[0] if self.ratio[0] != 0 else self.size[0],
                    self.parent.siz()[1] * self.ratio[1] if self.ratio[1] != 0 else self.size[1])
        else:
            return self.size

    def loc(self,alt_size = None):
        size = alt_size if alt_size != None else self.siz()
        if self.parent != None:
            parent_size = self.parent.siz()
            if self.align == "center":
                align = (parent_size / 2) - (size / 2)
            elif self.align == "none":
                align = Vec2(0,0)
            elif self.align == "left":
                align = (parent_size / 2) * Vec2(0,1) - (size / 2) * Vec2(0,1)
            elif self.align == "right":
                align = (parent_size / 2) * Vec2(2,1) - (size)
            elif self.align == "top":
                align = (parent_size / 2) * Vec2(1,0) - (size / 2) * Vec2(1,0)
            elif self.align == "bottom":
                align = (parent_size / 2) * Vec2(1,2) - (size / 2) 
            return self.parent.loc() + align + self.offset
        return self.offset
    def update(self,gui):
        for child in self.children:
            child.update(gui)
    def render(self,window,layer):
        if layer == self.layer:
            if len(self.text) == 0:
                location = self.loc()
                if not (location[0] > 1920 or location[0] + self.siz()[0] < 0):
                    pygame.draw.rect(window,self.color, (*location.render(),*self.siz().render()),self.width)
            else:
                if self.font != None:
                    text = self.font.render(self.text,1,self.color)
                    location = self.loc(Vec2(text.get_rect().width,text.get_rect().height))
                    window.blit(text,location.render())
                else:
                    print("text element not provided font")
        for child in self.children:
            child.render(window,layer)
    
class gui:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.resolution = [1920,1050]
        self.window = pygame.display.set_mode(self.resolution, pygame.RESIZABLE)
        pygame.display.set_caption("AirSchedule")
        pygame.display.set_icon(pygame.image.load("icon.png"))
        self.bg_color = (100,100,100)
        self.font_15 = pygame.font.SysFont("courier",15)
        self.font_25 = pygame.font.SysFont("courier",25)
        self.font_30 = pygame.font.SysFont("courier",30)
        self.quit = False

        self.mode = 0
        self.elements = []
        self.events = {}

        self.update(mode="load")

    def update(self,**kwargs):
        if not self.quit:            
            self.window.fill(self.bg_color)
            if kwargs.get("mode","none") == "load":
                center = element(None, size = self.resolution, color = [180,180,200])
                center_text = element(center, text=kwargs.get("msg","Connecting..."),font=self.font_30)
                self.elements = [center]
            elif kwargs.get("mode","none") == "home":
                container = element(None, size = self.resolution, color = self.bg_color)
                top = element(container, size=self.resolution,ratio=(0,0.1), color = [180,180,200],align="top")
                self.elements = [container]
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit = True
                elif event.type == pygame.VIDEORESIZE:
                    self.resolution = [event.dict['size'][0], event.dict['size'][1]]
                    self.window = pygame.display.set_mode(self.resolution, pygame.RESIZABLE)
                
            for item in self.elements:
                item.update(self)
            for i in range(5):
                for item in self.elements:
                    item.render(self.window,i)
            pygame.display.update()
        else:
            pygame.quit()
            
            
            
        

    
        
        
        
        
