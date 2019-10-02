import asyncio
import websockets
import logging
from setup import parser
from objects import *

logging.basicConfig()

class client:
    def __init__(self,websocket):
        self.ws = websocket

class simulator:
    def __init__(self):
        self.parser = parser("scenarios/test.scn")
        self.scn = self.parser.parse()
        self.clients = []

    async def send_scenario(self):
        msg = self.scn.encode()
        for client in self.clients:
            await client.ws.send(msg)

async def join(user):
    if user not in SIM.clients:
        SIM.clients.append(user)
        await user.ws.send(SIM.scn.encode())

async def leave(user):
    SIM.clients.remove(user)

async def handler(websocket,path):
    user = client(websocket)
    print(websocket,path)
    try:
        async for message in websocket:
            if message.find("join") != -1:
                await join(user)
    finally:
        await leave(user)
        websocket.close()

SIM = simulator()
    
asyncio.get_event_loop().run_until_complete(websockets.serve(handler, 'localhost', 51010))
asyncio.get_event_loop().run_forever()
