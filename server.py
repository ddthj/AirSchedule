"""
AirSchedule Server
2020

This file contains the server, which ticks through the simulator and updates
clients with the generated events.

It also provides the entire state of the flight objects upon request
So that new clients can populate their schedules
"""
from simulator import Simulator
import asyncio
import websockets
import time
from datetime import timedelta, datetime
from event import Event, EVENT_ID_GENERATOR


# Encoding the relevant state information that a client needs upon connecting
def encode_aircraft(ac):
    return "%s,%s,%s" % (ac.object_type,
                         ac.object_name,
                         ac.tail_number)


def encode_flight(fl):
    # The object_type's of the locations/aircraft don't need to be sent
    # As this packet has a fixed structure, the attribute types don't need
    # to be sent. ie- the client knows that the third item is the name of a
    # location
    return "%s,%s,%s,%s,%s,%s,%s,%s" % (fl.object_type,
                                        fl.object_name,
                                        fl.dept_loc.object_name,
                                        fl.arri_loc.object_name,
                                        fl.dept_time.isoformat(),
                                        fl.arri_time.isoformat(),
                                        fl.aircraft.object_name,
                                        fl.status)


class Server:
    def __init__(self):
        self.sim = Simulator()
        # the websocket connection for every client
        self.clients = []
        # A history of all simulator events
        self.event_history = []
        self.running = True
        # Used to control how often the server runs a tick
        # Does not affect timescale of the simulator
        self.last_tick = time.time()
        self.time_between_ticks = 1  # seconds

    # Adds a client connection to the list of clients
    async def join(self, ws):
        if ws not in self.clients:
            self.clients.append(ws)
            await self.send_state(ws)

    # Removes a client connection from the list of clients
    async def leave(self, ws):
        self.clients.remove(ws)

    # Sends a list of events to all connected clients
    async def send_events(self, events):
        self.event_history += events
        for event in events:
            for ws in self.clients:
                try:
                    # Encode and send event
                    await ws.send(event.encode())
                except Exception as e:
                    print("failed to send %s to %s... %s" % (event.encode(), ws, e))
        print("sent %s events to %s clients" % (len(events), len(self.clients)))

    # Decodes a client request to change the sim state, and generates an event
    async def decode_request(self, request):
        data = request.split(",")
        object_type = data[0]
        object_name = data[1]
        attribute_name = data[2]
        old_value = data[3]
        new_value = data[4]

        if object_type == "flight":
            flight = self.sim.get_object(object_type, object_name)
            if attribute_name == "aircraft":
                # we check to see if the object is still how the client expected it when making the request
                if flight.aircraft.object_name != old_value:
                    # if it's not, we make the "new" value equal the current value, and send that back as an event
                    new_value = flight.aircraft.object_name
                flight.__setattr__(attribute_name, self.sim.get_object(attribute_name, new_value))
                await self.send_events([Event(EVENT_ID_GENERATOR.get(),
                                              flight,
                                              attribute_name,
                                              flight.aircraft.object_name,
                                              self.sim.get_object(attribute_name, new_value)
                                              )
                                        ])
            elif attribute_name == "arri_time" or attribute_name == "dept_time":
                if flight.__getattribute__(attribute_name).isoformat() != old_value:
                    new_value = flight.__getattribute__(attribute_name).isoformat()
                flight.__setattr__(attribute_name, datetime.fromisoformat(new_value))
                await self.send_events([Event(EVENT_ID_GENERATOR.get(),
                                              flight,
                                              attribute_name,
                                              flight.__getattribute__(attribute_name),
                                              datetime.fromisoformat(new_value)
                                              )
                                        ])

    # Sends pertinent information about the simulation state to a given client
    # Information includes: current event #, date, aircraft, flights
    async def send_state(self, ws):
        # Message begins with the current date, followed by a ` to separate data
        message = self.sim.objects["scenario"][0].date.isoformat() + "`"
        for aircraft in self.sim.objects["aircraft"]:
            message += encode_aircraft(aircraft) + "`"
        for flight in self.sim.objects["flight"]:
            message += encode_flight(flight) + "`"

        try:
            await ws.send(message)
        except Exception as e:
            print("Failed to send state to client, ", e)

    # Handles each new websocket connection in essentially a new thread
    async def handler(self, ws, path):
        print('user joined: ', ws)
        try:
            await self.join(ws)
            async for message in ws:
                print(message)
                await self.decode_request(message)
            print('user left: ', ws)
        except websockets.ConnectionClosed:
            print("user left improperly: ", ws)
        finally:
            await self.leave(ws)
            await ws.close()

    # The main loop that runs the simulation
    async def run(self):
        while self.running:
            await asyncio.sleep(.001)
            if time.time() - self.time_between_ticks > self.last_tick:
                self.last_tick = time.time()
                dt = timedelta(seconds=(self.time_between_ticks * self.sim.objects["scenario"][0].timescale))
                events = self.sim.tick(dt)
                await self.send_events(events)


async def main():
    server = Server()
    await websockets.serve(server.handler, 'localhost', 51010)
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
