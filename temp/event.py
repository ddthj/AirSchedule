"""
AirSchedule Event
2020

This file contains the event class, which is used to keep track of
changing object attributes as the simulation progresses

Events are used to update clients on the state of the simulation
And support undo actions
"""
from setup import simObject

class event_id_generator:
    def __init__(self):
        self.id = 0
    def get(self):
        self.id += 1
        return self.id

EVENT_ID_GENERATOR = event_id_generator()

class event:
    def __init__(self,ident,reference,attributeName,old_value,new_value):
        self.ident = ident
        #a reference to the object that was affected by the event
        self.reference = reference
        #The attribute affected
        self.attributeName = attributeName
        #the old and new value of the attribute
        self.old_value = old_value
        self.new_value = new_value

    #restores the original value and returns a new event that documents the undo
    def undo(self,ident):
        self.reference.__setattr__(self.attributeName,self.old_value)
        return event(ident,self.reference,self.attributeName,self.new_value,self.old_value)
        
    #returns a string that describes the event
    def encode(self):
        message = "%s,%s,%s,%s," % (self.ident,self.reference.objectType,self.reference.objectName,self.attributeName)
        if isinstance(self.new_value,list):
            if len(self.new_value) > 0:
                if isinstance(self.new_value[0],simObject):
                    message += str(self.new_value[0].objectType) + "," + "".join(x.objectName + ";" for x in self.new_value)
                else:
                    message += "".join(str(x) + ";" for x in self.new_value)
            else:
                message += ";"
        elif isinstance(self.new_value,simObject):
            message += str(self.new_value.objectType) + "," + str(self.new_value.objectName)
        else:
            message += str(self.new_value)
        
        return message

#decodes an encoded event. This serves as an example and isn't utilized on the server's side
def decode_event(string):
    data = string.split(",")
    ident = int(data[0])
    objectType = data[1]
    objectName = data[2]
    attributeName = data[3]
    new_value = None
    referenceType = None
    referenceName = None
    #determine if the attribute is a reference
    if len(data) > 5:
        referenceType = data[4]
        referenceName = data[5]
        #check to see if our reference is actually a list of references
        if referenceName.split(";") > 1:
            referenceName = [x for x in data[5].split(";") if len(x) > 0]
    elif data[4].split(";") > 1:
        new_value = [x for x in data[4].split(";") if len(x) > 0]
    else:
        new_value = data[4]
    
            
            
        
        
        
        
