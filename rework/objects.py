#Objects can be initialized with either a comma-separated string (encoded) or by kwargs
#If the string is provided, kwargs are ignored

#All objects defined via kwargs will default an attribute to None if it isn't provided
#meaning not all attributes need to be listed in the scn file to create an object

#Converts time from string format hh:mm to just minutes
def convert_time(time):
    if time != None:
        return int(time) //100 * 60 + int(time) % 100
    return 0

#for encoding and decoding lists
def encode_list(data):
    return "".join(x+"." for x in data)
def decode_list(data):
    return data.split(".")[:-1]

class scenario:
    def __init__(self, data=None, **kwargs):
        if data != None:
            self.decode(data)
        else:
            self.id = kwargs.get("id")
            self.name = kwargs.get("name")
            self.time = convert_time(kwargs.get("time",0))
            self.timescale = int(kwargs.get("timescale",300))
            
class aircraft:
    def __init__(self, data=None, **kwargs):
        if data != None:
            self.decode(data)
        else:
            self.id = kwargs.get("id")
            self.name = kwargs.get("name")
            self.tail_number = kwargs.get("tail",None)
    def encode(self):
        attributes_to_encode = [self.id,self.name,self.tail_number]
        return "aircraft" + "".join(","+x for x in attributes_to_encode)
    def decode(self,data):
        data = data.split(",")
        self.id = data[1]
        self.name = data[2]
        self.tail_number = data[3]

class flight:
    def __init__(self, data=None, **kwargs):
        if data != None:
            self.decode(data)
        else:
            self.id = kwargs.get("id")
            self.name = kwargs.get("name")
            self.departure_location = kwargs.get("departure_location",None)
            self.departure_time = convert_time(kwargs.get("departure_time",None))
            self.arrival_location = kwargs.get("arrival_location",None)
            self.arrival_time = convert_time(kwargs.get("arrival_time",None))
            self.arrival_time += 1440 if self.arrival_time < self.departure_time else 0
            self.status = "scheduled"
            self.aircraft = kwargs.get("aircraft",None)
    def encode(self):
        attributes_to_encode = [
            self.id, self.name,
            self.departure_location, self.departure_time,
            self.arrival_location, self.arrival_time,
            self.status, self.aircraft]
        return "flight" + "".join("," + str(x) for x in attributes_to_encode)
    def decode(self,data):
        data = data.split(",")
        self.id = data[1]
        self.name = data[2]
        self.departure_location = data[3]
        self.departure_time = int(data[4])
        self.arrival_location = data[5]
        self.arrival_time = int(data[6])
        self.status = data[7]
        self.aircraft = data[8]

class location:
    def __init__(self, data=None, **kwargs):
        if data != None:
            self.decode(data)
        else:
            self.id = kwargs.get("id")
            self.name = kwargs.get("name")
            self.aircraft = kwargs.get("aircraft")
    def encode(self):
        attributes_to_encode = [
            self.id,
            self.name,
            encode_list(self.aircraft)]
        return "location" + "".join("," + x for x in attributes_to_encode)
    def decode(self,data):
        data = data.split(",")
        self.id = data[1]
        self.name = data[2]
        self.aircraft = decode_list(data[3])
        
            
            
        
        
        
                            
