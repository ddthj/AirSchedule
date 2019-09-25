
class aircraft:
    def __init__(self,ref,tail):
        self.ref = ref
        self.tail = tail
        self.location = None
    def __str__(self):
        return self.ref

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
        
class manifest:
    def __init__(self,ref,objects):
        self.ref = ref
        self.objects = objects
    
class person:
    def __init__(self,ref,ident,role,itinerary = None):
        self.ref = ref
        self.id = ident
        self.role = role
        self.location = None
    def __str__(self):
        return self.id

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

class scenario:
    def __init__(self, locations, flights):
        self.locations = locations
        self.flights = flights
        self.time = 0
    
    
    
        
        
