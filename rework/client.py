import asyncio
import websockets
from objects import *
from graphics import *

class client:
    def __init__(self):
        self.updates = []
        self.gui = gui()
        self.quit = False

    async def consume(self,ws):
        while True:
            inbound = await ws.recv()
            if self.quit:
                break

    async def produce(self,ws):
        while True:
            self.gui.update()
            if self.gui.quit:
                self.quit = True
                break
            await asyncio.sleep(.001)

    async def run(self):
        try:
            async with websockets.connect("ws://localhost:51010") as ws:
                consume_task = asyncio.create_task(self.consume(ws))
                produce_task = asyncio.create_task(self.produce(ws))
                await produce_task
                await consume_task
        except:
            self.gui.update(mode="load",msg="Connection Failed")
            await self.produce(None)

x = client()
asyncio.run(x.run())
