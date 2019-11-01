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
                s = inbound.split(",")

                if s[0] == "ud":
                    ud = update(int(s[1]),s[2:])
                    self.updates.append(ud)
                    if ud.change[0] == "ut":
                        self.scn.time += int(ud.change[1])
                    elif ud.change[0] == "uf":
                        for f in self.scn.flights:
                            if f.ref == ud.change[1]:
                                if ud.change[2] == "status":
                                    f.status = ud.change[3]
                                    break

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
