import asyncio
import websockets
from objects import *
from graphics2 import gui



scn = scenario([],[],[],[],[],[],[])
gui = gui(scn)

async def connect():
    async with websockets.connect("ws://localhost:51010") as ws:
        await ws.send("join")
        scn.decode(await ws.recv())
        
        
asyncio.get_event_loop().run_until_complete(connect())

while gui.run:
    gui.update()
