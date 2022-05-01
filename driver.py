import pandas as pd
import numpy as np
from kernel import Kernel
import constants as cs

from bizprocs.facilities.pooling import Pooling
from bizprocs.facilities.storing import Storage
from bizprocs.facilities.picking import Picking
from bizprocs.facilities.ordering import Orders


"""
This is the driver script for the entire project
"""
def PRIMARY_LOOP():
    processes = {
        # 'parking' : Pooling(),
        # 'stowage' : Storage(),
        'picking' : Picking(),
        # 'packing' : Packing(),
        'orders'  : Orders()
    }

    # OrderIN, DeliveryIN, OrderOUT, 
    event_dictionary = {
        # 'DeliveryIn' : ('parking','getDelivery'),
        'OrderUp': ('orders', 'OrderUp'),
        #  'ShiftChangeStorage' : ('stowage', 'ShiftChangeStorage')
        'ShiftChangePicking' : ('picking', 'ShiftChangePicking'),
        'PokeWorkersPicking' : ('picking', 'PokeWorkersPicking')
     }

    # SHIFTS every day 3 slots # workers per slot = [12-8, 8-4, 4-12]
    stowing_shift = {
        "SUN": [5, 5, 5],
        "MON": [5, 5, 5],
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
         'DELIVERY_SCHEDULE'    : 'DAILY',      #['DAILY', 'WEEKLY'] _TEST_
         'STORAGE_MECHANIC'     : 'DESIGNATED', #['DESIGNATED', 'RANDOM']
         'STORAGE_WORKERS'      :  5,           # stowing_shift
         'PICKING_MECHANIC'     : 'DESIGNATED', #['DESIGNATED', 'RANDOM']
         'PICKING_WORKERS'      :  5,           # picking_shift
         'PACKING_WORKERS'      :  5,           # packing_shift
         'PACKING_STATIONS'     :  4,           # N
         'KENNY_LOGGINS'        :  True
     }

    simulation_loop = Kernel(procs=processes,
                            runtime=60*525600, # minutes = 1 year
                            event_dictionary=event_dictionary,
                            options=options_dict)

    sim_results = simulation_loop.mainLoop()

    #try:
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