"""
AirSchedule Parser
2020

This file parses .scn files for the AirSchedule program
The included ReadMe.scn contains information on how to format .scn files
"""


# generates id's for the program to use internally
from exceptions import MalformedScnException, ObjectNotFoundException


class IdGen:
    def __init__(self):
        self.current_id = 0

    def get(self):
        self.current_id += 1
        return self.current_id


ID_GENERATOR = IdGen()


# Opens the file and read each line into a list
# Ignores lines with // and empty lines
def get_lines(file_name):
    try:
        with open(file_name, "r") as file:
            # Strips trailing whitespace, and ignores empty lines or lines with "//"
            raw = [line.rstrip() for line in file if len(line.strip()) > 0 and line.find("//") == -1]
        return raw
    except Exception as e:
        print("Couldn't read '%s', %s" % (file_name, e))
        return []


# This separates individual objects in the scn file into their own lists
def get_raw_objects(lines):
    raw_objects = []
    i = 0
    j = 1
    for j in range(1, len(lines)):
        if not lines[j].startswith("\t"):
            raw_objects.append([line.strip() for line in lines[i:j]])
            i = j
    raw_objects.append([line.strip() for line in lines[i:j + 1]])
    return raw_objects


# Takes a list of scn file lines that describe a single object
# and returns an instance of a simOjbect
# Primarily for childproofing
def create_simobject(raw_object):
    new_ident = ID_GENERATOR.get()
    definition = raw_object[0].split(" ")
    attributes = []
    if len(definition) == 2:
        # Getting type and name from top of object
        object_type, object_name = definition
        # iterating through the attributes
        for i in range(1, len(raw_object)):
            attribute = raw_object[i].split(" ")
            if len(attribute) == 2 or len(attribute) == 3:
                attributes.append(attribute)
            else:
                raise MalformedScnException(raw_object, i)
        return SimObject(new_ident, object_type, object_name, attributes)
    else:
        raise MalformedScnException(raw_object, 0)


# A simObject is created for every object/instance defined within the scn file
# This allows the program to handle any type of object that is defined
class SimObject:
    def __init__(self, ident, object_type, object_name, attributes):
        # The "Type" and name as defined in the scn file
        self.object_type = object_type
        self.object_name = object_name

        # This is an internal object id that's used by the simulator
        self.ident = ident

        # Used to tell the parser what attributes are references
        self.references = []

        for attribute in attributes:
            if len(attribute) == 3:
                # Creating an attribute and temporarily assigning it to the type and name of the reference
                # Instead of the reference itself
                if len(attribute[2].split(",")) > 1:
                    # If the attribute is a list we create that now
                    self.__setattr__(attribute[0], (attribute[1], [x for x in attribute[2].split(",") if len(x) > 0]))
                else:
                    # Attribute isn't a list
                    self.__setattr__(attribute[0], (attribute[1], attribute[2]))

                self.references.append(attribute[0])
            else:
                if len(attribute[1].split(",")) > 1:
                    self.__setattr__(attribute[0], [x for x in attribute[1].split(",") if len(x) > 0])
                else:
                    self.__setattr__(attribute[0], attribute[1])


# This searches for all objects that have references to other objects, and ensures they are properly linked
def resolve_references(objects):
    for item in sum(objects.values(), []):
        for attributeName in item.references:
            # The temporary attribute is a tuple containing the type and the name of the object to be referenced
            reference_type, reference_name = item.__getattribute__(attributeName)
            # The "name" can be a list of names, so we check for that here
            if isinstance(reference_name, list):
                item.__setattr__(attributeName, [find_object(objects, reference_type, name) for name in reference_name])
            else:
                item.__setattr__(attributeName, find_object(objects, reference_type, reference_name))


# This returns an object given its type and name
def find_object(objects, object_type, object_name):
    # Unused, This allows a reference in the scn file to point nowhere.
    if object_name == "NULL":
        return None
    for item in objects[object_type]:
        if item.object_name == object_name:
            return item
    raise ObjectNotFoundException(object_type, object_name)


# This is the main function of this file.
# It reads and parses the given scn file and returns all objects within the file
def get_objects_from_file(filename):
    objects = {}
    # Read the file
    raw_lines = get_lines(filename)
    if len(raw_lines) > 0:
        # Split the file up by object
        raw_objects = get_raw_objects(raw_lines)
        # Create simObjects
        for item in raw_objects:
            temp = create_simobject(item)
            # If the object type already exists, add this object to the list of others
            # Otherwise, create a new list within the dict for this objecttype
            if objects.get(temp.object_type):
                objects[temp.object_type].append(temp)
            else:
                objects[temp.object_type] = [temp]

        # After the object list has been created, any references within the objects themselves must be resolved
        resolve_references(objects)
        return objects
    return None
