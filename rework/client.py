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
        while self.running:
            if self.gui.quit:
                self.running = False
            self.gui.update()
            await asyncio.sleep(.001)

    async def run(self):
        async with websockets.connect("ws://localhost:51010") as ws:
            consume_task = asyncio.create_task(self.consume(ws))
            produce_task = asyncio.create_task(self.produce(ws))
            await asyncio.wait([consume_task,produce_task],return_when=asyncio.FIRST_COMPLETED)

        self.gui.update(mode="load",msg="Connection Failed")
        self.gui.update()

x = client()
asyncio.run(x.run())
