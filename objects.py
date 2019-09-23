
class aircraft:
    def __init__(self,ref,tail):
        self.ref = ref
        self.tail = tail
    def __str__(self):
        return self.id

class group:
    def __init__(self,ref,people):
        self.ref = ref #used for parsing only
        self.people = people
    def __str__(self):
        return self.id

class itinerary:
    def __init__(self,ident,flights):
        self.id = ident
        self.flights = flights
    def __str__(self):
        msg = self.id + "\n"
        for item in self.flights:
            msg += item + "\n"
        return msg
        
class manifest:
    def __init__(self,ref,objects):
        self.ref = ref
        self.objects = objects
    
class person:
    def __init__(self,ref,ident,role,itinerary = None):
        self.id = ident
        self.ref = ref #used for parsing only
        self.role = role
    def __str__(self):
        return self.id

class flight:
    def __init__(self,
        ident,
        manifest,
        aircraft,
        departure_location,
        departure_time,
        arrival_location,
        arrival_time):

        self.id = ident
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
        
class location:
    def __init__(self, ident, aircraft, flight_crew, cabin_crew, passengers, cargo):
        self.id = ident
        self.aircraft = aircraft
        self.flight_crew = flight_crew
        self.cabin_crew = cabin_crew
        self.passengers = passengers
        self.cargo = cargo
        
    def __str__(self):
        msg = str(self.id) + "\n"
        msg += "Aircraft: %s" % str( len(self.aircraft))
        msg += "Pilots: %s" % str( len(self.flight_crew))
        msg += "Attendants: %s" % str( len(self.cabin_crew))
        msg += "Passengers: %s" % str( len(self.passengers))
        return msg

class scenario:
    def __init__(self, locations, flights):
        self.locations = locations
        self.flights = flights
        self.time = 0
    
    
    
        
        
