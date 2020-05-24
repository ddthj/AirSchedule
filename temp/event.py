"""
AirSchedule Event
2020

This file contains the event class, which is used to keep track of
changing object attributes as the simulation progresses

Events are used to update clients on the state of the simulation
And support undo actions
"""
from setup import SimObject


class EventIdGenerator:
    def __init__(self):
        self.id = 0

    def get(self):
        self.id += 1
        return self.id


EVENT_ID_GENERATOR = EventIdGenerator()


class Event:
    def __init__(self, ident, reference, attribute_name, old_value, new_value):
        self.ident = ident
        # a reference to the object that was affected by the event
        self.reference = reference
        # The attribute affected
        self.attributeName = attribute_name
        # the old and new value of the attribute
        self.old_value = old_value
        self.new_value = new_value

    # restores the original value and returns a new event that documents the undo
    def undo(self, ident):
        self.reference.__setattr__(self.attributeName, self.old_value)
        return Event(ident, self.reference, self.attributeName, self.new_value, self.old_value)

    # returns a string that describes the event
    def encode(self):
        message = "%s,%s,%s,%s," % (
            self.ident, self.reference.object_type, self.reference.object_name, self.attributeName)
        if isinstance(self.new_value, list):
            if len(self.new_value) > 0:
                if isinstance(self.new_value[0], SimObject):
                    message += str(self.new_value[0].object_type) + "," + "".join(
                        x.object_name + ";" for x in self.new_value)
                else:
                    message += "".join(str(x) + ";" for x in self.new_value)
            else:
                message += ";"
        elif isinstance(self.new_value, SimObject):
            message += str(self.new_value.object_type) + "," + str(self.new_value.object_name)
        else:
            message += str(self.new_value)

        return message


"""
# decodes an encoded event. This serves as an example and isn't utilized on the server's side
def decode_event(string):
    data = string.split(",")
    ident = int(data[0])
    object_type = data[1]
    object_name = data[2]
    attribute_name = data[3]
    new_value = None
    reference_type = None
    reference_name = None
    # determine if the attribute is a reference
    if len(data) > 5:
        reference_type = data[4]
        reference_name = data[5]
        # check to see if our reference is actually a list of references
        if reference_name.split(";") > 1:
            reference_name = [x for x in data[5].split(";") if len(x) > 0]
    elif data[4].split(";") > 1:
        new_value = [x for x in data[4].split(";") if len(x) > 0]
    else:
        new_value = data[4]
"""
