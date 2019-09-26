import asyncio
import websockets
from parse import *
from objects import *

class simulator:
    def __init__(self):
        self.parser = parser("scenarios/test.scn")
        self.scn = self.parser.parse()
        
