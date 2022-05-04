"""
Business Process :: Picking()
"""
import numpy as np
import pandas as pd
import constants as cs
import warnings 

from bizprocs.process import BusinessProcess
from bizprocs.workers.picker import PickageWorker

class Picking(BusinessProcess):

    def __init__(self):
        super().__init__(name="Picking")
        self.__addEvent__("ShiftChangePicking",self.__shiftChange__)
        self.__addEvent__("PokeWorkersPicking",self.__pokeWorkers__)

        self.n_workers = 0
        self.workers = {}


    def startup(self, kernel=None):
        # set number of workers
        self.n_workers = kernel.options['PICKING_WORKERS']  

        # allocate all shift changes
        self.__scheduleShiftChanges__(kernel)

        # link to packing
        if 'packing' in kernel.processes:
            self.my_packing = kernel.processes['packing']
        

    def __scheduleShiftChanges__(self, kernel=None):

        # every 8 hours there is a new shift of workers
        shift_interval = 8 * 60 * 60 
        time_shift_change = 0

        # kernel.addEvent(0, "ShiftChangePicking")
        # kernel.addEvent(shift_interval, "ShiftChangePicking")

        # for the time being, only 2 shift changes

        while time_shift_change < kernel.runtime:           
            kernel.addEvent(time_shift_change, "ShiftChangePicking")
            time_shift_change += shift_interval


    def __shiftChange__(self, kernel=None):
        # create clock out tasks for old workers
        for they_call_me_the_working_man in self.workers:
            self.workers[they_call_me_the_working_man].clockOut(kernel)

        # create new workers
        for i in range(1,self.n_workers+1):
            new_worker = PickageWorker(self, kernel, i)
            self.workers[new_worker.name] = new_worker


    def __pokeWorkers__(self, kernel=None):
        for working_man in self.workers:
            # make them do something if idle
            if self.workers[working_man].idle:
                self.workers[working_man].poke(kernel)


    def validateOrder(self, kernel, order_content):
        if not order_content:
            warnings.warn("{} at time {} got blank order".format(self.name, kernel.clock))
            return False

        total_unmet = {
            'P1' : 0,
            'P2' : 0,
            'P3' : 0,
            'P4' : 0
        }

        total_capacity = {
            'P1' : 0,
            'P2' : 0,
            'P3' : 0,
            'P4' : 0
        }

        # sum present unmet needs in workers
        for working_man in self.workers:
            # make them do something if idle
            for item in self.workers[working_man].gap:
                total_unmet[item] += self.workers[working_man].gap[item]

        # add in the order requirements
        for item in order_content:
            total_unmet[item] += order_content[item]

        # sum up capacity across storage
        for area in kernel.DATA_STORAGE.storage:
            for item in kernel.DATA_STORAGE.storage[area]:
                total_capacity[item] += kernel.DATA_STORAGE.storage[area][item]

        delta = {}
        for item in total_capacity:
            delta[item] = total_capacity[item] - total_unmet[item]
            
        has_margin = all([delta[margin] >= 0 for margin in delta])

        return has_margin
        
    def killOrder(self, kernel=None, dead_order=None):
        # log the lost sales
        kernel.DATA_STORAGE.costs['lost_sales'] += dead_order.getPenalty()

        # and leave
        return

    def setAssignment(self, worker, order):
        self._assignments[worker] = order


"""
Each picker, if there are unfulfilled orders, will engage in picking operation. The
picking operation will take place in the following manner:

i. The picker will be assigned a single order to pick (in FIFO order).

ii. The picker will travel from the picking station to the appropriate inventory
storage area to pick the items included in the particular customer order.
a. In the case of designated stowing policy, the picker will travel in the
order of inventory storage area 1 à 2 à 3 à 4. However, the picker
will not need to visit station 1 if there are no t-shirts for example. Once
all items have been picked, the picker can return to the picking station
immediately without visiting all inventory storage areas.

b. In the case of randomized stowing policy, the picker will choose one
inventory storage area at random and pick from that area. If there are not
enough inventory in that inventory storage area, then the picker will
choose to move to a random adjacent inventory storage area and will
repeat until all items have been picked. Once all items have been picked,
the picker will return to the picking station.

iii. Once the picker returns to the picking station with all items, the picker will put
these items on the conveyor belt and will send to the packing station with the
least amount of orders waiting to be completed. If multiple packing stations have
the same amount of orders waiting to be completed, then the picker will select
one randomly.

We assume that pickers can carry an unlimited number of items. The picker can travel
directly between the picking station and any of the inventory storage area. Between each
inventory storage area, the picker can only travel directly to the adjacent inventory
storage area. The picker cannot travel from inventory storage area 1 to inventory storage
area 4 and the other way around.

The amounts of time it takes to complete individual steps in the picking operation are
listed below:
    • Time to travel from the picking station to each inventory storage area: 120
    seconds
    • Time to travel from an inventory storage area to an adjacent inventory storage
    area: 60 seconds
    • Time to pick one unit of a product: 10 seconds
    • Time to send picked products from the picking station to a packing station
    before starting another trip: 30 seconds
    Assume that there are no variations in travel, picking, or transport time.
    There is no partial order fulfillment. An order is either entirely fulfilled or discarded.
    Whether or not order fulfillment is possible or not will be determined at the front of the
    FIFO queue (i.e., when the picker is about to go pick the inventory).
    The picker does not need to visit the storage area to find out whether the order can be
    fulfilled or not. The picker, before starting the trip, will be able to check the amount of
    inventory in the storage area AND the orders that are currently in the process of being
    fulfilled by other pickers. If there aren't enough inventory after subtracting the current
    in-process orders to fulfill everything in the new order, the picker will discard the new
    order, lost sales penalty will be charged for the entire new order, and the picker will
    check if the next order can be fulfilled or not.
"""