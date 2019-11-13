import asyncio
import websockets
from objects import *

class client:
    def __init__(self):
        self.updates = []

    async def consume(self,ws):
        while True:
            inbound = await ws.recv()

    async def produce(self,ws):
        while True:
            await asyncio.sleep(.001)

    async def start(self):
        pass

    async def run(self):
        async with websockets.connect("ws://localhost:51010") as ws:
            consume_task = asyncio.create_task(self.consume(ws))
            produce_task = asyncio.create_task(self.produce(ws))
            await produce_task
            await consume_task

x = client()
asyncio.run(x.start())
