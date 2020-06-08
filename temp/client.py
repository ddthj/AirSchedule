"""
AirSchedule Client
2020

This file includes the client. The client communicates with the server to view and interact with the simulation state
"""
import time
import asyncio
import datetime
import websockets
import logging
from graphics import Gui, FlightElement, scroll_handler
from vec2 import Vec2

logging.basicConfig(level=logging.INFO)
MINUTES_WIDTH = 4  # controls how compressed the time line is


class Aircraft:
    def __init__(self, string):
        data = string.split(",")
        self.name = data[1]
        self.tail_number = data[2]
        self.element = None


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
        self.element = None

    def resolve_reference(self, aircraft):
        for item in aircraft:
            if item.name == self.aircraft:
                self.aircraft = item

    def get_color(self):
        if self.status == "scheduled":
            return 50, 160, 160
        elif self.status == "outgate":
            return 50, 200, 200
        elif self.status == "offground":
            return 50, 160, 68
        elif self.status == "onground":
            return 50, 109, 160
        elif self.status == "ingate":
            return 78, 104, 128
        else:
            return 0, 0, 0

    def create_element(self, gui, index):
        box_width = (self.arri_time - self.dept_time).total_seconds() / 60
        box_start = (gui.default_time - self.dept_time).total_seconds() / 60
        self.element = FlightElement(
            size=Vec2(box_width * MINUTES_WIDTH, 35),
            padding=Vec2(100 - (box_start * MINUTES_WIDTH), (1+index*35)),
            color=self.get_color(),
            text=self.name,
            font=gui.font_25,
            dept_text=self.dept_loc,
            dept_time=str(self.dept_time.time())[0:5],
            arri_text=self.arri_loc,
            arri_time=str(self.arri_time.time())[0:5],
            side_font=gui.font_15,
            handlers=[scroll_handler]
        )
        return self.element

    def update_element(self, client):
        self.element.dept_text = self.dept_loc
        self.element.dept_time = str(self.dept_time.hour)
        self.element.arri_text = self.arri_loc
        self.element.arri_time = str(self.arri_time.hour)
        self.element.color = self.get_color()
        self.element.padding = Vec2(self.element.padding[0], (client.objects["aircraft"].index(self.aircraft) + 1) * 35)
        self.element.prep_side_text()


class Client:

    def __init__(self):
        self.pending_events = []
        self.events = []
        self.running = True
        self.objects = {"aircraft": [], "flight": []}
        self.time = None
        self.need_setup = True
        self.gui = Gui()
        self.gui.connecting_page()
        self.gui.update(self)

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
        self.need_setup = False

        # GUI needs a start time, so we use the current sim time
        self.gui.default_time = self.time
        self.gui.schedule_page(self)

    async def consume(self, ws):
        while self.running:
            try:
                data = await ws.recv()
                if self.need_setup:
                    await self.setup(data)
                else:
                    logging.info(data)
            except websockets.exceptions.ConnectionClosed:
                logging.info("Connection Closed")
                break
            await asyncio.sleep(.001)

    async def produce(self, ws):
        while self.running:
            self.gui.update(self)
            if self.gui.quit:
                self.running = False
            if len(self.pending_events) > 0:
                pass
            await asyncio.sleep(.001)

    async def run(self):
        try:
            async with websockets.connect("ws://localhost:51010") as ws:
                logging.info("Connected!")
                consume_task = asyncio.create_task(self.consume(ws))
                produce_task = asyncio.create_task(self.produce(ws))
                await asyncio.wait([consume_task, produce_task], return_when=asyncio.FIRST_COMPLETED)
        except OSError as e:
            logging.info(e)
            self.gui.connecting_failed_page()
            self.gui.update(self)
            time.sleep(1.75)
        except Exception as e:
            logging.info(e)


if __name__ == "__main__":
    x = Client()
    asyncio.run(x.run())
