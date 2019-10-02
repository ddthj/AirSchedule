class aircraft:
    def __init__(self,ref,tail):
        self.ref = ref
        self.tail = tail
        self.location = None 
    def __str__(self):
        return self.ref
    def encode(self):
        return "aircraft," + self.ref + "," + self.tail + "\t"

class group:
    def __init__(self,ref,people):
        self.ref = ref
        self.people = people
    def __str__(self):
        return self.ref

class itinerary:
    def __init__(self,ref,flights):
        self.ref = ref
        self.flights = flights #not actually flight objects, just flight ref strings
    def __str__(self):
        msg = self.ref + "\n"
        for item in self.flights:
            msg += item + "\n"
        return msg
    def encode(self):
        return "itinerary," + self.ref + "\t" + "".join([x + "," for x in self.flights]) + "\n"
    def decode(self,msg,scn):
        items = [x for x in msg.split("\t") if len(x) > 0]
        self.ref = items[0].split(",")[1]
        self.flights = [x for x in items[1].split(",") if len(x) > 0]
        
class manifest:
    def __init__(self,ref,objects):
        self.ref = ref
        self.objects = objects
    def encode(self):
        if self.objects != None:
            return "manifest," + self.ref + "\t" + "".join(x.encode() + "\t" for x in self.objects) + "\n"
    def decode(self,msg,scn):
        items = [x for x in msg.split("\t") if len(x) > 0]
        for item in items:
            bits = item.split(",")
            if bits[0] == "manifest":
                self.ref = bits[1]
            elif bits[0] == "person":
                temp = scn.object_by_ref(scn.people,None,bits[1])
                if temp != None:
                    self.objects.append(temp)
                else:
                    temp = person(None,bits[1],bits[2],bits[3])
                    scn.people.append(temp)
                    self.objects.append(temp)
        return self
                
class person:
    def __init__(self,ref,ident,role,itinerary = None):
        self.ref = ref
        self.id = ident
        self.role = role
        self.itinerary = itinerary
        self.location = None
    def __str__(self):
        return self.id
    def encode(self):
        return "person," + self.id + "," + self.role + "," + str(self.itinerary) + "\t"

class flight:
    def __init__(self,
        ref,
        manifest,
        aircraft,
        departure_location,
        departure_time,
        arrival_location,
        arrival_time):

        self.ref = ref
        self.manifest = manifest
        self.aircraft = aircraft
        self.flight_crew = []
        self.cabin_crew = []
        self.passengers = []
        self.nonrev = []
        self.cargo = []
        self.departure_location = departure_location
        self.departure_time = departure_time
        self.arrival_location = arrival_location
        self.arrival_time = arrival_time
        self.status = "scheduled"
    def __str__(self):
        msg = self.ref
        msg += "\n%s @%s to %s @%s" % (self.departure_location.ref, self.departure_time, self.arrival_location.ref,self.arrival_time)
        return msg
    def encode(self):
        return "flight," + self.ref + "," + self.manifest.ref + "," + self.aircraft.ref + "," + self.departure_location.ref + "," + self.departure_time + "," + self.arrival_location.ref + "," + self.arrival_time + "," + self.status + "\n"
    def decode(self,msg,scn):
        bits = [x for x in msg.split(",") if len(x) > 0]
        self.ref = bits[1]
        self.manifest = bits[2]
        self.aircraft = bits[3]
        self.deperture_location = bits[4]
        self.departure_time = bits[5]
        self.arrival_location = bits[6]
        self.arrival_time = bits[7]
        self.status = bits[8]
        return self
    def resolve_references(self,scn):
        self.manifest = scn.object_by_ref(scn.manifests, self.manifest, None)
        self.aircraft = scn.object_by_ref(scn.aircraft,self.aircraft,None)
        self.departure_location = scn.object_by_ref(scn.locations,self.departure_location,None)
        self.arrival_location = scn.object_by_ref(scn.locations, self.arrival_location,None)  
        
class location:
    def __init__(self, ref, aircraft, flight_crew, cabin_crew, passengers, cargo):
        self.ref = ref
        self.aircraft = aircraft
        self.flight_crew = flight_crew
        self.cabin_crew = cabin_crew
        self.passengers = passengers
        self.cargo = cargo   
    def __str__(self):
        msg = str(self.ref) + "\n"
        msg += "Aircraft: %s" % str( len(self.aircraft))
        msg += "\nPilots: %s" % str( len(self.flight_crew))
        msg += "\nAttendants: %s" % str( len(self.cabin_crew))
        msg += "\nPassengers: %s" % str( len(self.passengers))
        return msg
    def encode(self):
        return "location," + self.ref + "\t" + "".join([x.encode() for x in self.aircraft]) + "".join([x.encode() for x in self.flight_crew + self.cabin_crew + self.passengers]) + "".join(x.encode() for x in self.cargo) + "\n"
    def decode(self,msg,scn):
        items = [x for x in msg.split("\t") if len(x) > 0]
        for item in items:
            bits = item.split(",")
            if bits[0] == "location":
                self.ref = bits[1]
            elif bits[0] == "aircraft":
                temp = scn.object_by_ref(scn.aircraft,bits[1],None)
                if temp != None:
                    temp.location = self
                    self.aircraft.append(temp)
                else:
                    temp = aircraft(bits[1],bits[2])
                    temp.location = self
                    scn.aircraft.append(temp)
            elif bits[0] == "person":
                temp = scn.object_by_ref(scn.people,None,bits[1])
                if temp != None:
                    temp.location = self
                else:
                    temp = person(None,bits[1],bits[2],bits[3])
                    temp.location = self
                    scn.people.append(temp)
                if temp.role == "pilot":
                    self.flight_crew.append(temp)
                elif temp.role == "attendant":
                    self.cabin_crew.append(temp)
                else:
                    self.passengers.append(temp)
                    
            elif bits[0] == "cargo":
                pass
            else:
                print("failed to decode bit %s" % bits)
        return self

class scenario:
    def __init__(self, locations, flights, manifests, groups, itineraries, aircraft, people):
        self.locations = locations
        self.flights = flights
        self.manifests = manifests
        self.groups = groups
        self.itineraries = itineraries
        self.aircraft = aircraft
        self.people = people
        self.time = 0
    def object_by_ref(self,objects,ref,ident):
        for item in objects:
            if ident != None and ident == item.id:
                return item
            elif ident == None and item.ref == ref:
                return item
        return None
    def encode(self):
        return "".join([x.encode() for x in self.locations]) + "".join([x.encode() for x in self.flights]) + "".join([x.encode() for x in self.manifests]) + "".join([x.encode() for x in self.itineraries])
    def decode(self,msg):
        main = [x for x in msg.split("\n") if len(x) > 0]
        for item in main:
            if item.find("location") != -1:
                self.locations.append(location(None,[],[],[],[],[]).decode(item,self))
            elif item.find("flight") != -1:
                self.flights.append(flight(None,None,None,None,None,None,None).decode(item,self))
            elif item.find("manifest") != -1:
                self.manifests.append(manifest(None,[]).decode(item,self))
            elif item.find("itinerary") != -1:
                self.itineraries.append(itinerary(None,[]).decode(item,self))
            else:
                print("couldn't decode %s" % (item))
                
