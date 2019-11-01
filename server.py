import asyncio
import websockets
import logging
from setup import parser
from objects import *
import time

class client:
    def __init__(self,websocket):
        self.ws = websocket

class simulator:
    def __init__(self):
        self.parser = parser("scenarios/AOC Schedule.scn")
        self.scn = self.parser.parse()
        self.clients = []
        self.updates = []
        self.update_number = 0
        self.timescale = 2
        self.last = time.time()
        
    async def run(self):
        while True:
            await asyncio.sleep(.001)
            if time.time() > self.last + self.timescale:
                self.last = time.time()
                self.scn.time += 5
                time_update = update(self.update_number,"ut,5")
                self.updates.append(time_update)
                self.update_number += 1
                await self.send_update(time_update)
                print(time_update.encode())

            for f in self.scn.flights:
                if self.scn.time > f.departure_time - 10 and self.scn.time <= f.departure_time:
                    if f.status != "outgate":
                        f.status = "outgate"
                        f_update = update(self.update_number,"uf," + str(f.ref) + "," + "status,"+ "outgate")
                        self.updates.append(f_update)
                        self.update_number += 1
                        await self.send_update(f_update)
                elif self.scn.time > f.departure_time and self.scn.time <= f.arrival_time - 10:
                    if f.status != "offground":
                        f.status = "offground"
                        f_update = update(self.update_number,"uf," + str(f.ref)+ "," + "status,"+ "offground")
                        self.updates.append(f_update)
                        self.update_number += 1
                        await self.send_update(f_update)
                elif self.scn.time > f.arrival_time - 10 and self.scn.time <= f.arrival_time:
                    if f.status != "onground":
                        f.status = "onground"
                        f_update = update(self.update_number,"uf," + str(f.ref) + "," + "status,"+ "onground")
                        self.updates.append(f_update)
                        self.update_number += 1
                        await self.send_update(f_update)
                elif self.scn.time > f.arrival_time:
                    if f.status != "ingate":
                        f.status = "ingate"
                        f_update = update(self.update_number,"uf," + str(f.ref) + "," + "status,"+ "ingate")
                        self.updates.append(f_update)
                        self.update_number += 1
                        await self.send_update(f_update)
                elif self.scn.time <= f.departure_time - 10 and f.status != "scheduled":
                    f.status = "scheduled"
                    f_update = update(self.update_number,"uf," + str(f.ref) + "," + "status,"+ "scheduled")
                    self.updates.append(f_update)
                    self.update_number += 1
                    await self.send_update(f_update)
                    
                    
    
    async def send_update(self,update):
        for c in self.clients:
            await c.ws.send(update.encode())

    async def join(self, user):
        if user not in self.clients:
            self.clients.append(user)
            await user.ws.send(self.scn.encode())

    async def leave(self, user):
        self.clients.remove(user)

    async def handler(self, websocket, path):
        user = client(websocket)
        print('user joined: ', websocket, path)
        assert path == '/'
        try:
            await self.join(user)
            async for message in websocket:
                print(message)
                if message.find("timescale") != -1:
                    self.timescale = float(message.split("timescale")[1])
                elif message.find("time") != -1:
                    time = int(message.split("time")[1])
                    minutes = (time//100 * 60) + time % 100
                    delta = minutes - self.scn.time
                    self.scn.time = minutes
                    time_update = update(self.update_number,"ut,%s"%delta)
                    self.updates.append(time_update)
                    self.update_number += 1
                    await self.send_update(time_update)
                await websocket.send(message)
        finally:
            await self.leave(user)
            await websocket.close()

async def main():
    server = simulator()
    await websockets.serve(server.handler, 'localhost', 51010)
    await server.run()
    await server.wait_closed()

asyncio.run(main())
