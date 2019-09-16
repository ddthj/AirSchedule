
class aircraft:
    def __init__(self,name):
        self.name = name
    def __str__(self):
        return "Aircraft "+self.name

class crew:
    def __init__(self,name):
        self.name = name
    def __str__(self):
        return "Crew " +self.name

class cabin_crew(crew):
    pass

class flight_crew(crew):
    pass

class flight:
    def __init__(
        self,
        name,
        aircraft,
        flight_crew,
        departure_location,
        departure_time,
        arrival_location,
        arrival_time):

        self.name = name
        self.aircraft = aircraft
        self.flight_crew = flight_crew
        self.departure_location = departure_location
        self.departure_time = departure_time
        self.arrival_location = arrival_location
        self.arrival_time = arrival_time
        self.status = "scheduled"
        self.warnings = []
        
class location:
    def __init__(self, name, aircraft, crew):
        self.name = name
        self.aircraft = [] if aircraft == None else aircraft
        self.crew = [] if crew == None else crew
    def __str__(self):
        msg = str(self.name) + "\n"
        for aircraft in self.aircraft:
            msg += str(aircraft) + "\n"
        for crew in self.crew:
            msg += str(crew) + "\n"
        return msg

class scenario:
    def __init__(self, locations, flights):
        self.locations = locations
        self.flights = flights
        self.time = 0
    
    
    
        
        
