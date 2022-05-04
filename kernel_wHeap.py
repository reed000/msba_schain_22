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

import heapq as MinHeap
import queue as MuhQueue
import sys


class Kernel():

    def __init__(self, procs : dict,
                       runtime : int,
                       event_dictionary : dict,
                       options : dict):

        # we abuse recursion in this simulation               
        sys.setrecursionlimit(42069)

        self.clock = 0

        # save the options input
        self.options = options

        # heapq : Min Heap - store tuples (time, event)
        self.event_queue = []
        # required now to check times before putting into the heap.
        self.event_times = set()
        
        # Keep note of the next event chronologically to roll forward the system clock
        self.next_event_time = 0 

        # store maximum runtime
        self.runtime = runtime

        # DATA initialized 
        self.DATA_STORAGE = DataStore()

        # Add Packing Station Costs
        self.DATA_STORAGE.costs['packing_stn'] += self.options['PACKING_STATIONS'] * cs.PACK_STATION_COST

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

        # set up the List of orders - QUEUE  (.append, .pop(0))  (get put)
        self.orders = MuhQueue.Queue()

        # initialize processes
        self.processes = procs
        for proc_name in self.processes:
            self.addLogs("Booting: {}".format(proc_name),[])
            self.processes[proc_name].startup(kernel=self)
     
        # set up the initial dictionary of modules and events
        self.event_dictionary = event_dictionary

        # TODO ! ! ! W A R N I N G ! ! ! Set parking 0
        # HARD CODE this for TESTING
        # self.DATA_STORAGE.parking = {
        #         'P1':100,
        #         'P2':100,
        #         'P3':100,
        #         'P4':100
        #     }
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
            if not len(self.event_queue):
                # TODO - this is a dumb way to end the simulation
                self.clock = self.runtime
                pbar.postfix = self.clock
                pbar.update()
                break

            # Peek the next most imminent event key from the Heap           
            self.next_event_time = self.event_queue[0][0]

            # walk the sim through that event
            self.step()

            # update that progress bar
            pbar.update(self.clock-last_clock)
            last_clock = self.clock

        pbar.close()
        
        if self.options['SAVE_DATA']:
            self.writeDataframe()

        if self.options['FINAL_ECHO']:
            self.finalEcho()


# TODO: Add daily event at 12:00 for updating holding/labor costs
    def step(self):
        # Update the clock
        self.clock = self.next_event_time

        # pop the event from the queue       
        eventType = MinHeap.heappop(self.event_queue)[1]

        # find which process must handle the event and its identifying name
        self.addLogs("T={}::NewEvent={}", [self.clock, eventType])
        event_handler, event_name = self.event_dictionary[eventType]
        self.addLogs("T={}::LoadedEvent={}::Proc={}", [self.clock, event_name,event_handler])

        # run that process' event handler
        self.processes[event_handler].handleEvent(event_name, kernel=self)

        # report happenings of the time step
        self.report()

    
    def addEvent(self, event_time, event_name):
        # check if new time is in the event times set
        event_time = self.__checkEventTime__(event_time)
        
        # TODO potential problem on duplicate times
        MinHeap.heappush(self.event_queue, (event_time, event_name))

        # add clock time to the set
        self.event_times.add(event_time)
        
        # self.addLogs("Clock {} :: Scheduling event - {} at t={}",[self.clock, event_name, event_time])
        return event_time, event_name

    def __checkEventTime__(self, event_time):
        if event_time in self.event_times:
            event_time += 1e-1
            event_time = self.__checkEventTime__(event_time)
        
        return event_time

    def addLogs(self, message:str, message_args:list):
        if self.options['KENNY_LOGGINS']:
            formatted = message.format(*message_args)
            self.LOGS.info(formatted)


    def report(self):
        # output data storage to make sure we're not messing up
        # print("REPORT ORDERS: {}".format(self.orders.qsize()))

        # transmit entire data storage to a time-stamped dict
        if self.options['SAVE_DATA']:
            self.DATA_STORAGE.save_state(self.clock)


    def acquireCurrency(self, order):
        # output data storage to make sure we're not messing up
        self.DATA_STORAGE.revenue += order.getProfit()


    def receivePunishment(self, order):
        # output data storage to make sure we're not messing up
        self.costs['lost_sales'] += order.getPenalty()


    def writeDataframe(self):
        df = pd.DataFrame.from_dict(
            data=self.DATA_STORAGE._state_dict,
            orient='index'
        )

        df.to_csv("output/simout_{}.csv".format(datetime.now().strftime("%m_%d-%H:%M")))

    def finalEcho(self):
        echo_out = self.DATA_STORAGE.get_KPIs()
        for this_kpi in echo_out:
            print(this_kpi,' : ',str(echo_out[this_kpi]))
        # self.addLogs(echo_out, [])

    def get_day_and_shift(self, timestamp):
        """
        Returns Tuple (str: DAY, int: SHIFT #) of current wall clock

        tested in explore.ipynb
        """
        hour = 60 * 60
        day = hour * 24
        week = day * 7

        # modulus for seconds value from THU 12:00
        curr_time = timestamp % day
        curr_day = timestamp % week

        # Calculate SHIFT [0,1,2,3] | (0,1) = Shift 1 0000:8000
        if curr_time <= (hour * 4): #First 4 hours
            shift = 0
        elif curr_time <= (hour * 8): # Next 4 hours
            shift = 1
        elif curr_time <= (hour * 16 ):  # Next 8 hours
            shift = 2
        else:  # shift < hour * 24 = 86400 = week
            shift = 3

        # Calculate DAY of WEEK
        days = ["THU", "FRI", "SAT", "SUN", "MON", "TUE", "WED"]
        for i in range(1,8):
            if curr_day < day*i:  #<12 AM
                today = days[i-1]
                break
        
        # print("{}: {} shift {}".format(timestamp, today, shift))
        return (today, shift)

    def get_midnight_strikes(self):
        midnights = []
        for i in range(366): 
            midnights.append(i*86400)

            # TODO self.addEvent(i, "MIDNIGHT")

            # TODO Inventory holding costs are accrued on a continuous basis. For initial starting inventory, 
            # assume that there is no inventory holding cost before time 0 but inventory holding cost 
            # would start accruing from time 0. For convenience, you may use seconds as the minimal 
            # unit calculation for the inventory holding cost

        return midnights