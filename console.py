import asyncio
import websockets
from objects import *

class client:
    async def produce(self,ws):
        while True:
            await asyncio.sleep(.001)
            msg = input(">")
            if msg == "help":
                print("no")
            elif msg.find("timescale") != -1:
                msg = msg.split(" ")
                await ws.send(msg[0]+msg[1])
            elif msg.find("time") != -1:
                msg = msg.split(" ")
                await ws.send(msg[0]+msg[1])
                

    async def run(self):
        async with websockets.connect("ws://localhost:51010") as ws:
            produce_task = asyncio.create_task(self.produce(ws))
            await produce_task
            await consume_task

x = client()
asyncio.run(x.run())
