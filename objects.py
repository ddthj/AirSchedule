import re

#todo - when adding small objects to flights/manifests/etc encode the entire object
#on decode check for existing objects with the same ref/id

class aircraft:
    def __init__(self,ref,tail):
        self.ref = ref
        self.tail = tail
        self.location = None 
    def __str__(self):
        return self.ref
    def encode(self):
        return "aircraft," + self.ref + "," + self.tail + "," + self.location.ref + "\n"
    def decode(self, msg):
        msg = msg.split(",")
        self.ref = msg[1]
        self.tail = msg[2]
        self.location = msg[3]        

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
        return "itinerary," + self.ref + "," + "".join([x + "," for x in self.flights]) + "\n"
    def decode(self,msg):
        msg = msg.split(",")
        self.ref = msg[1]
        self.flights = [msg[i] for i in range(2,len(msg))]
        
class manifest:
    def __init__(self,ref,objects):
        self.ref = ref
        self.objects = objects
    def encode(self):
        if self.objects != None:
            return "manifest," + self.ref + "," + "".join(type(x).__name__ + "," + str(x.id) + "," for x in self.objects if x.ref != None) + "\n"
    def decode(self,msg):
        msg = msg.split(",")
        self.ref = msg[1]
        self.objects = [msg[i]+msg[i+1] for i in range(2,len(msg),2)]
    
class person:
    def __init__(self,ref,ident,role,itinerary = None):
        self.ref = ref
        self.id = ident
        self.role = role
        self.location = None
    def __str__(self):
        return self.id
    def encode(self):
        if self.location != None:
            return "person," + self.id + "," + self.role + "," + self.location.ref + "\n"
        return "person," + self.id + "," + self.role + "," + "None" + "\n"
    def decode(self,msg):
        msg = msg.split(",")
        self.id = msg[1]
        self.role = msg[2]
        self.location = msg[3]

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
    def decode(self,msg):
        msg = msg.split(",")
        self.ref = msg[1]
        self.manifest = msg[2]
        self.aircraft = msg[3]
        self.departure_location = msg[4]
        self.departure_time = msg[5]
        self.arrival_location = msg[6]
        self.arrival_time = msg[7]
        
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
        return "location," + self.ref + ",aircraft," + "".join([x.ref + "," for x in self.aircraft]) + "people," + "".join([x.id + "," for x in self.flight_crew + self.cabin_crew + self.passengers]) + "cargo," + "".join(x.ref + "," for x in self.cargo) + "\n"
    def decode(self,msg):
        msg = msg.split(",") 
        self.ref = msg[1]
        self.aircraft = msg[3:msg.index("people")]
        self.people = msg[msg.index("people")+1:msg.index("cargo")]
        self.cargo = msg[msg.index("cargo")+1:]
        

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
    def encode(self):
        return "".join([x.encode() for x in self.locations]) + "".join([x.encode() for x in self.flights]) + "".join([x.encode() for x in self.manifests]) + "".join([x.encode() for x in self.itineraries]) + "".join([x.encode() for x in self.aircraft]) + "".join([x.encode() for x in self.people])
