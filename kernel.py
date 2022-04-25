"""
Kernel Class
"""
import numpy as np
import pandas as pd

maxSimulationLength = 60*525600 # minutes = 1 year    

# # # # # # # # # # # # # # # # # #
# Notional data structures below  #
# # # # # # # # # # # # # # # # # #

    # eventID : {busProc name,  function}
#    event_dictionary = {
#        'DeliveryIn' : ('parking','EventDelivery'))
#    }

    # int TIMESTAMP : eventID
#    selfevent_queue = {
#        800  : DockDelivery,
#        1600 : ReceiveOrders
#        3200 : Worker0Arrives
#    }   

    # DATA STORAGE
        # parking, Storage_X = {
        #         'P1':0,
        #         'P2':0,
        #         'P3':0,
        #         'P4':0
        #     }

        # profit = 0
        #Costs = {
        #     'labor': 0
        #     'delivery': 0
        #     'lost_sales': 0
        #     'facilities_fixed': 0
        #     'packing_station': 0
        #     'inventory_holding': 0
        # }

class Kernel():

    def __init__(self, procs : dict,
                       runtime : int,
                       event_dictionary : dict,
                       options : dict):
                       
        print("Kernel()::__init__() is initializing some cool stuff")
        self.clock = 0

        # Event queue implemented using dictionary
                #clock: eventID
        self.event_queue = {}
        
        # Keep note of the next event chronologically to roll forward the system clock
        self.next_event_time = 0 

        # DATA
        self.DATA_STORAGE = {
            "parking": {
                'P1':0,
                'P2':0,
                'P3':0,
                'P4':0
            },
            "Storage": {
                'P1':0,
                'P2':0,
                'P3':0,
                'P4':0
            },
            "Costs": None,
            "Revenue": None,
        }

        # save the options input
        self.options = options

        # initialize processes
        self.processes = procs
        for proc_name in self.processes:
            print("Booting: {}".format(proc_name))
            self.processes[proc_name].startup(kernel=self)
    
        # check event queue population
        print(self.event_queue)

        self.event_dictionary = event_dictionary


    def mainLoop(self):
        ### THE MAIN SIMULATION LOOP STARTS HERE

        # Run the simulation so long as the clock has not exceed max time
        while self.clock < maxSimulationLength:
            if not len(self.event_queue.keys()):
                # TODO - this is a dumb way to end the simulation
                return

            # get the next event from the most imminent event key            
            self.next_event_time = min(self.event_queue.keys())

            # walk the sim through that event
            self.step()


    def step(self):
        # Update the clock
        # print("Stepping Clock to {}".format(self.next_event_time))
        self.clock = self.next_event_time

        # pop the event from the queue       
        eventType = self.event_queue.pop(self.clock)    # Get the next event while removing it from the event list

        # find which process must handle the event and its identifying name
        event_handler, event_name = self.event_dictionary[eventType]
        print("Loaded event: {} to be done by {}".format(event_name,event_handler))

        # run that process' event handler
        self.processes[event_handler].handleEvent(event_name, kernel=self)

        # report happenings of the time step
        self.report()

    
    def report(self):
        # output data storage to make sure we're not messing up
        profit = self.DATA_STORAGE['Revenue']
        print("Current Clock: {}".format(self.clock))
        print(self.DATA_STORAGE)
