import asyncio
import websockets
from objects import *
from graphics import gui


class client:
    def __init__(self):
        self.scn = scenario([],[],[],[],[],[],[],0)
        self.updates = []
        self.gui = gui(self.scn)

    async def consume(self,ws):
        while True:
            inbound = await ws.recv()
            if len(inbound) > 2000:
                self.scn.decode(inbound)
            else:
                print(inbound)
                if inbound.find("ud") != -1:
                    s = inbound.split(",")
                    ud = update(int(s[1]),s[2])
                    self.updates.append(ud)
                    if ud.change.find("time") != -1:
                        self.scn.time += int(ud.change.split("time")[1])


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
