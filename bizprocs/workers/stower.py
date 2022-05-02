"""
Worker Super Class (Stower for Storage)
"""
import warnings
import numpy as np
import pandas as pd
import constants as cs

import math

from bizprocs.workers.worker import Worker

class StowageWorker(Worker):
    def __init__(self, facility=None, kernel=None, num=0):
        super().__init__(facility, kernel, num)

        # define the default first task
        self.__startUpTask__ = self.__checkParking__

        # what the worker is carrying
        self.hands = {}

        # next dropoff
        self.dropoff = {}

        # destination
        self.destination = 'Parking'

        # the worker's capacity
        self.max_capacity = cs.STOWERLIMIT

        # get a product weight dictionary
        self.weights = {
            'P1' : cs.P1_WEIGHT,
            'P2' : cs.P2_WEIGHT,
            'P3' : cs.P3_WEIGHT,
            'P4' : cs.P4_WEIGHT
        }

        # save the distribution method, RANDOM or DESIGNATED
        self.stow_strategy = kernel.options['STORAGE_MECHANIC']

        # populate LOCAL methods
        self.__addEvent__(self.name+"_CheckParking"  ,self.__checkParking__)
        self.__addEvent__(self.name+"_TravelStorage" ,self.__travelStorage__)
        self.__addEvent__(self.name+"_TravelAdjacent",self.__travelAdjacent__)
        self.__addEvent__(self.name+"_StowProduct"   ,self.__stowProduct__)
        self.__addEvent__(self.name+"_TravelParking" ,self.__travelParking__)
        self.__addEvent__(self.name+"_SmokeCigs"     ,self.__smokeCigs__)

        # add self to the kernel's registers
        self.__clockIn__(facility, kernel)

        
    def __checkParking__(self, kernel=None):
        max_weight_prod = kernel.DATA_STORAGE.get_max_weight_parking()

        # amount taken is minimum of max capacity or amount left
        # TODO - wrong!!! needs maximum capacity of UNITS, not WEIGHT
        load, max_weight_prod = self.__setLoad__(kernel, max_weight_prod)        

        # if this is the load then there is nothing in parking
        if load == -999:
            warnings.warn("Stowage Empty at time {}".format(kernel.clock))
            return

        # grab it with your hands
        self.hands[max_weight_prod] = math.floor(load / self.weights[max_weight_prod])

        # decrement it from the parking area
        kernel.DATA_STORAGE.parking[max_weight_prod] -= \
                            math.floor(load / self.weights[max_weight_prod])

        # figure out where to go
        self.__setDestination__(max_weight_prod)

        eta = kernel.clock + cs.STOWER_PICKUP_TIME
        self.__addWorkerEvent__(kernel, eta, self.name+"_TravelStorage")

    
    def __setLoad__(self, kernel=None, max_weight_prod=None):
        load_out = 0

        # Case 1: 
        # ono.wav, the parking area is empty
        if kernel.DATA_STORAGE.parking[max_weight_prod]==0:
            load_out = -999

        # Case 2:
        # redundantly max weight products in parking area
        # select randomly
        else:
            load_out = min(kernel.DATA_STORAGE.parking[max_weight_prod], \
                            self.max_capacity)   

         # ! ! ! ! ! ! ! ! ! ! !
         # WARNING: DEPRECATED !
         # ! ! ! ! ! ! ! ! ! ! !
#        # Case 1: 
#        # ono.wav, the parking area is empty
#        if len(max_weight_prod) > 1 and \
#            kernel.DATA_STORAGE.parking[max_weight_prod[0]]==0:
#            load_out = -999
#
#        # Case 2:
#        # redundantly max weight products in parking area
#        # select randomly
#        elif len(max_weight_prod) > 1 and \
#            kernel.DATA_STORAGE.parking[max_weight_prod[0]]>0:
#            random_select = np.random.randint(0,len(max_weight_prod)-1)
#            max_weight_prod = max_weight_prod[random_select]
#            load_out = min(kernel.DATA_STORAGE.parking[max_weight_prod], \
#                            self.max_capacity) 
#
#        # Case 3:
#        # redundantly max weight products in parking area
#        # select randomly
#        else:
#            max_weight_prod = max_weight_prod[0]
#            load_out = min(kernel.DATA_STORAGE.parking[max_weight_prod], \
#                            self.max_capacity)   
#
        return load_out, max_weight_prod


    def __setDestination__(self, max_weight_prod=None):
        # where random or deterministic logic is set
        if self.stow_strategy == "DESIGNATED" and self.destination == "Parking":
            dest_dict = {
                'P1' : 'Area1',
                'P2' : 'Area2',
                'P3' : 'Area3',
                'P4' : 'Area4'
            }

            self.destination = dest_dict[max_weight_prod]
        elif self.stow_strategy == "DESIGNATED" and self.destination != "Parking":
            self.destination = "Parking"

        elif self.stow_strategy == "RANDOM":
            dest_dict = {
                'Parking' : 'Area1',
                'Area1'   : 'Area2',
                'Area2'   : 'Area3',
                'Area3'   : 'Area4',
                'Area4'   : 'Parking',
            }

            old_dest = self.destination
            self.destination = dest_dict[old_dest]

        else:
            warnings.warn("Worker {} got bogus stow strategy.".format(self.name))


    # will need to be upgraded with multiple storage areas
    def __travelStorage__(self, kernel=None):
        eta = kernel.clock + cs.STOWER_TO_STORAGE_TIME
        self.__addWorkerEvent__(kernel, eta, self.name+"_StowProduct")

    
    def __stowProduct__(self, kernel=None):
        # set the self.dropoff variable
        if self.stow_strategy == "DESIGNATED":
            self.dropoff = self.hands
        else:
            self.__randomStorage__(self, kernel)

        # add to the appropriate storage area
        for item in self.dropoff:
            kernel.DATA_STORAGE.storage[self.destination][item] += self.dropoff[item]    

        # release it with your hands
        for item in self.dropoff:
            self.hands[item] -= self.dropoff[item]        

        # figure out what to do next
        self.__setDestination__(kernel)

        if self.destination == "Parking":
            eta = kernel.clock + cs.STOWER_TO_STORAGE_TIME
            next_event = self.name+"_CheckParking"
        elif self.destination == "Area1":
            warnings.warn("Set destination to Area1 despite already stowing...")
            eta = kernel.clock + 1e-1
            next_event = self.name+"_TravelAdjacent"
        elif self.destination == "Area2":
            eta , next_event = kernel.clock + 1e-1, self.name+"_TravelAdjacent"
        elif self.destination == "Area3":
            eta, next_event = kernel.clock + 1e-1, self.name+"_TravelAdjacent"
        elif self.destination == "Area4":
            eta = kernel.clock + 1e-1
            next_event = self.name+"_TravelAdjacent"

        self.__addWorkerEvent__(kernel, eta, next_event)


    def __randomStorage__(self, kernel=None):
        if self.destination == "Area4":
            self.dropoff = self.hands.copy()
        else:
            for item in self.hands:
                self.dropoff[item] = floor(self.hands[item]/4.0)


    def __evaluateStorage__(self, kernel=None):
        pass


    def __travelAdjacent__(self, kernel=None):
        eta = kernel.clock + cs.STOWER_TRAVEL_TIME
        self.__addWorkerEvent__(kernel, eta, self.name+"_StowProduct")


    def __travelParking__(self, kernel=None):
        eta = kernel.clock + cs.STOWER_TO_STORAGE_TIME
        self.__addWorkerEvent__(kernel, eta, self.name+"_CheckParking")


    def __smokeCigs__(self, kernel=None):
        pass

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