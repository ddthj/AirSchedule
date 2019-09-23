from objects import *

class gen:
    def __init__(self):
        self.person = 0
        x = itinerary("a",[])
    def get(self,role):
        number = "{:04d}".format(self.person)
        self.person +=1
        if role == "pilot":
            return "fc"+number
        elif role == "attendant":
            return "cc"+number
        else:
            return "px"+number
        
class parser:
    def __init__(self,file):
        self.file = file
        self.gen = gen()
        self.raw = self.load(self.file)
        self.locations = []
        self.aircraft = []
        self.people = []
        self.itineraries = []
        self.groups = []
        self.flights = []
        self.manifests = []
        
        if self.raw != None:
            self.raw_objects = self.split(self.raw)
            self.parse(self.raw_objects)
            
    #turns lists into actual objects
    def parse(self,obs):
        #first pass defines all itineraries and aircraft
        for item in obs:
            if item[0].find("itinerary") != -1:
                ident = item[0].split("itinerary")[1]
                flights = [item[i].strip() for i in range(1,len(item))]
                self.itineraries.append(itinerary(ident,flights))
            elif item[0].find("aircraft") != -1:
                ref = item[0].split("aircraft")[1]
                tail = None
                for i in range(1,len(item)):
                    if item[i].find("tail") != -1:
                        tail = item[i].split("tail")[1]
                self.aircraft.append(aircraft(ref,tail))

        #second pass gets people and groups
        for item in obs:
            if item[0].find("person") != -1:
                ref = item[0].split("person")[1]
                ident = None
                role = None
                itinerary_ref = None
                for i in range(1,len(item)):
                    if item[i].find("role") != -1:
                        role = item[i].split("role")[1]
                    elif item[i].find("itinerary") != -1:
                        itinerary_ref = item[i].split("itinerary")[1]
                self.people.append(person(ref,self.gen.get(role),role,itinerary_ref))
                
            elif item[0].find("group") != -1:
                ref = item[0].split("group")[1]
                quantity = None
                itinerary_ref = None
                role = None
                for i in range(1,len(item)):
                    if item[i].find("quantity") != -1:
                        quantity = item[i].split("quantity")[1]
                    elif item[i].find("itinerary") != -1:
                        itinerary_ref = item[i].split("itinerary")[1]
                    elif item[i].find("role") != -1:
                        role = item[i].split("role")[1]
                people = [person(None,self.gen.get(role),role,itinerary_ref) for i in range(int(quantity))]
                #self.people += people
                self.groups.append(group(ref,people))

        #third pass gets manifests and locations
        for item in obs:
            if item[0].find("manifest") != -1:
                ref = item[0].split("manifest")[1]
                include = []
                for i in range(1,len(item)):
                    if item[i].find("person") != -1:
                        ref = item[i].split("person")[1]
                        include.append(self.person_by_ref(ref))
                    elif item[i].find("group") != -1:
                        ref = item[i].split("group")[1]
                        include += self.group_by_ref(ref).people
                self.manifests.append(manifest(ref,include))
            elif item[0].find("location") != -1:
                name = item[0].split("location")[1]
                local_aircraft = []
                local_flight_crew = []
                local_cabin_crew = []
                local_passengers = []
                local_cargo = []
                temp = [x for x in item if x.find("\t\t") != -1]
                for i in range(len(temp)):
                    if temp[i].find("aircraft") != -1:
                        ref = temp[i].split("aircraft")[1]
                        local_aircraft.append(self.aircraft_by_ref(ref))
                    elif temp[i].find("person") != -1:
                        ref = temp[i].split("person")[1]
                        local_person = self.person_by_ref(ref)
                        if local_person.role == "pilot":
                            local_flight_crew.append(local_person)
                        elif local_person.role == "attendant":
                            local_cabin_crew.append(local_person)
                        else:
                            local_passengers.append(local_person)
                    elif temp[i].find("group") != -1:
                        ref = temp[i].split("group")[1]
                        local_group = self.group_by_ref(ref)
                        local_passengers += local_group.people
                    #cargo, etc
                self.locations.append(location(name,local_aircraft,local_flight_crew,local_cabin_crew,local_passengers,local_cargo))
                                     
                        
    def group_by_ref(self,ref):
        for group in self.groups:
            if group.ref == ref:
                return group
        print("couldn't find group %s" % (ref))
        
    def person_by_ref(self,ref):
        for person in self.people:
            if person.ref == ref:
                return person
        print("couldn't find person %s" % (ref))

    def aircraft_by_ref(self,ref):
        for aircraft in self.aircraft:
            if aircraft.ref == ref:
                return aircraft
        print("couldn't find aircraft %s" % (ref))
    
    #splits a list by strings that aren't indented
    def split(self,raw):
        obs = []
        i = 0
        for j in range(1,len(raw)):
            if raw[j].find("\t") == -1:
                obs.append(raw[i:j])
                i=j
        obs.append(raw[i:j+1])
        return obs
                
    #reads file, puts each valid line into a list
    def load(self,file):
        try:
            with open(file,"r") as f:
                #removes spaces, newlines, empty lines, and anything with a "/"
                raw = [line.replace(" ","") for line in f.read().split("\n") if len(line.strip()) > 0 and line[0] != "/"]
                return raw
        except Exception as e:
            print(e)
                               
x = parser("scenarios/test.scn")

                
                
                    
                    
        

        

        
                
        
        
