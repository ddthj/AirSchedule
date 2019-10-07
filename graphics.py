import pygame

class gui:
    def __init__(self,client):
        pygame.init()
        pygame.font.init()
        self.resolution = [1440, 960]
        self.scale = 1
        self.window = pygame.display.set_mode(self.resolution, pygame.RESIZABLE)
        pygame.display.set_caption("AirSchedule")
        pygame.display.set_icon(pygame.image.load("icon.png"))
        self.bg_color = (100,100,100)
        self.run = True
        self.mode = 0
        self.x_scroll = 0
        self.client = client

    def resize(self,event):
        average_rescale = sum([event.dict['size'][0]/self.resolution[0],event.dict['size'][1]/self.resolution[1]]) / 2
        self.resolution = [int(self.resolution[0]*average_rescale),int(self.resolution[1]*average_rescale)]
        self.scale = self.resolution[0] / 720
        self.window = pygame.display.set_mode(self.resolution, pygame.RESIZABLE)

    def render_mode(self):
        if self.mode == 0:
            self.render_top()

    def render_top(self):
        #rendering light bg and black outlines
        self.rect(0,0,self.resolution[0]//6,self.resolution[1],(200,200,200),True)
        self.rect(0,0,self.resolution[0]//6,self.resolution[1],(0,0,0),False)
        self.rect(0,0,self.resolution[0],self.resolution[1]//6,(200,200,200),True)
        self.rect(0,0,self.resolution[0],self.resolution[1]//6,(0,0,0),False)
        #rendering time axis
        text_center = [self.resolution[0]//2, self.resolution[1]//10]
        self.text(text_center[0],text_center[1],(0,0,0),"Time",19,True,True)
        for i in range(20):
            time = "{:02d}:{:02d}".format(30*i//60, 30*i%60)
            self.text(74*i + self.resolution[0]//6,self.resolution[1]//6.5,(0,0,0),time,15,True,True)
            self.rect(74*i + self.resolution[0]//6,self.resolution[1]//6,75,self.resolution[1]-self.resolution[1]//6,(50,50,50),False)
        for i in range(len(self.client.aircraft)):
            tail = self.client.aircraft[i].tail
            self.text(self.resolution[0]//12,self.resolution[1]//15*i + self.resolution[1]//5,(0,0,0),tail,19,True,True)
            self.rect(0,self.resolution[1]//15*i + self.resolution[1]//6,self.resolution[0],self.resolution[1]//15,(0,0,0),False)
            for flight in self.client.flights:
                if flight.aircraft.ref == self.client.aircraft[i].ref:
                    dept_time = int(flight.departure_time[:2])*60 + int(flight.departure_time[2:])
                    arri_time = int(flight.arrival_time[:2])*60 + int(flight.arrival_time[2:])
                    x = self.resolution[0]//6 + int((dept_time/30)*74)+1
                    y = self.resolution[1]//15*i + self.resolution[1]//6 +2
                    w = int(((arri_time-dept_time)/30)*74)
                    h = self.resolution[1]//15 -3
                    self.rect(x,y,w,h,(50,160,160),True)
                    self.text(x+w//2, y+h//3, (0,0,0),flight.ref,19,True,True)
                    self.text(x+w//2, y+h//1.25, (0,0,0),flight.status,12,True,True)
                    self.text(x+5, y+h//2.5, (0,0,0),flight.departure_time,12,False,True)
                    self.text(x+5, y+h//1.5, (0,0,0),flight.departure_location.ref,12,False,True)
                    self.text(x+w-32, y+h//2.5, (0,0,0),flight.arrival_time,12,False,True)
                    self.text(x+w-32, y+h//1.5, (0,0,0),flight.arrival_location.ref,12,False,True)
                    
            
    def update(self):
        self.window.fill(self.bg_color)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.run = False
            elif event.type == pygame.VIDEORESIZE:
                self.resize(event)
        self.render_mode()
        if self.run:
            pygame.display.update()

    def rect(self,x,y,w,h,color,fill=False):
        width = 0 if fill else 2
        pygame.draw.rect(self.window,color,(x,y,w,h),width)
    
    def text(self,x,y,color,text,size,centerx,centery):
        font = pygame.font.SysFont("courier",size)
        text = font.render(text,1,color)
        x -= text.get_rect().width//2 if centerx else 0            
        y -= text.get_rect().height//2 if centery else 0   
        self.window.blit(text,(x,y))
