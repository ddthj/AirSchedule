import sys
import asyncio
import websockets
from objects import *
from graphics import *
import logging

class client:
    def __init__(self):
        self.updates = []
        self.gui = gui()
        self.running = True

    async def consume(self,ws):
        while self.running:
            try:
                inbound = await ws.recv()
            except websockets.exceptions.ConnectionClosed:
                break
            
    async def produce(self,ws):
        self.gui.update(mode="home")
        while self.running:
            if self.gui.quit:
                self.running = False
            self.gui.update()
            await asyncio.sleep(.001)

    async def run(self):
        try:
            async with websockets.connect("ws://localhost:51010") as ws:
                consume_task = asyncio.create_task(self.consume(ws))
                produce_task = asyncio.create_task(self.produce(ws))
                await asyncio.wait([consume_task,produce_task],return_when=asyncio.FIRST_COMPLETED)
        except OSError:
            self.gui.update(mode="load",msg="Connection Failed")
            while not self.gui.quit:
                self.gui.update()
            self.gui.update()


x = client()
asyncio.run(x.run())
