from objects import *

class parser:
    def load(self,file):
        try:
            with open(file,"r") as f:
                raw = [line.strip().replace(" ","") for line in f.read().split("\n") if len(line) > 0]
        except Exception as e:
            print(e)
            return None
        #print(raw)

        locations = []
        #aircraft = []
        #crew = []
        flights = []

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
                #crew.append(temp_flight_crew)
                temp.crew.append(temp_flight_crew)
            elif line.find("aircraft") != -1:
                aircraft_name = line.split("aircraft")[1]
                temp_aircraft = aircraft(aircraft_name)
                #aircraft.append(temp_aircraft)
                temp.aircraft.append(temp_aircraft)
        if temp.name != "temp":
            locations.append(temp)
                
        return locations,flights
                               
x = parser()
loc,flt = x.load("scenarios/test.scn")
print(loc[0])           
                
                
                    
                    
        

        

        
                
        
        
