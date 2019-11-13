from objects import *
#Airschedule Parser
#Reads Scenario files into an organization of dictionaries that makes object creation simple

#generates id's for the program to use internally 
class id_gen:
    def __init__(self,object_types):
        self.count = {object_type:0 for object_type in object_types}
    def get(self,object_type):
        self.count[object_type] += 1
        return str(self.count[object_type])
        
def read(file):
    #Open the file and read each line into a list
    #Ignores lines with leading '/' and empty lines
    with open(file,"r") as f:
        raw = [line for line in f if len(line.strip()) > 0 and line[0] != "/"]

    #Finds object types by looking at all lines without a leading \t
    object_types = []
    for item in raw:
        if not item.startswith("\t") and item.split(" ")[0] not in object_types:
            object_types.append(item.split(" ")[0])

    #Creating a dict that will hold a list of each object type.
    objects = {x : [] for x in object_types}
    
    #class to keep track of object id's
    gen = id_gen(object_types)

    #Separating rawi into lists for each object 
    object_list = []
    i = 0
    for j in range(1,len(raw)):
        if not raw[j].startswith("\t"):
            object_list.append(raw[i:j])
            i=j
    object_list.append(raw[i:j+1])

    #Turning each list into a dict, and storing it correctly in the objects dict
    for item in object_list:
        most_recent_dict = None #if our object has a dict/list of items, this points to the most recently creted dict
        temp = {}
        object_type, name = item[0].strip().split(" ")
        temp["type"] = object_type
        temp["id"] = gen.get(object_type)
        temp["name"] = name
        for i in range(1,len(item)):
            data = item[i].strip().split(" ")
            #First check to see if we need to append this line to a list, based on indentation
            if item[i].startswith("\t\t"):
                #creates new dict entry if object type isn't already inside, else simply appends item to existing list
                sub_obj_type, sub_obj_name = item[i].strip().split(" ")
                if temp[most_recent_dict].get(sub_obj_type) != None:
                    temp[most_recent_dict][sub_obj_type].append(sub_obj_name)
                else:
                    temp[most_recent_dict][sub_obj_type] = [sub_obj_name]
            else:
                #Otherwise we process it as either an attribute or list definition depending on the number of args provided
                if len(data) > 1 and len(data[1]) > 0:
                    temp[data[0]] = data[1]
                else:
                    most_recent_dict = data[0]
                    temp[data[0]] = {}
        #Finally we add the temp dict to our objects dict in the right type key
        objects[object_type].append(temp)
    return objects

#turns all dict objects into python objects provided they're in the objects_types_to_parse list
#ie - won't parse cargo if you don't tell it to parse cargo
def parse(raw_objects,objects_types_to_parse):
    parsed_objects = {x : [] for x in objects_types_to_parse}
    for object_type in objects_types_to_parse:
        for item in raw_objects.get(object_type):
            if object_type == "scenario":
                temp = scenario(**item)
            elif object_type == "location":
                temp = location(**item)
            elif object_type == "flight":
                temp = flight(**item)
            elif object_type == "aircraft":
                temp = aircraft(**item)
            parsed_objects[object_type].append(temp)
    return parsed_objects
                
    
    

