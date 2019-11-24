import asyncio
import websockets
import logging
from setup import *
from objects import *
import time
#Airschedule Server

class simulator:
    def __init__(self):
        self.objects = parse(read("AOC Schedule.scn"),["scenario","flight","aircraft"])
        self.scenario = self.objects["scenario"][0]
        self.clients = []
        self.updates = []
        self.update_number = 0
        self.last = time.time()
        
    async def run(self):
        while True:
            await asyncio.sleep(.001)
            if time.time() > self.last + self.scenario.timescale:
                self.last = time.time()
                self.scenario.time += 5
                #TODO- create update string
                #await self.send_update()
            #TODO - send updates
            for item in self.objects["flight"]:
                if self.scenario.time <= item.departure_time - 10 and item.status != "scheduled":
                    item.status = "scheduled"
                elif self.scenario.time > item.departure_time - 10 and self.scenario.time <= item.departure_time and item.status != "outgate":
                    item.status = "outgate"
                elif self.scenario.time > item.departure_time and self.scenario.time <= item.arrival_time-10 and item.status != "offground":
                    item.status = "offground"
                elif self.scenario.time > item.arrival_time-10 and self.scenario.time <= item.arrival_time and item.status != "onground":
                    item.status = "onground"
                elif self.scenario.time > item.arrival_time and item.status != "ingate":
                    item.status = "ingate"
    
    async def send_update(self,update):
        message = "ud,"+str(self.update_number)+","+update
        self.updates.append(message)
        self.update_number += 1
        for ws in self.clients:
            await ws.send(message)

    async def join(self, ws):
        if ws not in self.clients:
            self.clients.append(ws)
            await ws.send(self.scenario.encode() + ";"+"".join(x.encode() +";" for x in self.objects["aircraft"])+";"+"".join(x.encode() +";" for x in self.objects["flight"]))

    async def leave(self, ws):
        self.clients.remove(ws)

    async def handler(self, websocket, path):
        print('user joined: ', websocket, path)
        try:
            await self.join(websocket)
            async for message in websocket:
                print(message)
        except websockets.ConnectionClosed:
            print("user left improperly: ",websocket)            
        finally:
            print('user left: ', websocket, path)
            await self.leave(websocket)
            websocket.close()

async def main():
    server = simulator()
    await websockets.serve(server.handler, 'localhost', 51010)
    await server.run()
    await server.wait_closed()
asyncio.run(main())
