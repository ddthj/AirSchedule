"""
AirSchedule Exceptions
2020

This file holds all the exceptions that AirSchedule throws
Typically in response to a misconfigured .scn file
"""

#If the create_simObject() can't determine a certain line of the scn file
#it will raise a MalformedScnException that points to the problem
class MalformedScnException(Exception):
    def __init__(self, context, line):
        self.context = context
        self.line = line
        self.message = "\n\n" + "".join(x + "\n" for x in self.context) + "\n" + str(self.context[self.line]) + " <--"
    def __str__(self):
        return self.message

#Raised if the parser can't find the object required to resolve a reference
class ObjectNotFoundException(Exception):
    def __init__(self,objectType,objectName):
        self.message = "\n\nCould not find type '%s' named '%s'\nWas the wrong type provided or the object not defined?" % (objectType, objectName)
    def __str__(self):
        return self.message
    
#This can be thrown when trying to convert a time string in the scn file into a datetime object
class TimeNotISOException(Exception):
    def __init__(self,time):
        self.message = "\n\nThe time '%s' could not be parsed, is it in ISO 8601?" % (time)
    def __str__(self):
        return self.message

#A generic error when a variable in the scn file isn't what it's supposed to be
class BadFormatException(Exception):
    def __init__(self, problem):
        self.message = "\n\nThe data '%s' could not be parsed" % (problem)
    def __str__(self):
        return self.message

#This is raised by  the parser if it fines two objects with the same type and name, which would break the simulator
class ObjectDefinedTwiceException(Exception):
    def __init__(self,temp_object):
        self.message = "\n\nThe object '%s %s' is defined twice" % (temp_object.objectType,temp_object.objectName)
    def __str__(self):
        return self.message

class NoScenarioFoundException(Exception):
    def __init__(self):
        self.message = "\n\nNo object with type 'scenario' could be found. One must be defined"
    def __str__(self):
        return self.message
    
