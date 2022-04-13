"""
Kernal Class
"""
import numpy as np
import pandas as pd
import constants as cs

from stage_1 import Stage1

maxSimulationLength = 500 #525600 minutes = 1 year    

class Kernel():

    def __init__(self):
        print("Kernel()::__init__() is initializing some cool stuff")
        self.clock = 0

        # Event list implemented using dictionary
        self.eventList = {} 

        # Keep note of the next event chronologically to roll forward the system clock
        self.nextEventScheduleTime = 0 

        self.startup()
        self.mainLoop()

        #Operations
        self.INBOUND = Stage1()

    def startup(self):
        # TODO : make compatible with class
        ### INITIAL ARRIVAL EVENT GENERATION
        # Current clock = 0
        print("Kernel()::__init__() is starting some cool stuff")
        
        a = np.random.random()
        self.eventList[round(self.clock+a, 8)] = "... nope"
        print(self.eventList)
        self.nextEventScheduleTime = round(self.clock + a, 8)


    def mainLoop(self):
        # TODO: Needs input params
        ### THE MAIN SIMULATION LOOP STARTS HERE
        while self.clock < maxSimulationLength:
            print("Sim step!")
            self.step()


    def step(self):
        # Process next event
        
        print("Stepping Clock")
        # increment clock
        self.clock = self.clock + 5

        eventType = "None"
        if len(self.eventList.keys()):
            eventType = self.eventList.pop(self.nextEventScheduleTime)    # Get the next event while removing it from the event list

        if eventType == "DELIVERY":
            self.INBOUND.exec_delivery()
        elif eventType == "StartTreat":
            processEventStartTreat()
        elif eventType == "EndTreat":
            processEventEndTreat()
        elif eventType == "None":
            print("Nothing happened lol")
    
    
    def report(self):
        # Print metrics
        
        print("Current Clock: ".format(self.clock))
        pass


if __name__ == "__main__":
    MuhKernel = Kernel()
    print("Helloooo")
    MuhKernel.report()
