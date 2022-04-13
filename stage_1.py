"""
Process Stage 1 Inbound simulation

    # Read incoming delivery
    # increment product counts
    # Add delivery cost
    
"""
import numpy as np
import pandas as pd
import constants as cs

class Stage1():

    def __init__(self):
        print("Kernel()::__init__() is initializing some cool stuff")
        self.clock = 0

        # Event list implemented using dictionary
        self.eventList = {} 

        self.parking = {
            'P1':0,
            'P2':0,
            'P3':0,
            'P4':0
        }

        self.cost = 0

        # Keep note of the next event chronologically to roll forward the system clock
        self.nextEventScheduleTime = 0 

        self.startup()
        self.mainLoop()
        self.report()


    def schd_delivery(self):
        # Process delivery
        a = np.random.random() * 20

        # Add Events
        self.eventList[round(self.clock+a, 8)] = "DELIVERY_SCHD"
        self.nextEventScheduleTime = round(self.clock + a, 8)

        # Accumulate Delivery Cost
        self.cost += cs.DELIVERY_COST


    def exec_delivery(self, shipment):
        # Process delivery

        # Process Shipments to Inventory Parking
        # TODO Check for total weight limits
        self.parking['P1'] += shipment['P1']
        self.parking['P2'] += shipment['P2']
        self.parking['P3'] += shipment['P3']
        self.parking['P4'] += shipment['P4']
   

    def startup(self):
        # TODO : make compatible with class
        ### INITIAL ARRIVAL EVENT GENERATION
        # Current clock = 0
        print("Kernel()::__init__() is starting some cool stuff")       
        
        self.schd_delivery()
        # print(self.eventList)


    def mainLoop(self):
        # TODO: Needs input params
        ### THE MAIN SIMULATION LOOP STARTS HERE
        while self.clock < maxSimulationLength:
            # print("Sim step!")
            self.step()


    def step(self):
        # Process next event
        
        # print("Stepping Clock")
        # increment clock
        self.clock = self.clock + 5

        eventType = "None"
        if len(self.eventList.keys()):
            eventType = self.eventList.pop(self.nextEventScheduleTime)    # Get the next event while removing it from the event list

        if eventType == "DELIVERY_SCHD":
            shipment = {
                'P1': np.random.randint(1,100),
                'P2': np.random.randint(1,100),
                'P3': np.random.randint(1,100),
                'P4': np.random.randint(1,100)
            }
            # print(shipment)
            self.exec_delivery(shipment)
        elif eventType == "None":
            print("Nothing happened lol")

        # schedule a new delivery
        self.schd_delivery()
    
    
    def report(self):
        # Print metrics
        
        print("Current Clock: ".format(self.clock))

        print("The value of Parking for P1 is {}".format(self.parking['P1']))
        print("The value of Parking for P2 is {}".format(self.parking['P2']))
        print("The value of Parking for P3 is {}".format(self.parking['P3']))
        print("The value of Parking for P4 is {}".format(self.parking['P4']))

        print("DELIVERY Expense {}".format(self.cost))


if __name__ == "__main__":
    InboundOps = Stage1()
    