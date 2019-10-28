import pygame

class Vec2:
    def __init__(self,*args):
        self.data = args[0] if isinstance(args[0],list) else [x for x in args]
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

class box:
    def __init__(self,parent,**kwargs):
        self.parent = parent
        if parent != None:
            self.layer = kwargs.get("layer", parent.layer + 1)
        else:
            self.layer = kwargs.get("layer", 0)
        self.location = kwargs.get("location", Vec2(0,0)) #relative location
        self.size = kwargs.get("size",Vec2(10,10))
        self.ratio = kwargs.get("ratio", None) #our size related to parent
        self.color = kwargs.get("color", [0,0,0])
        self.centered = kwargs.get("centered", False) #unused
        #controls fill/boarder width
        self.width= kwargs.get("width", 0)
        #whether or not to center box around its location
        self.children = []
    def get_loc(self):
        if self.parent != None:
            return self.parent.get_loc() + self.location
        return self.location
    def render(self,window,layer):
        if layer == self.layer:
            loc = self.get_loc()
            if loc[0] +self.size[0] > 0 and loc[0] < 1920:
                pygame.draw.rect(window,self.color, (*self.get_loc().render(),*self.size.render()),self.width)
    def onPress(self):
        pass
    def onRelease(self):
        pass
    def update(self,gui):
        if self.ratio != None:
            if self.parent != None:
                self.size = Vec2(self.parent.size[0]/self.ratio[0] if self.ratio[0] != 0 else self.size[0],
                            self.parent.size[1]/self.ratio[1] if self.ratio[1] != 0 else self.size[1])
            else:
                self.size = Vec2(gui.resolution[0]/self.ratio[0] if self.ratio[0] != 0 else self.size[0],
                                 gui.resolution[1]/self.ratio[1] if self.ratio[1] != 0 else self.size[1])

class textbox:
    def __init__(self,parent,text,**kwargs):
        self.parent = parent
        self.text = text
        self.layer = kwargs.get("layer",parent.layer + 1)
        self.color = kwargs.get("color", [0,0,0])
        self.location = kwargs.get("location", parent.location)
        self.centered = kwargs.get("centered", True)#text centered in textbox, not parent
        self.size = kwargs.get("size", 15)
        self.font = kwargs.get("font")
    def get_loc(self):
        return self.parent.get_loc() + self.location
    def render(self,window,layer):
        if layer == self.layer:
            loc = self.get_loc()
            if loc[0] >= 0 and loc[0] < 1920:
                try:
                    text = self.font.render(self.text,1,self.color)
                except:
                    pass
                center = Vec2(0,0) if not self.centered else Vec2(text.get_rect().width//2,text.get_rect().height//2)
                window.blit(text,(loc - center).render())
    def update(self,gui):
        pass

class gui:
    def __init__(self,client):
        pygame.init()
        pygame.font.init()
        self.resolution = [1920,1050]
        self.window = pygame.display.set_mode(self.resolution, pygame.RESIZABLE)
        pygame.display.set_caption("AirSchedule")
        pygame.display.set_icon(pygame.image.load("icon.png"))
        self.bg_color = (100,100,100)
        self.run = True
        self.client = client
        self.mode = 0
        self.x_scroll = 0

        top = box(None,color=[200,200,200], size=Vec2(self.resolution[0],self.resolution[1]//6),ratio=Vec2(1,0),layer=3)
        side = box(None,color=[200,200,200], location=Vec2(0,self.resolution[1]//6),size=Vec2(self.resolution[0]//8,self.resolution[1]),ratio=Vec2(0,1),layer=3)

        self.font_15 = pygame.font.SysFont("courier",15)
        self.font_25 = pygame.font.SysFont("courier",25)
        self.font_30 = pygame.font.SysFont("courier",30)

        time_box = box(side,size=Vec2(side.size[0],30),width=2)
        time_label = textbox(time_box,"Time",location=time_box.size/2,size=30,font=self.font_30)

        #time_box = box(top_bar,color=[200,200,200],layer=0, location=Vec2(0,top_bar.size[1]-25),size=Vec2(top_bar.size[0],20), ratio=Vec2(1,0))
        #time_label = textbox(time_box,"Time",location=time_box.size/2,size=30)
        self.elements = [
            top,
            side,
            time_box,
            time_label
            ]

    def update(self):
        msg = []
        self.window.fill(self.bg_color)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.run = False
            elif event.type == pygame.VIDEORESIZE:
                self.resolution = [event.dict['size'][0], event.dict['size'][1]]
                self.window = pygame.display.set_mode(self.resolution, pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.x_scroll -= 50
                elif event.button == 5:
                    self.x_scroll += 50
                if self.x_scroll < 0:
                    self.x_scroll = 0

        center = box(None,color=[210,210,210],size=Vec2(3750,29*(1+len(self.client.aircraft))),location=Vec2(self.elements[1].size[0]-self.x_scroll,self.elements[0].size[1]))
        temp = [center]
        for a in range(len(self.client.aircraft)):
            temp.append(box(center,size=Vec2(3750,30),location=Vec2(0, 29*(a+1)),width=2,layer=center.layer+2))
        for b in range(49):
            timetext = "{:02d}:{:02d}".format(30*b//60, 30*b%60)
            temp.append(box(center,size=Vec2(1, 10 + 29 * (len(self.client.aircraft))),location=Vec2(50+(b*75),20)))
            temp.append(textbox(center,timetext,location=Vec2(50 + 75*b,12),font=self.font_15))

        for flight in self.client.flights:
            i = self.client.aircraft.index([aircraft for aircraft in self.client.aircraft if aircraft.ref == flight.aircraft.ref][0])
            dept_time = int(flight.departure_time[:2])*60 + int(flight.departure_time[2:])
            arri_time = int(flight.arrival_time[:2])*60 + int(flight.arrival_time[2:])

            flight_box = box(center,color=[50,160,160],size=Vec2((((arri_time-dept_time)/30) * 75),29),location=Vec2(((dept_time/30) * 75)+50,29*(1+i)))
            flight_name = textbox(flight_box,flight.ref,location=flight_box.size/2,size=25,font=self.font_25)
            dept_name = textbox(flight_box,flight.departure_location.ref + " " + flight.departure_time,location=Vec2(0,1)*flight_box.size/2,size=15,font=self.font_15,centered=False)
            arri_name = textbox(flight_box,flight.arrival_location.ref + " " + flight.arrival_time,location=Vec2(flight_box.size[0]-75,flight_box.size[1]/2),size=15,font=self.font_15,centered=False)
            temp+= [flight_box,flight_name, dept_name,arri_name]
            
        for i in range(len(self.client.aircraft)):
            ac = box(self.elements[1], size=Vec2(self.elements[1].size[0],30),location=Vec2(0,29)*(1+i),width=2)
            tx = textbox(ac,self.client.aircraft[i].tail,location=ac.size/2 + Vec2(0,2),size=30, font=self.font_30)
            temp += [ac,tx]
            
        time = int(self.client.time[:2]) * 60 + int(self.client.time[2:])
        temp.append(box(center,color=[255,0,0],size=Vec2(2,10+29*len(self.client.aircraft)),location=Vec2(50+ time*2.5,20)))

        for element in self.elements:
            element.update(self)
        for i in range(10):
            for element in (self.elements + temp):
                element.render(self.window,i)
        if self.run:
            pygame.display.update()
        return msg
