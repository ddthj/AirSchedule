"""
AirSchedule Client
2020

This file includes the client. The client communicates with the server to view and interact with the simulation state
"""
import asyncio
import datetime
import websockets


class Aircraft:
    def __init__(self, string):
        data = string.split(",")
        self.name = data[1]
        self.tail_number = data[2]


class Flight:
    def __init__(self, string):
        data = string.split(",")
        self.name = data[1]
        self.dept_loc = data[2]
        self.arri_loc = data[3]
        self.dept_time = datetime.datetime.fromisoformat(data[4])
        self.arri_time = datetime.datetime.fromisoformat(data[5])
        self.aircraft = data[6]

    def resolve_reference(self, aircraft):
        for item in aircraft:
            if item.name == self.aircraft:
                self.aircraft = item


class Client:

    def __init__(self):
        self.pending_events = []
        self.events = []
        self.running = True
        self.objects = {"aircraft": [], "flight": []}
        self.time = None

    async def setup(self, state):
        blocks = state.split("`")
        self.time = datetime.datetime.fromisoformat(blocks[0])

    async def consume(self, ws):
        while self.running:
            try:
                data = await ws.recv()
            except websockets.exceptions.ConnectionClosed:
                break

    async def produce(self, ws):
        while self.running:
            if len(self.pending_events) > 0:
                pass

    async def run(self):
        try:
            async with websockets.connect("ws://localhost:51010") as ws:
                consume_task = asyncio.create_task(self.consume(ws))
                produce_task = asyncio.create_task(self.produce(ws))
                await asyncio.wait([consume_task, produce_task], return_when=asyncio.FIRST_COMPLETED)
        except OSError:
            print("oopsie")


if __name__ == "__main__":
    x = Client()
    x.run()
