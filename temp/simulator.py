"""
AirSchedule Simulator
2020

This file contains the simulator class, which handles events that occur
as the scenario is played through

It also contains handlers and utilities for managing the SimObjects provided
by the parser
"""
from setup import get_objects_from_file
from datetime import datetime, timedelta
from exceptions import *
from event import Event, EVENT_ID_GENERATOR


# Converts a string to a datetime object
# Includes error handling
def convert_datetime(string_time):
    try:
        return datetime.fromisoformat(string_time)
    except:
        raise TimeNotISOException(string_time)


# simObject flights store their departure/arrival times in a string
# When we import them here, we want to convert the string to a datetime
def init_flight(flight, date):
    flight.dept_time = convert_datetime(flight.dept_time)
    flight.arri_time = convert_datetime(flight.arri_time)
    update_flight_status(flight, date)


# Same for the scenario's current date
def init_scenario(scenario):
    scenario.date = convert_datetime(scenario.date)
    try:
        scenario.timescale = float(scenario.timescale)
    except Exception:
        raise BadFormatException(scenario.timescale)


# Sets the status of the flight. Returns a list of events if status was changed
# Could be expanded to incorporate delays, breakdowns, etc
def update_flight_status(flight, time):
    flag = False
    events = []
    # If the flight was just imported by the parser, it won't have a status
    # So first we check to see if it has the status attribute and add it as necessary
    if hasattr(flight, "status"):
        temp = flight.status
    else:
        temp = "scheduled"
        flag = True

    if time <= flight.dept_time:
        flight.status = "scheduled"
    elif flight.dept_time < time <= flight.dept_time + timedelta(minutes=10):
        flight.status = "outgate"
    elif flight.dept_time + timedelta(minutes=10) < time <= flight.arri_time - timedelta(minutes=10):
        flight.status = "offground"
    elif flight.arri_time - timedelta(minutes=10) < time <= flight.arri_time:
        flight.status = "onground"
    else:
        flight.status = "ingate"

    if not (flight.status == temp or flag):
        events.append(Event(EVENT_ID_GENERATOR.get(), flight, "status", temp, flight.status))
        if flight.status == "offground":
            # Flight has left the depart location, we need another event to remove it from that location's aircraft
            temp_aircraft = flight.dept_loc.aircraft[:]
            temp_aircraft.remove(flight.aircraft)
            events.append(
                Event(EVENT_ID_GENERATOR.get(), flight.dept_loc, "aircraft", flight.dept_loc.aircraft, temp_aircraft))
        if flight.status == "onground":
            temp_aircraft = flight.arri_loc.aircraft[:] + [flight.aircraft]
            events.append(Event(EVENT_ID_GENERATOR.get(), flight.arri_loc, "aircraft", flight.arri_loc.aircraft[:],
                                temp_aircraft))
            flight.arri_loc.aircraft.append(flight.aircraft)

    return events


# The simulator class handles anything simulated
# The passing of time, flights, etc
# A handler should be created for every type of simObject you want to simulate
class Simulator:
    def __init__(self):
        self.objects = get_objects_from_file("ReadMe.scn")

        # ensuring a scenario is defined
        if self.objects.get("scenario"):
            # Custom setup for the scenario object(s):
            for scenario in self.objects["scenario"]: init_scenario(scenario)
        else:
            raise NoScenarioFoundException
        # Custom setup for the flight objects
        for flight in self.objects["flight"]: init_flight(flight, self.objects["scenario"][0].date)

    # returns a desired object given the type and name
    def get_object(self, object_type, object_name):
        for item in self.objects[object_type]:
            if item.object_name == object_name:
                return item
        return None

    # takes a timedelta object and runs a tick of simulation
    def tick(self, dt):
        events = [
            Event(EVENT_ID_GENERATOR.get(),
                  self.objects["scenario"][0],
                  "date",
                  self.objects["scenario"][0].date.isoformat(),
                  (self.objects["scenario"][0].date + dt).isoformat()
                  )
        ]
        self.objects["scenario"][0].date += dt

        for flight in self.objects["flight"]:
            events += update_flight_status(flight, self.objects["scenario"][0].date)
        # it's the job of the server to handle these events
        return events
