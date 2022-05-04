"""
Worker Super Class (Picker for Picking)
"""
import warnings
import numpy as np
import pandas as pd
import constants as cs

import math

from bizprocs.workers.worker import Worker

class PickageWorker(Worker):
    def __init__(self, facility=None, kernel=None, num=0):
        super().__init__(facility, kernel, num)

        # define the default first task
        self.__startUpTask__ = self.__idling__

        # what the worker is carrying
        self.hands = {
            'P1' : 0,
            'P2' : 0,
            'P3' : 0,
            'P4' : 0
        }

        # Dictionary of items that we do not have
        self.gap = {}

        # dictionary with contents of the order to be fulfilled
        self.order = None

        # flag indicating if the current order is over
        self.order_completed = False

        # flag indicating the worker is sitting around doing nothing
        self.idle = False

        # destination
        self.destination = 'Picking'

        # save the distribution method, RANDOM or DESIGNATED
        self.stow_strategy = kernel.options['STORAGE_MECHANIC']

        # populate LOCAL methods
        # TODO - repopulate with picker methods
        self.__addEvent__(self.name+"_RequestOrder"  ,self.__requestOrder__)
        self.__addEvent__(self.name+"_CheckArea"     ,self.__checkArea__)
        self.__addEvent__(self.name+"_HeftItem"      ,self.__heftItem__)
        self.__addEvent__(self.name+"_TravelStorage" ,self.__travelStorage__)
        self.__addEvent__(self.name+"_TravelAdjacent",self.__travelAdjacent__)
        self.__addEvent__(self.name+"_TravelPicking" ,self.__travelPicking__)
        self.__addEvent__(self.name+"_DeliverOrder"  ,self.__deliverOrder__)
        self.__addEvent__(self.name+"_TransferOrder" ,self.__transferOrder__)

        # add self to the kernel's registers
        self.__clockIn__(facility, kernel)


    def poke(self, kernel=None):
        # call base worker poke
        super().poke(kernel)

        # then request that order
        self.__requestOrder__(kernel)

    
    def __requestOrder__(self, kernel=None):
        # You're back at the picking station
        # Assign yourself the next order from the queue

        if kernel.orders.empty(): # not kernel.orders:
            # no orders - bail out until poked
            self.__idling__(kernel)
            return

        self.order = kernel.orders.get() # kernel.orders.pop(0)

        # check in with the facility the new order is valid:
        order_ok = self.facility.validateOrder(kernel, self.order.getContent())
        
        if order_ok:
            # figure out what you need
            self.__calcOrderGap__()

            # and walk on over to storage
            self.__travelStorage__(kernel)
        else:
            # have facility kill the order and log the loss
            # print("{} - {}: Got an order".format(kernel.clock,self.name))
            # print("creation time: ",self.order._creation_time)
            # print("destruction time: ",self.order._destruction_time)
            # print("TOO LATE: ",self.order._TOO_LATE)
            # print("content: ",self.order._content)
            # print("number items: ",self.order.n_items)
            # print("profit: ",self.order.order_profit)
            # print("penalty: ",self.order.order_penalty)

            self.facility.killOrder(kernel, self.order)

            # request another one
            self.__requestOrder__(kernel)        


    def __travelStorage__(self, kernel=None):
        ## figure out where you're supposed to go
        self.__setDestination__(kernel, xfer_type="INITIAL")

        eta = kernel.clock + cs.STOWER_PICKUP_TIME
        self.__addWorkerEvent__(kernel, eta, self.name+"_CheckArea")


    def __checkArea__(self, kernel=None):
        ## this function checks if the area has any of the items in the order

        # check if the order is done
        self.__isOrderComplete__()

        # if you have all the items you don't need to be here, go back
        if self.order_completed:
            self.destination = "Picking"
            eta = kernel.clock + cs.PICKER_TO_STORAGE_TIME
            self.__addWorkerEvent__(kernel, eta, self.name+"_DeliverOrder")
            return

        # get the items where you are
        area_inventory = kernel.DATA_STORAGE.storage[self.destination]        

        # search for each missing item
        for missing_item in self.gap:
            # ignore if there is none of the needed item
            if area_inventory[missing_item] <= 0:
                continue

            # otherwise, grab the item
            self.__heftItem__(kernel, missing_item)

            # after hefting time for one unit, check again
            eta = kernel.clock + cs.PICKER_TO_STORAGE_TIME
            self.__addWorkerEvent__(kernel, eta, self.name+"_CheckArea")
            return

        # this place didn't have the missing items, move along
        self.__setDestination__(kernel, xfer_type="TRANSFER")
        self.__travelAdjacent__(kernel)


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
        # head to the first product warehouse in the order
        dest_dict = {
                "P1" : 'Area1',
                "P2" : 'Area2',
                "P3" : 'Area3',
                "P4" : 'Area4',
            }

        first_needed_item = list(self.gap.keys())[0]
        self.destination = dest_dict[first_needed_item]

    def __destLogicDesignatedTransfer__(self, kernel=None):
        # head home if order complete
        # else head to next warehouse and check if items are required
        dest_dict = {
            'Area1' : 'Area2',
            'Area2' : 'Area3',
            'Area3' : 'Area4',
            'Area4' : 'Area3',
        }

        old_dest = self.destination
        self.destination = dest_dict[old_dest]

    def __destLogicRandomInitial__(self, kernel=None):
        dest_dict = {
                0   : 'Area1',
                1   : 'Area2',
                2   : 'Area3',
                3   : 'Area4',
            }

        self.destination = dest_dict[np.random.randint(0,4,1)]

    def __destLogicRandomTransfer__(self, kernel=None):
        from_to_dict = {
            'Area1' : ['Area2', 'Area2'],
            'Area2' : ['Area1', 'Area3'],
            'Area3' : ['Area2', 'Area4'],
            'Area4' : ['Area3', 'Area3'],
        }

        possible_nexts = from_to_dict[self.destination]
        self.destination = possible_nexts[np.random.randint(0,1,1)]


    def __heftItem__(self, kernel=None, missing_item=None):
        self.hands[missing_item] += 1
        kernel.DATA_STORAGE.storage[self.destination][missing_item] -= 1


    def __travelAdjacent__(self, kernel=None):
        eta = kernel.clock + cs.PICKER_TRAVEL_TIME
        self.__addWorkerEvent__(kernel, eta, self.name+"_CheckArea")


    def __travelPicking__(self, kernel=None):
        # travel from stowage to picking unit
        eta = kernel.clock + cs.PICKER_TO_STORAGE_TIME
        self.__addWorkerEvent__(kernel, eta, self.name+"_DeliverOrder")


    def __deliverOrder__(self, kernel=None):
        for item in self.hands:
            kernel.DATA_STORAGE.temp_packing[item] += self.hands[item]

        eta = kernel.clock + cs.PICKER_TO_PACKING_TIME
        self.__addWorkerEvent__(kernel, eta, self.name+"_TransferOrder")


    def __transferOrder__(self, kernel=None):
        lbs_index = self.facility.my_packing.getLeastBurdenedStation()
        lbs = self.facility.my_packing.getStationByIndex(lbs_index)
        lbs.addOrder(self.order)
        
        self.__resetOrderCounters__()
        self.__requestOrder__(kernel)


    def __calcOrderGap__(self):
        gap = self.order.getContent()

        for item in self.hands:
            if item not in gap:
                continue

            gap[item] -= self.hands[item]
            if gap[item] <= 0:
                gap.pop(item)

        self.gap = gap
    

    def __isOrderComplete__(self):
        self.__calcOrderGap__()

        if not self.gap:
            self.order_completed = True


    def __resetOrderCounters__(self):
        # called during a delivery,
        # resets the attributes used to track stuff
        # what the worker is carrying
        self.hands = {
            'P1' : 0,
            'P2' : 0,
            'P3' : 0,
            'P4' : 0
        }

        # Dictionary of items that we do not have
        self.gap = {}

        # flag indicating if the current order is over
        self.order_completed = False

        # dictionary with contents of the order to be fulfilled
        self.order = None

        # destination
        self.destination = 'Picking'

        # reset the present task
        self.present_task = {}