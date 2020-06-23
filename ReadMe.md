Airschedule is a program that allows for the configuration, simulation, and management of an airline's aircraft and flights.
Currently it is very simple, and only allows dispatchers to modify the scheduled departure times for a given flight, or switch a flight from one aircraft to another.

Any number of clients (dispatch stations) can be connected to the server and modify the schedule.

# Installation
1. Install Python 3.7.x on the server and client computers
2. Install the necessary python libraries with ```pip install requirements.txt```
3. Clone/Download this repo onto the client/server computers
4. You may need to open a network port/configure security settings. Airschedule operates on port 51010
5. On the server computer, Modify Readme.scn to create a scenario of choice. There isn't currently an option to load a scenario with a different name.

# Usage
1. Server should run server.py. 
2. Clients should run client.py. A GUI will load and display the schedule page once connected.
3. Clients can click and drag flights in 5 minute increments horizontally, or between aircraft vertically.
4. Clients can double-click and drag to select and move an entire line of flights.

# Screenshots

![](https://github.com/ddthj/AirSchedule/blob/master/Picture%201.PNG?raw=True)
![](https://github.com/ddthj/AirSchedule/blob/master/Gif%201.gif?raw=true)
