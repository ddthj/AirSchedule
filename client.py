import asyncio
import concurrent.futures
import websockets
from objects import *
from graphics2 import gui


class client:
    def __init__(self):
        self.scn = scenario([],[],[],[],[],[],[])
        self.gui = gui(self.scn)

    async def consume(self,ws):
        try:
            c = 0
            while True:
                print(c)
                inbound = await ws.recv()
                if c < 1:
                    self.scn.decode(inbound)
                else:
                    print(inbound)
                c+= 1
                print(c)
        finally:
            print("done")
   
    async def produce(self,ws):
        while True:
            messages = self.gui.update()
            if len(messages) > 0:
                for message in messages:
                    await ws.send(message)

    async def run(self):
        async with websockets.connect("ws://localhost:51010") as ws:
            consume_task = asyncio.create_task(self.consume(ws))
            produce_task = asyncio.create_task(self.produce(ws))
            await produce_task
            await consume_task
       
x = client()
asyncio.run(x.run())

