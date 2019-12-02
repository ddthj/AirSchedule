import pygame
from vector import Vec2
from objects import flight

def inside(elem,point):
    top_left = elem.loc()
    bottom_right = top_left + elem.siz()
    if top_left[0] < point[0] and bottom_right[0] > point[0] and top_left[1] < point[1] and bottom_right[1] > point[1]:
        return True
    return False

#converts from m into hh:mm
def string_time(time):
    hours = time // 60 * 100
    minutes = time % 60
    return "{:04d}".format(hours+minutes)

#Event handler for the flights_by_aircraft page that allows scrolling through the schedule
def scroll_handler(self,client,events):
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.offset -= Vec2(100,0)
            elif event.button == 5:
                self.offset += Vec2(100,0)
            if self.offset[0] > 0:
                self.offset = Vec2(0,0)

#handler that updates the position of the red time line
def time_line_handler(self,client,events):
    scn = client.objects.get("scenario",[])
    if len(scn) > 0:
        time = scn[0].time
        self.offset = Vec2(time*2.5,0)

#returns color based on status of flight
def flight_box_color(status):
    if status == "scheduled":
        return [50,160,160]
    elif status == "outgate":
        return [50,200,200]
    elif status == "offground":
        return [50, 160, 68]
    elif status == "onground":
        return [50, 109, 160]
    elif status == "ingate":
        return [78, 104, 128]
    
def flight_box_handler(self,client,events):
    flag = False
    index = -1 + (self.parent.offset[1]//30) + self.offset[1] // 30
    if self.selected == True:
        mov = Vec2(*client.mouse) - self.start_pos
        if mov[1] > 25 and index < len(client.objects["aircraft"])-1:
            self.offset += Vec2(0,30)
            self.start_pos += Vec2(0,30)
        elif mov[1] < -25 and index > 0:
            self.offset -= Vec2(0,30)
            self.start_pos -= Vec2(0,30)
    
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and inside(self,client.mouse):
                self.selected = True
                self.start_pos = Vec2(*client.mouse)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.selected == True:
                    flag = True
                self.selected = False
                
    for i in client.objects["flight"]:
        if i.id == self.id:
            self.color = flight_box_color(i.status)
            if flag:
                temp = flight(i.encode())
                temp.aircraft = client.objects["aircraft"][index].id
                client.pending_updates.append("ud,"+temp.encode())
            break

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
        #If text is provided it will be the only part of the element rendered unless there is a width assigned (no fill)
        self.text = kwargs.get("text","")
        self.font = kwargs.get("font", None)
        #How this element responds to events and updates
        self.handler = kwargs.get("handler",None)
        self.selected = False #flag used for flight box event handler
        self.start_pos = Vec2(0,0) #vector used for flight box event handler
        #if this element renders
        self.visible = kwargs.get("visible",True)
        #parent/child organization
        self.children = kwargs.get("children", [])
        self.parent = parent
        if parent != None:
            parent.children.append(self)
    #Returns the size of the element after adjusting via ratio
    def siz(self):
        if self.parent != None:
            return Vec2(self.parent.siz()[0] * self.ratio[0] if self.ratio[0] != 0 else self.size[0],
                    self.parent.siz()[1] * self.ratio[1] if self.ratio[1] != 0 else self.size[1])
        else:
            return self.size
    #Returns the location of the element after factoring in parent's location, alignment, offsets, etc
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
                align = (parent_size / 2) * Vec2(2,1) - (size/2) * Vec2(2,1)
            elif self.align == "top":
                align = (parent_size / 2) * Vec2(1,0) - (size / 2) * Vec2(1,0)
            elif self.align == "bottom":
                align = (parent_size / 2) * Vec2(1,2) - (size/2) * Vec2(1,2)
            return self.parent.loc() + align + self.offset
        return self.offset
    #Allows the element to handle events if it has a handler, also calls children's update functions
    def update(self,client,events):
        if self.handler != None:
            self.handler(self,client,events)
        for child in self.children:
            child.update(client,events)
    #Renders the element if it is visible, also calls children's render functions
    def render(self,window,layer):
        if layer == self.layer:
            if len(self.text) == 0:
                location = self.loc()
                if not (location[0] > 1920 or location[0] + self.siz()[0] < 0):
                    pygame.draw.rect(window,self.color, (*location.render(),*self.siz().render()),self.width)
            else:
                text = self.font.render(self.text,1,self.color)
                location = self.loc(Vec2(text.get_rect().width,text.get_rect().height))
                if self.font != None:
                    if not (location[0] > 1920 or location[0] + self.siz()[0] < 0):
                        window.blit(text,location.render())
                        if self.width > 0:
                            location = self.loc()
                            pygame.draw.rect(window,self.color, (*location.render(),*self.siz().render()),self.width)
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

        self.mode = "load"
        self.update(None,mode="load")

    def update(self,client,**kwargs):
        if not self.quit:
            #self.window.fill(self.bg_color) #fills screen with bg color - not necessary if elements populate entire screen

            #sets elements to loading screen
            if kwargs.get("mode","none") == "load":
                self.mode = "load"
                center = element(None, size = self.resolution, color = [180,180,200])
                center_text = element(center, text=kwargs.get("msg","Connecting..."),font=self.font_30)
                self.elements = [center]
            #sets elements for home screen - unused screen
            elif kwargs.get("mode","none") == "home":
                self.mode = "home"
                container = element(None, size = self.resolution, color = self.bg_color)
                top = element(container, size=self.resolution,ratio=(0,0.1), color = [180,180,200],align="top")
                self.elements = [container]
            #sets elements to display flights by aircraft
            elif kwargs.get("mode","none") == "flights_by_aircraft":
                self.mode = "flights_by_aircraft"
                container = element(None, size = self.resolution,visible=False)
                top = element(container, size=self.resolution,ratio=(0,0.1), color = [180,180,200],align="top",layer=0)
                bottom = element(container, size=self.resolution,ratio=(0,0.9),align="bottom",visible=False,layer=0)
                sidebar = element(bottom,align="left",color = [180,180,200], ratio=Vec2(0.1,1),layer=2)
                center = element(bottom,align="right", ratio=Vec2(0.9,1),layer=0,visible=False)
                time_box = element(sidebar, align="top",width=1,text="Time",font=self.font_25, size=Vec2(1,30),ratio=(1,0),visible=False)
                schedule = element(center,align="left", ratio=Vec2(0,1), size=(3675,0),color=[210,210,230],handler=scroll_handler,layer=0)
                time_row = element(schedule,size=Vec2(1,30),ratio=Vec2(1,0),align="top",width=1,layer=0)
                times = [element(time_row,size=Vec2(75,30),align="left",offset=Vec2((75*i)-25,0),text="{:02d}:{:02d}".format(30*i//60, 30*i%60),font=self.font_15) for i in range(49)]
                time_line = element(schedule,align="none",color=[255,0,0],layer=1, size=Vec2(2,1),ratio=Vec2(0,1),handler=time_line_handler)
                aircraft_objects = client.objects.get("aircraft",[])
                flight_objects = client.objects.get("flight",[])
                aircraft_labels, aircraft_rows, flights = [], [], []
                for i in range(len(aircraft_objects)):
                    aircraft_labels.append(element(sidebar,align="top",width=1,text=aircraft_objects[i].tail_number,font=self.font_25,size=Vec2(1,30),ratio=(1,0),offset=Vec2(0,(1+i)*30)))
                    row = element(schedule,size=Vec2(1,30),ratio=Vec2(1,0),align="top",width=1,offset=Vec2(0,(1+i)*30),visible=False)
                    aircraft_rows.append(row)
                    for flight in flight_objects:
                        if flight.aircraft == aircraft_objects[i].name:
                            box_color = flight_box_color(flight.status)
                            flight_box = element(row,color=box_color,size=Vec2((((flight.arrival_time-flight.departure_time)/30) * 75),30),align="left",offset=Vec2((flight.departure_time/30) * 75,0),layer=row.layer-1,handler=flight_box_handler)
                            flight_box.id = flight.id
                            flight_name = element(flight_box,text=flight.name,font=self.font_25)
                            flight_dept_info = element(flight_box,text=flight.departure_location,font=self.font_15,align="left")
                            flight_arri_info = element(flight_box,text=flight.arrival_location,font=self.font_15,align="right")
                            flights.append(flight_box)
                self.elements = [container]
            
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.quit = True
                elif event.type == pygame.VIDEORESIZE:
                    self.resolution = [event.dict['size'][0], event.dict['size'][1]]
                    self.window = pygame.display.set_mode(self.resolution, pygame.RESIZABLE)
            if client != None:
                client.mouse = pygame.mouse.get_pos()
            for item in self.elements:
                item.update(client,events)
            for i in range(4):
                for item in self.elements:
                    item.render(self.window,i)
            pygame.display.update()
        else:
            pygame.quit()
