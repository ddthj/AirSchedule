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

        # # TODO: Do this as a unit test. It's currently broken.
        # scn2 = scenario([],[],[],[],[],[],[])
        # scn2.decode(self.scn.encode())
        # assert scn2.encode() == self.scn.encode()

    def add_message(self, msg: str):
        assert 'fake message' in msg
        print ('processing message: ', msg)

class simulatorserver:
    def __init__(self, sim):
        self.sim = sim
        self.clients = []

    async def broadcast_scenario(self):
        msg = self.sim.scn.encode()
        for client in self.clients:
            await client.ws.send(msg)

    async def join(self, user):
        if user not in self.clients:
            self.clients.append(user)
            await user.ws.send(self.sim.scn.encode())

    async def leave(self, user):
        self.clients.remove(user)

    async def handler(self, websocket, path):
        user = client(websocket)
        print('user joined: ', websocket, path)
        assert path == '/'
        try:
            await self.join(user)
            async for message in websocket:
                self.sim.add_message(message)
                await self.broadcast_scenario()
        finally:
            await self.leave(user)
            websocket.close()



async def main():
    server = simulatorserver(simulator())
    server = await websockets.serve(server.handler, 'localhost', 51010)
    await server.wait_closed()

asyncio.run(main())
