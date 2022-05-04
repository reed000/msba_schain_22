"""
Business Process :: Storage()
"""
import numpy as np
import pandas as pd
import constants as cs

from bizprocs.process import BusinessProcess
from bizprocs.workers.stower import StowageWorker

class Storage(BusinessProcess):

    def __init__(self):
        super().__init__(name="Storage")
        self.__addEvent__("ShiftChangeStorage",self.__shiftChange__)
        self.__addEvent__("PokeWorkersStorage",self.__pokeWorkers__)

        self.n_workers = 0
        self.workers = {}   


    def startup(self, kernel=None):
        # set number of workers
        self.n_workers = 3 #kernel.options['STOWAGE_WORKERS']  

        # allocate all shift changes
        self.__scheduleShiftChanges__(kernel)
        

    def __scheduleShiftChanges__(self, kernel=None):

        # every 8 hours there is a new shift of workers
        shift_interval = 8 * 60 * 60 
        time_shift_change = 0

        # kernel.addEvent(0, "ShiftChangeStorage")
        # kernel.addEvent(shift_interval, "ShiftChangeStorage")

        # for the time being, only 2 shift changes

        while time_shift_change < kernel.runtime:           
            kernel.addEvent(time_shift_change, "ShiftChangeStorage")
            time_shift_change += shift_interval


    def __shiftChange__(self, kernel=None):
        # create clock out tasks for old workers
        for they_call_me_the_working_man in self.workers:
            self.workers[they_call_me_the_working_man].clockOut(kernel)

        # create new workers
        for i in range(1,self.n_workers+1):
            new_worker = StowageWorker(self, kernel, i)
            self.workers[new_worker.name] = new_worker


    def __pokeWorkers__(self, kernel=None):
        # this method will get workers to move if idle
        pass
        # for working_man in self.workers:
        #     # make them do something if idle
        #     if self.workers[working_man].idle:
        #         self.workers[working_man].poke(kernel)
        

"""
Each stower, provided that there are still unstowed inventories in the pooling area, will
engage in stowing operation. The stowing operation will take place in the following
manner:

i. At the beginning of each trip, the stower will evaluate the remaining work in the
inventory parking area for each of the four products. The remaining work is
defined by the # of units remaining in the parking area multiplied by the weight
of each product. The stower will choose to stow the product with the most
remaining work. If there are multiple products with the same remaining work,4
the stower will choose one of the product with the most remaining work
randomly. The stower will carry only one type of product each trip, even if the
stower has remaining capacity to carry more than one type of product after
taking on all of the remaining units of one type of product.

ii. The stower will carry the chosen product to the inventory storage areas and stow
the product in the inventory storage areas based on either the designated storage
policy or random storage policy.

    a. The designated storage policy will designate each of the inventory
    storage area to carry only one type of product. For convenience, we will
    designate area 1 to t-shirts, area 2 to hoodies, area 3 to sweatpants, and
    area 4 to sneakers. The stower can travel directly to the corresponding
    inventory storage area from the inventory parking area.

    b. The random storage policy will make the stower travel across all four
    storage area and store ¼ of the total units across all four storage areas.
    The stower will travel the storage areas in the order of 1 à 2 à 3 à 4.
    If the number of units carried by the stower is not evenly divisible by 4,
    then the number of units stowed in each area is rounded down, with the
    remainder being stowed in area 4.

iii. Once the product has been stowed, the stower will return to the inventory
parking area and start the trip again as in step (i) if necessary.


Each stower can carry up to 12 lbs. per trip. The stower can travel directly between the
inventory parking area and any of the inventory storage area. Between each inventory
storage area, the stower can only travel directly to the adjacent inventory storage area.
The stower cannot travel directly from inventory storage area 1 to inventory storage
area 4 and the other way around.

Assume that there are no limits to the amount of products that can be stowed in any of
the inventory storage area. Also assume that having a lot of stowers will not cause
congestions anywhere in the facility.

The amounts of time it takes to complete individual steps in the stowing operation are
listed below:
    • Time to pick up items before starting the trip: 120 seconds
    • Time to travel from the inventory parking area to an inventory storage area: 120
    seconds
    • Time to travel from an inventory storage area to an adjacent inventory storage
    area: 60 seconds
    • Time to stow one unit of a product: 10 seconds

    
Assume that there are no variations in pick up, travel, or stowing time. The 120 seconds
to pick up the item is NOT included in the travel time. The stower will need to prep by
picking everything up (120s) + travel to the inventory storage area (120s) + travel
across the inventory storage area if necessary (???s) + travel back to the inventory
parking area (120s)
"""