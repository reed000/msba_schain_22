import pandas as pd
import numpy as np
from kernel import Kernel
import constants as cs

from bizprocs.storing import Storage

"""
This is the driver script for the entire project
"""
def PRIMARY_LOOP():
    processes = {
        #'parking' : Pooling()
        'stowage' : Storage(),
        # 'picking' : Picking(),
        # 'packing' : Packing(),
        # 'orders'  : OrdersQueue()
    }

    # OrderIN, DeliveryIN, OrderOUT, 
    event_dictionary = {
         'DeliveryIn' : ('parking','getDelivery'),
         'ShiftChangeStorage' : ('stowage', 'ShiftChangeStorage')
     }

    options_dict = {
         'DELIVERY_SCHEDULE' : 'WEEKLY',    #['DAILY', 'WEEKLY']
         'STORAGE_MECHANIC' : 'DESIGNATED', #['DESIGNATED', 'RANDOM']
         'STORAGE_WORKERS' :  4,            # N
         'PICKING_MECHANIC' : 'DESIGNATED', #['DESIGNATED', 'RANDOM']
         'PICKING_WORKERS' :  4,            # N
         'PACKING_WORKERS' :  4,            # N
         'PACKING_STATIONS' : 4             # N
     }

    simulation_loop = Kernel(procs=processes,
                            runtime=99999999999999999999,
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