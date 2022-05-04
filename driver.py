"""
This is the driver script for the entire project

Project Entry Point
- Set variables in Constants.py
- Set options below
"""
import pandas as pd
import numpy as np
from kernel_wHeap import Kernel
import constants as cs

from bizprocs.facilities.pooling import Pooling
from bizprocs.facilities.storing import Storage
from bizprocs.facilities.picking import Picking
from bizprocs.facilities.packing import Packing
from bizprocs.facilities.ordering import Orders

SET_RUNTIME = 3600*24*10 # 10 days
# SET_RUNTIME = 3600*24*30*2 # 2 months
# SET_RUNTIME = 60*525600 # minutes = 1 year

def find_delivery_file():
    """
    TODO: Does this need to be automated for 'out of box' solution
    TODO Add delivery file path to kernel.options
    """
    weekly_delivery_times = []
    daily_delivery_times = []

    week = 604800
    day = 86400
    hour = 3600
    minute = 60

    daily_first = (3600)*9
    Mon_first = 345600 + (3600)*9
    for i in range (31536000): 
        if (i - daily_first) % day == 0:
            daily_delivery_times.append(i)
        if (i - Mon_first) % week == 0:
            weekly_delivery_times.append(i)


def PRIMARY_LOOP():
    processes = {
        'parking' : Pooling(),
        'stowage' : Storage(),
        'picking' : Picking(),
        'packing' : Packing(),
        'orders'  : Orders()
    }

    event_dictionary = {
        'DeliveryIn' : ('parking','DeliveryIn'),
        'OrderUp': ('orders', 'OrderUp'),
        'ShiftChangeStorage' : ('stowage', 'ShiftChangeStorage'),
        'PokeWorkersStorage' : ('stowage', 'PokeWorkersStorage'),
        'ShiftChangePicking' : ('picking', 'ShiftChangePicking'),
        'PokeWorkersPicking' : ('picking', 'PokeWorkersPicking'),
        'ShiftChangePacking' : ('packing', 'ShiftChangePacking'),
        'PokeWorkersPacking' : ('packing', 'PokeWorkersPacking')
        # Order Out
     }

    # SHIFTS every day 3 slots # workers per slot = [12-8, 8-4, 4-12]

    # find 100 order of workers
    # loop 80 - 120 workers for each of the 21 time slots per worker
    stowing_shift = {
        "SUN": [5, 5, 5],
        "MON": [20, 5, 5],
        "TUE": [5, 5, 5],
        "WED": [5, 5, 5],
        "THU": [5, 5, 5],
        "FRI": [5, 5, 5],
        "SAT": [5, 5, 5]
    }
    picking_shift = {
        "SUN": [5, 5, 5],
        "MON": [5, 5, 5],
        "TUE": [5, 5, 5],
        "WED": [5, 5, 5],
        "THU": [5, 5, 5],
        "FRI": [5, 5, 5],
        "SAT": [5, 5, 5]
    }
    packing_shift = {   # Each shift should ~= N PACKING_STATIONS
        "SUN": [5, 5, 5],
        "MON": [5, 5, 5],
        "TUE": [5, 5, 5],
        "WED": [5, 5, 5],
        "THU": [5, 5, 5],
        "FRI": [5, 5, 5],
        "SAT": [5, 5, 5]
    }
    options_dict = {
        # Optimize Variables
         'DELIVERY_SCHEDULE'    : 'WEEKLY',      #['DAILY', 'WEEKLY'] _TEST_
         'STORAGE_MECHANIC'     : 'DESIGNATED', #['DESIGNATED', 'RANDOM']
         'STORAGE_WORKERS'      :  500,         # stowing_shift
         'PICKING_MECHANIC'     : 'DESIGNATED', #['DESIGNATED', 'RANDOM']
         'PICKING_WORKERS'      :  25,          # picking_shift
         'PACKING_WORKERS'      :  30,          # packing_shift
         'PACKING_STATIONS'     :  30,          # N
        # Debug Variables
         'KENNY_LOGGINS'        :  False,        # [True, False*]
         'SAVE_DATA'            :  False,       # [True*, False]
         'FINAL_ECHO'           :  True,        # [True*, False]
         'ORDER_TEST'           :  False,        # [True, False*]
         #'ORDER_FILE'           : #'strategies/final-project-2022m4_orders.csv' ## moreeee compute :(
         'ORDER_FILE'           : 'strategies/order_sample.csv' 

    }
    
    print("Runtime: ", SET_RUNTIME)
    print("Delivery Option: ", options_dict['DELIVERY_SCHEDULE'])
    print("Storage: ", options_dict['STORAGE_MECHANIC'])

    simulation_loop = Kernel(procs=processes,
                            runtime=SET_RUNTIME,
                            event_dictionary=event_dictionary,
                            options=options_dict)

    sim_results = simulation_loop.mainLoop()

    #try:
    #    for loop
            # - set different options
            # - scipy optimize 
            # - target (simulation_loop.revenue)
    #    sim_results = simulation_loop.mainLoop()
    #except:
    #    print("Ono.wav")


    # simulation_loop.processResults()


if __name__ == "__main__":
    PRIMARY_LOOP()



"""
OPTIONS

The inbound receiving operation
1. Choose between (a) the weekly delivery schedule, or (b) the daily delivery 
schedule.

2. The delivery schedule over the next 52 weeks for each of the products managed 
by the fulfillment center. This can vary from shipment to shipment or it can stay 
constant throughout the entire 52 weeks.


The inventory stowing and the order picking operations
• Choose between (a) the designated stowing policy or (b) the randomized 
stowing policy.
• The weekly stowing shift schedule (i.e., the # of workers on duty each shift for 
every day of the week). This schedule will stay constant throughout all 52 weeks.
• The weekly picking shift schedule (i.e., the # of workers on duty each shift for 
every day of the week). This schedule will stay constant throughout all 52 weeks.


The order packing operation
• Choose the number of packing stations to set up (i.e., the maximum number of 
packers that can work at the same time).
• The weekly packing shift schedule (i.e., the # of workers on duty each shift for 
every day of the week). This schedule will stay constant throughout all 52 weeks.

"""