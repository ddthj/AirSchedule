import asyncio
import websockets
from objects import *


url = "ws://localhost:51010"
x = scenario([],[],[],[],[],[],[])

async def join():
    async with websockets.connect(url) as ws:
        await ws.send("join")
        x.decode(await ws.recv())

asyncio.get_event_loop().run_until_complete(join())
