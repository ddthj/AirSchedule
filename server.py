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
        self.parser = parser("scenarios/AOC Schedule.scn")
        self.scn = self.parser.parse()
        self.clients = []

    async def broadcast_scenario(self):
        msg = self.scn.encode()
        for client in self.clients:
            await client.ws.send(msg)

    async def join(self, user):
        if user not in self.clients:
            self.clients.append(user)
            await user.ws.send(self.scn.encode())

    async def leave(self, user):
        self.clients.remove(user)

    async def handler(self, websocket, path):
        user = client(websocket)
        print('user joined: ', websocket, path)
        assert path == '/'
        try:
            await self.join(user)
            async for message in websocket:
                print(message)
                await websocket.send(message)
        finally:
            await self.leave(user)
            await websocket.close()



async def main():
    server = simulator()
    server = await websockets.serve(server.handler, 'localhost', 51010)
    await server.wait_closed()

asyncio.run(main())
