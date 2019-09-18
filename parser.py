from objects import *

class parser:
    def __init__(self):
        self.locations = []
        self.flights = []

    def handle_obj(self,obj):
        if obj[0].find("location") != -1:
            location_name = obj[0].split("location")[1]
            temp = location(location_name,None,None)
            for item in obj:
                if item.find("flight_crew") != -1:
                    flight_crew_name = line.split("flight_crew")[1]
                    temp.crew.append(flight_crew(flight_crew_name))
                elif item.find("aircraft") != -1:
                    aircraft_name = line.split("aircraft")[1]
                    temp.aircraft.append(aircraft(aircraft_name))
                #cabin crew, cargo, nonrev, etc
            self.locations.append(temp)
        
    
    def load(self,file):
        try:
            with open(file,"r") as f:
                raw = [line.strip().replace(" ","") for line in f.read().split("\n") if len(line) > 0]
        except Exception as e:
            print(e)
            return None,None

        obj = 0
        for i in range(len(raw)):
            if raw[i].find("location") != -1:
                if obj != 0:
                    self.handle_obj(raw[obj:i-1])
                obj = i
            elif raw[i].find("flight") != -1 and not raw[i].find("crew") != -1:
                if obj != 0:
                    pass#self.handle_obj(raw[obj:i-1])
                obj = i
        #self.handle_obj(raw[obj:i])           
            
                
        '''        
        temp = location("temp",None,None)
        for line in raw:
            if line.find("location") != -1:
                location_name = line.split("location")[1]
                if temp.name != "temp":
                    locations.append(temp)
                temp = location(location_name,None,None)
            elif line.find("flight_crew") != -1:
                flight_crew_name = line.split("flight_crew")[1]
                temp_flight_crew = flight_crew(flight_crew_name)
                temp.crew.append(temp_flight_crew)
            elif line.find("aircraft") != -1:
                aircraft_name = line.split("aircraft")[1]
                temp_aircraft = aircraft(aircraft_name)
                temp.aircraft.append(temp_aircraft)
        if temp.name != "temp":
            locations.append(temp)
        '''
                
        return self.locations,self.flights
                               
x = parser()
loc,flt = x.load("scenarios/test.scn")
for item in loc:
    print(item)
                
                
                    
                    
        

        

        
                
        
        
