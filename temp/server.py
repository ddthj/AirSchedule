"""
AirSchedule Server
2020

This file contains the server, which ticks through the simulator and updates
clients with the generated events.

It also provides the entire state of the flight objects upon request
So that new clients can populate their schedules
"""
from simulator import simulator
import asyncio
import websockets
import time
from datetime import timedelta

#Encoding the relavant state information that a client needs upon connecting
def encode_aircraft(ac):
    return "%s,%s,%s" % (ac.objectType,
                         ac.objectName,
                         ac.tail_number)

def encode_flight(fl):
    #The objectTypes of the locations/aircraft don't need to be sent
    #As this packet has a fixed structure, the attribute types don't need
    #to be sent. ie- the client knows that the third item is the name of a
    #location
    return "%s,%s,%s" % (fl.objectType,
                         fl.objectName,
                         fl.dept_loc.objectName,
                         fl.arri_loc.objectName,
                         fl.dept_time.isoformat(),
                         fl.arri_time.isoformat(),
                         fl.aircraft.objectName)
                         

class server:
    def __init__(self):
        self.sim = simulator()
        #the websocket connection for every client
        self.clients = []
        #A history of all simulator events
        self.event_history = []
        self.running = True
        #Used to control how often the server runs a tick
        #Does not affect timescale of the simulator
        self.last_tick = time.time()
        self.time_between_ticks = 1 #seconds

    #Adds a client connection to the list of clients
    async def join(self, ws):
        if ws not in self.clients:
            self.clients.append(ws)

    #Removes a client connection from the list of clients
    async def leave(self, ws):
        self.clients.remove(ws)

    #Sends a list of events to all connected clients
    async def send_events(self, events):
        for event in events:
            for ws in self.clients:
                try:
                    #Encode and send event
                    await ws.send(event.encode())
                except:
                    print("failed to send %s to %s"%(event.encode(),ws))
        print("sent %s events to %s clients" % (len(events),len(self.clients)))

    #Sends pertinent information about the simulation state to a given client
    #Information includes: current event #, date, aircraft, flights
    async def send_state(self,ws):
        #Message begins with the current date, followed by a ` to separate data
        message = self.sim.objects["scenario"][0].date.isoformat() + "`"
        for aircraft in self.sim.objects["aircraft"]:
            message += encode_aircraft(aircraft) + "`"
        for flight in self.sim.objects["flight"]:
            message += encode_flight(flight) + "`"

        try:
            ws.send(message)
        except Exception as e:
            
            print("Failed to send state to client, ",e)        

    #Handles client connections as they are created
    async def handler(self, ws, path):
        print('user joined: ', websocket, path)
        try:
            await self.join(ws)
            async for message in ws:
                print(message)
        except websockets.ConnectionClosed:
            print("user left improperly: ",websocket)
        finally:
            await self.leave(ws)
            ws.close()

    #The main loop that runs the simulation
    async def main(self):
        websockets.serve(self.handler, 'localhost', 51010)
        while self.running:
            if time.time() - self.time_between_ticks > self.last_tick:
                self.last_tick = time.time()
                dt = timedelta(seconds=(self.time_between_ticks * self.sim.objects["scenario"][0].timescale))
                events = self.sim.tick(dt)
                self.event_history += events
                await self.send_events(events)

x = server()
asyncio.run(x.main())
