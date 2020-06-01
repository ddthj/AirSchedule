"""
AirSchedule Client
2020

This file includes the client. The client communicates with the server to view and interact with the simulation state
"""
import asyncio
import datetime
import websockets
import logging

logging.basicConfig(level=logging.INFO)


class Aircraft:
    def __init__(self, string):
        data = string.split(",")
        self.name = data[1]
        self.tail_number = data[2]
        self.box = None


class Flight:
    def __init__(self, string):
        data = string.split(",")
        self.name = data[1]
        self.dept_loc = data[2]
        self.arri_loc = data[3]
        self.dept_time = datetime.datetime.fromisoformat(data[4])
        self.arri_time = datetime.datetime.fromisoformat(data[5])
        self.aircraft = data[6]
        self.status = data[7]
        self.box = None

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
        # whether or not we have parsed the sim state
        self.ready = False

    async def setup(self, state):
        blocks = state.split("`")
        self.time = datetime.datetime.fromisoformat(blocks[0])
        for i in range(1, len(blocks)):
            if blocks[i].startswith("aircraft"):
                self.objects["aircraft"].append(Aircraft(blocks[i]))
            elif blocks[i].startswith("flight"):
                self.objects["flight"].append(Flight(blocks[i]))

        for flight in self.objects["flight"]:
            flight.resolve_reference(self.objects["aircraft"])

        logging.info("parsed %s aircraft and %s flights" % (len(self.objects["aircraft"]), len(self.objects["flight"])))
        first = self.objects["flight"][0]
        logging.info("flight %s has linked to aircraft %s" % (first.name, first.aircraft.name))
        self.ready = True

    async def consume(self, ws):
        while self.running:
            try:
                data = await ws.recv()
                if not self.ready:
                    await self.setup(data)
                else:
                    logging.info(data)
            except websockets.exceptions.ConnectionClosed:
                logging.info("Connection Closed")
                break

            await asyncio.sleep(.001)

    async def produce(self, ws):
        while self.running:
            if len(self.pending_events) > 0:
                pass
            await asyncio.sleep(.001)

    async def run(self):
        try:
            async with websockets.connect("ws://localhost:51010") as ws:
                logging.info("connected!")
                consume_task = asyncio.create_task(self.consume(ws))
                produce_task = asyncio.create_task(self.produce(ws))
                await asyncio.wait([consume_task, produce_task], return_when=asyncio.FIRST_COMPLETED)
        except OSError:
            logging.info("oopsie")
        except Exception as e:
            logging.info(e)


if __name__ == "__main__":
    x = Client()
    asyncio.run(x.run())
