import sys
import asyncio
import websockets
from objects import *
from graphics import *
import logging

def strip_update(item,head_length=2):
    return "".join(x + "," for x in item.split(",")[head_length:])[:-1]

class client:
    def __init__(self):
        self.updates = []
        self.pending_updates = []
        self.gui = gui()
        self.running = True
        self.objects = {"scenario":[],"aircraft":[],"flight":[]}
        self.mouse = (0,0)

    async def consume(self,ws):
        while self.running:
            try:
                new_items = False
                inbound = await ws.recv()
                for item in inbound.split(";"):
                    if item.startswith("aircraft"):
                        self.objects["aircraft"].append(aircraft(item))
                        new_items = True
                    elif item.startswith("flight"):
                        self.objects["flight"].append(flight(item))
                        new_items = True
                    elif item.startswith("scenario"):
                        self.objects["scenario"].append(scenario(item))
                        new_items = True
                    elif item.startswith("ud"):
                        self.updates.append(item)
                        data = item.split(",")
                        if data[2] == "aircraft":
                            for j in self.objects["aircraft"]:
                                if j.id == data[3]:
                                    j.decode(strip_update(item))
                                    break
                        elif data[2] == "flight":
                            for j in self.objects["flight"]:
                                if j.id == data[3]:
                                    j.decode(strip_update(item))
                                    break
                        elif data[2] == "scenario":
                            temp = scenario(strip_update(item))
                            self.objects["scenario"] = [temp]
                if new_items == True:
                    self.gui.update(self,mode="flights_by_aircraft")

            except websockets.exceptions.ConnectionClosed:
                break
            
    async def produce(self,ws):
        self.gui.update(self,mode="flights_by_aircraft")
        while self.running:
            if self.gui.quit:
                self.running = False
            self.gui.update(self)
            if len(self.pending_updates) > 0:
                msg = ""
                while len(self.pending_updates) > 0:
                    msg +=  self.pending_updates.pop() + ";"
                #print(msg)
                await ws.send(msg)
            await asyncio.sleep(.001)

    async def run(self):
        try:
            async with websockets.connect("ws://localhost:51010") as ws:
                consume_task = asyncio.create_task(self.consume(ws))
                produce_task = asyncio.create_task(self.produce(ws))
                await asyncio.wait([consume_task,produce_task],return_when=asyncio.FIRST_COMPLETED)
        except OSError:
            self.gui.update(self,mode="load",msg="Connection Failed")
            while not self.gui.quit:
                self.gui.update(self)
            self.gui.update(self)


x = client()
asyncio.run(x.run())
