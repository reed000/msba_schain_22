"""
Kernel Class
"""
import numpy as np
import pandas as pd
import constants as cs
from data_store import DataStore

# # # # # # # # # # # # # # # # # #
# Notional data structures below  #
# # # # # # # # # # # # # # # # # #

    # eventID : {busProc name,  function}
#    event_dictionary = {
#        'DeliveryIn' : ('parking','EventDelivery'))
#    }

    # int TIMESTAMP : eventID
#    self.event_queue = {
#        800  : DockDelivery,
#        1600 : ReceiveOrders
#        3200 : WorkerStorage_2347_0_TransitStorage
#        3210 : WorkerStorage_2347_0_StowItem
#        3330 : WorkerStorage_2347_0_TransitParking
#    }   


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

        # store maximum runtime
        self.runtime = runtime

        # DATA
        self.DATA_STORAGE = DataStore()

        # save the options input
        self.options = options

        # initialize processes
        self.processes = procs
        for proc_name in self.processes:
            print("Booting: {}".format(proc_name))
            self.processes[proc_name].startup(kernel=self)
    
        # check event queue population
        # print(self.event_queue)

        self.event_dictionary = event_dictionary

        # ! ! ! W A R N I N G ! ! ! 
        # HARD CODE this for TESTING
        self.DATA_STORAGE.parking = {
                'P1':100,
                'P2':100,
                'P3':100,
                'P4':100
            }
        # ! ! ! W A R N I N G ! ! ! 

    # TODO Can be moved to an other class
    def get_day_and_shift(timestamp):
        """
        Returns Tuple (DAY, SHIFT #) of current wall clock
        tested in explore.ipynb
        """
        hour = 60 * 60
        day = hour * 24
        week = day * 7

        curr_time = timestamp % day
        curr_day = timestamp % week

        # Calculate SHIFT [0,1,2]
        if curr_time <= (hour * 8): #First 8 hours
            shift = 0
        elif curr_time <= (hour * 16 ):
            shift = 1
        else:  # shift < hour * 24 = 86400 = week
            shift = 2

        # Calculate DAY of WEEK
        days = ["THU", "FRI", "SAT", "SUN", "MON", "TUE", "WED"]
        for i in range(1,8):
            if curr_day < day*i:  #<12 AM
                today = days[i-1]
                break
        
        # print("{}: {} shift {}".format(timestamp, today, shift))
        return (today, shift)


    def mainLoop(self):
        ### THE MAIN SIMULATION LOOP STARTS HERE

        # Run the simulation so long as the clock has not exceed max time
        while self.clock < self.runtime:
            if not len(self.event_queue.keys()):
                # TODO - this is a dumb way to end the simulation
                return

            # get the next event from the most imminent event key            
            self.next_event_time = min(self.event_queue.keys())

            # walk the sim through that event
            self.step()


# TODO: Add daily event at 12:00 for updating holding/labor costs
    def step(self):
        # Update the clock
        # print("Stepping Clock to {}".format(self.next_event_time))
        self.clock = self.next_event_time

        # pop the event from the queue       
        eventType = self.event_queue.pop(self.clock)    # Get the next event while removing it from the event list

        # find which process must handle the event and its identifying name
        # print(self.event_dictionary)
        event_handler, event_name = self.event_dictionary[eventType]
        print("Loaded event: {} to be done by {}".format(event_name,event_handler))

        # run that process' event handler
        self.processes[event_handler].handleEvent(event_name, kernel=self)

        # report happenings of the time step
        self.report()

    
    def addEvent(self, event_time, event_name):
        # if the event time exists is taken
        while event_time in self.event_queue:
            event_time+=1.0
        
        self.event_queue[event_time] = event_name


    def report(self):
        # output data storage to make sure we're not messing up
        profit = self.DATA_STORAGE.revenue
        print("Current Clock: {}".format(self.clock))
        print(self.DATA_STORAGE)