import asyncio
import websockets
from objects import *
from graphics2 import gui


class client:
    def __init__(self):
        self.scn = scenario([],[],[],[],[],[],[])
        self.gui = gui(self.scn)
        # Note: Dom dislikes the design where gui seems to own an object which is externally mutated.

    async def consume(self,ws):
        try:
            while True:
                inbound = await ws.recv()
                print("got msg from server.")
                self.scn.decode(inbound)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            print("consume done")

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
