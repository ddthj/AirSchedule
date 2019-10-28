x = ""
mode = 2
if mode == 0:
    while x != "stop":
        x = input()
        items = x.split("\t")
        print("flight %s\n\tdeparture_location %s\n\tdeparture_time %s\n\tarrival_location %s\n\tarrival_time %s\n\taircraft %s\n\tmanifest " % (items[1],items[2],items[3],items[4],items[5],items[0]))
elif mode == 1:
    while x != "stop":
        x = input()
        items = x.split("\t")
        print("itinerary %s\n\t%s"%(items[1],items[1]))
        print("group %s\n\tquantity %s\n\titinerary %s\n\trole passenger"%(items[1],items[6],items[1]))
else:
    while x != "stop":
        x = input()
        if len(x) > 0:
            print("manifest %s\n\tgroup %s"%(x,x))
    
        
        
    
