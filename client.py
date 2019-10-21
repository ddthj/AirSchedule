import asyncio
import websockets
from objects import *
from graphics import gui


class client:
    def __init__(self):
        self.scn = scenario([],[],[],[],[],[],[])
        self.gui = gui(self.scn)

    async def consume(self,ws):
        while True:
            inbound = await ws.recv()
            print("got msg from server.")
            if len(inbound) > 200:
                self.scn.decode(inbound)
                print("decoded scn")
            else:
                print(inbound)

    async def produce(self,ws):
        while True:
            await asyncio.sleep(.001)
            messages = self.gui.update()
            for message in messages:
                print("sending this to server:", repr(message))
                await ws.send(message)

    async def run(self):
        async with websockets.connect("ws://localhost:51010") as ws:
            consume_task = asyncio.create_task(self.consume(ws))
            produce_task = asyncio.create_task(self.produce(ws))
            await produce_task
            await consume_task

x = client()
asyncio.run(x.run())
