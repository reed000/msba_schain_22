"""
Kernel Class
"""
import numpy as np
import pandas as pd
import constants as cs
from data_store import DataStore

from tqdm.auto import tqdm
import logging
from datetime import datetime

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
                       
        # print("Kernel()::__init__() is initializing some cool stuff")
        self.clock = 0

        # save the options input
        self.options = options

        # Event queue implemented using dictionary
                #clock: eventID
        self.event_queue = {}
        
        # Keep note of the next event chronologically to roll forward the system clock
        self.next_event_time = 0 

        # store maximum runtime
        self.runtime = runtime

        # DATA initialized 
        self.DATA_STORAGE = DataStore()

        # LOGGING
        if self.options['KENNY_LOGGINS']:
            log_name = datetime.now().strftime("%Y_%m_%d-%H:%M:%S") + '_logger.log'
            handler = logging.FileHandler(filename='logs/'+log_name)

            formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            #handler.setFormatter(formatter)

            self.LOGS = logging.getLogger()
            self.LOGS.setLevel(logging.DEBUG)
            self.LOGS.addHandler(handler)
            self.addLogs("StartUp :: logger object created",[])

        # initialize processes
        self.processes = procs
        for proc_name in self.processes:
            # print("Booting: {}".format(proc_name))
            self.processes[proc_name].startup(kernel=self)
    
        # check event queue population
        # print(self.event_queue)

        # set up the List of orders - QUEUE  (.append, .pop(0))
        self.orders = []

        # set up the initial dictionary of modules and events
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

        # DEFAULT STORAGE
        if self.options['STORAGE_MECHANIC'] == "DESIGNATED":
            self.DATA_STORAGE.storage = {
                'Area1': {'P1':10000,
                        'P2':0,
                        'P3':0,
                        'P4':0},
                'Area2': {'P1':0,
                        'P2':5000,
                        'P3':0,
                        'P4':0},
                'Area3': {'P1':0,
                        'P2':0,
                        'P3':5000,
                        'P4':0},
                'Area4': {'P1':0,
                        'P2':0,
                        'P3':0,
                        'P4':3333}}
        elif self.options['STORAGE_MECHANIC'] == "RANDOM":
            self.DATA_STORAGE.storage = {
                'Area1': {'P1':25000,
                        'P2':1250,
                        'P3':1250,
                        'P4':833},
                'Area2': {'P1':25000,
                        'P2':1250,
                        'P3':1250,
                        'P4':833},
                'Area3': {'P1':25000,
                        'P2':1250,
                        'P3':1250,
                        'P4':833},
                'Area4': {'P1':25000,
                        'P2':1250,
                        'P3':1250,
                        'P4':834}}

    def mainLoop(self):
        ### THE MAIN SIMULATION LOOP STARTS HERE

        # progres bar of great justice
        pbar = tqdm(total=self.runtime, position=0, leave=True, ascii=True)
        last_clock = 0

        # Run the simulation so long as the clock has not exceed max time
        while self.clock < self.runtime:
            if not len(self.event_queue.keys()):
                # TODO - this is a dumb way to end the simulation
                # print("**************EMPTY EVENT QUEUE*********** Hooray?")
                self.clock = self.runtime
                pbar.postfix = self.clock
                pbar.update()
                break

            # TODO Possible refactor of event_queue to min-heap if performance bad
            # https://www.geeksforgeeks.org/min-heap-in-python/

            # get the next most imminent event key            
            self.next_event_time = min(self.event_queue.keys())

            # walk the sim through that event
            self.step()

            
            pbar.update(self.clock-last_clock)
            last_clock = self.clock

        pbar.close()
        
        if self.options['SAVE_DATA']:
            self.writeDataframe()


# TODO: Add daily event at 12:00 for updating holding/labor costs
    def step(self):
        # Update the clock
        # print("Stepping Clock to {}".format(self.next_event_time))
        self.clock = self.next_event_time

        # pop the event from the queue       
        eventType = self.event_queue.pop(self.clock)    # Get the next event while removing it from the event list

        # find which process must handle the event and its identifying name
        self.addLogs("Clock {} :: Loading event - {}", [self.clock, eventType])
        event_handler, event_name = self.event_dictionary[eventType]
        self.addLogs("Clock {} :: Loaded event - {} to be done by {}", [self.clock, event_name,event_handler])

        # run that process' event handler
        self.processes[event_handler].handleEvent(event_name, kernel=self)

        # report happenings of the time step
        self.report()

    
    def addEvent(self, event_time, event_name):
        # if the event time exists is taken
        while event_time in self.event_queue:
            event_time += 1e-3
        
        self.addLogs("Clock {} :: Scheduling event - {} at t={}",[self.clock, event_name, event_time])
        self.event_queue[event_time] = event_name

        return event_time, event_name


    def addLogs(self, message:str, message_args:list):
        if self.options['KENNY_LOGGINS']:
            formatted = message.format(*message_args)
            self.LOGS.info(formatted)


    def report(self):
        # output data storage to make sure we're not messing up
        profit = self.DATA_STORAGE.revenue

        # transmit entire data storage to a time-stamped dict
        if self.options['SAVE_DATA']:
            self.DATA_STORAGE.save_state(self.clock)


    def writeDataframe(self):
        df = pd.DataFrame.from_dict(
            data=self.DATA_STORAGE._state_dict,
            orient='index'
        )

        df.to_csv("output/simout.csv")

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