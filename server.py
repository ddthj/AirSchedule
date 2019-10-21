import asyncio
import websockets
import logging
from setup import parser
from objects import *

class simulator:
    def __init__(self):
        self.parser = parser("scenarios/test.scn")
        self.scn = self.parser.parse()
        self.clients = []            

async def join(user):
    SIM.clients.append(user)
async def leave(user):
    SIM.clients.remove(user)
    

async def handler(websocket,path):
    await join(websocket)
    try:
        await websocket.send(SIM.scn.encode())
        try:
            async for message in websocket:
                print(message)
                await websocket.send(message)
        except:
            pass
    finally:
        await leave(websocket)

SIM = simulator()
    
asyncio.get_event_loop().run_until_complete(websockets.serve(handler, 'localhost', 51010))
asyncio.get_event_loop().run_forever()
