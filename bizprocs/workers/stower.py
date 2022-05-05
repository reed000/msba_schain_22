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


    def poke(self, kernel=None):
        # call base worker poke
        super().poke(kernel)

        # then check that parking
        self.__checkParking__(kernel)

        
    def __checkParking__(self, kernel=None):
        # hold if there is nothing in the parking area:
        nothing = kernel.DATA_STORAGE.parking['P1'] == 0 and \
                    kernel.DATA_STORAGE.parking['P2'] == 0 and \
                    kernel.DATA_STORAGE.parking['P3'] == 0 and \
                    kernel.DATA_STORAGE.parking['P4'] == 0
        
        if nothing:
            self.__idling__(kernel)

        # otherwise, get the max weight thing
        max_weight_prod = kernel.DATA_STORAGE.get_max_weight_parking()

        # amount taken is minimum of max capacity or amount left
        # TODO - wrong!!! needs maximum capacity of UNITS, not WEIGHT
        load, max_weight_prod = self.__setLoad__(kernel, max_weight_prod)        

        # grab it with your hands
        self.hands[max_weight_prod] = math.floor(load / self.weights[max_weight_prod])

        # log which product we are hefting
        self.max_weight_prod = max_weight_prod

        # decrement it from the parking area
        kernel.DATA_STORAGE.parking[max_weight_prod] -= \
                            math.floor(load / self.weights[max_weight_prod])

        # figure out where to go
        self.__setDestination__(kernel, "INITIAL")

        eta = kernel.clock + cs.STOWER_PICKUP_TIME
        self.__addWorkerEvent__(kernel, eta, self.name+"_TravelStorage")

    
    def __setLoad__(self, kernel=None, max_weight_prod=None):
        load_out = 0

        # Case 1: 
        # ono.wav, the parking area is empty
        if kernel.DATA_STORAGE.parking[max_weight_prod]<=0:
            load_out = -999

        # Case 2:
        # redundantly max weight products in parking area
        # select randomly
        else:
            load_out = min(kernel.DATA_STORAGE.parking[max_weight_prod], \
                            self.max_capacity)   

        return load_out, max_weight_prod


# # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # W A R N I N G ! ! !   MAJOR REFACTORING ! ! ! # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __setDestination__(self, kernel=None, xfer_type=None):
        # sets logical flow
        strategy_dict = {
            "DESIGNATED" : {
                "INITIAL"  : self.__destLogicDesignatedInitial__,
                "TRANSFER" : self.__destLogicDesignatedTransfer__,
            },
            "RANDOM" : {
                "INITIAL"  : self.__destLogicRandomInitial__,
                "TRANSFER" : self.__destLogicRandomTransfer__,
            }
        }

        # execute the appropriate destination determination function
        strategy_dict[self.stow_strategy][xfer_type](kernel)

    def __destLogicDesignatedInitial__(self, kernel=None):
        '''
        The designated storage policy will designate each of the inventory
        storage area to carry only one type of product.
        '''
        # head to the first product warehouse in the order
        dest_dict = {
                "P1" : 'Area1',
                "P2" : 'Area2',
                "P3" : 'Area3',
                "P4" : 'Area4',
            }

        self.destination = dest_dict[self.max_weight_prod]

    def __destLogicDesignatedTransfer__(self, kernel=None):
        self.destination = "Parking"

    def __destLogicRandomInitial__(self, kernel=None):
        '''
        The random storage policy will make the stower travel across all four
        storage area and store ¼ of the total units across all four storage areas.
        The stower will travel the storage areas in the order of 1 à 2 à 3 à 4.
        '''        
        self.destination = 'Area1'

    def __destLogicRandomTransfer__(self, kernel=None):
        from_to_dict = {
            'Area1' : 'Area2',
            'Area2' : 'Area3',
            'Area3' : 'Area4',
            'Area4' : 'Parking',
        }

        area_now = self.destination
        self.destination = from_to_dict[area_now]


# # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # W A R N I N G ! ! !   MAJOR REFACTORING ! ! ! # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __stowProduct__(self, kernel=None):
        # set the self.dropoff variable
        if self.stow_strategy == "DESIGNATED":
            self.dropoff = self.hands
        else:
            self.__randomStorage__(self, kernel)

        # add to the appropriate storage area
        for item in self.dropoff:
            kernel.DATA_STORAGE.storage[self.destination][item] += self.dropoff[item]
            if item == "P1":
                kernel.DATA_STORAGE.throughputs['value_storage'] += self.dropoff[item] * cs.P1_PROFIT
            elif item == "P2":
                kernel.DATA_STORAGE.throughputs['value_storage'] += self.dropoff[item] * cs.P2_PROFIT
            elif item == "P3":
                kernel.DATA_STORAGE.throughputs['value_storage'] += self.dropoff[item] * cs.P3_PROFIT
            elif item == "P4":
                kernel.DATA_STORAGE.throughputs['value_storage'] += self.dropoff[item] * cs.P4_PROFIT

        # release it with your hands
        for item in self.dropoff:
            self.hands[item] -= self.dropoff[item]        

        # figure out what to do next
        self.__setDestination__(kernel, "TRANSFER")

        action_dict = {
            "Parking"   : (kernel.clock + cs.STOWER_TO_STORAGE_TIME, self.name+"_TravelParking"),
            "Area1"     : (kernel.clock + 1e-3, self.name+"_TravelAdjacent"),
            "Area2"     : (kernel.clock + 1e-3, self.name+"_TravelAdjacent"),
            "Area3"     : (kernel.clock + 1e-3, self.name+"_TravelAdjacent"),
            "Area4"     : (kernel.clock + 1e-3, self.name+"_TravelAdjacent"),
        }

        eta, next_event = action_dict[self.destination]

        self.__addWorkerEvent__(kernel, eta, next_event)


    def __randomStorage__(self, kernel=None):
        if self.destination == "Area4":
            self.dropoff = self.hands.copy()
        else:
            for item in self.hands:
                self.dropoff[item] = floor(self.hands[item]/4.0)



    def __travelStorage__(self, kernel=None):
        eta = kernel.clock + cs.STOWER_TO_STORAGE_TIME
        self.__addWorkerEvent__(kernel, eta, self.name+"_StowProduct")

    def __travelParking__(self, kernel=None):
        self.__resetMe__()
        
        eta = kernel.clock + cs.STOWER_TO_STORAGE_TIME
        self.__addWorkerEvent__(kernel, eta, self.name+"_CheckParking")

    def __travelAdjacent__(self, kernel=None):
        eta = kernel.clock + cs.STOWER_TRAVEL_TIME
        self.__addWorkerEvent__(kernel, eta, self.name+"_StowProduct")


    def __resetMe__(self):
        # called during a delivery,
        # resets the attributes used to track stuff
        # what the worker is carrying
        # what the worker is carrying
        self.hands = {}

        # next dropoff
        self.dropoff = {}


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