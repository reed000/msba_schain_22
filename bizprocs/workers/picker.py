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

        # flag indicating if worker is carrying items
        self.has_items = False

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

        # add self to the kernel's registers
        self.__clockIn__(facility, kernel)

    def poke(self, kernel=None):
        self.idle = False   
        print("{} : Back to work".format(self.name))
        self.__requestOrder__(kernel)


    def __idling__(self, kernel=None):
        # reset the present task
        self.present_task = {}
        print("{}: I've got nothing, idling".format(self.name))
        self.idle = True

    
    def __requestOrder__(self, kernel=None):
        # You're back at the picking station
        # Assign yourself the next order from the queue

        if not kernel.orders:
            # no orders - bail out until poked
            self.__idling__(kernel)
            return

        self.order = kernel.orders.pop(0)
        print("{}: Got an order, validating".format(self.name))

        # check in with the facility the new order is valid:
        order_ok = self.facility.validateOrder(kernel, self.order.getContent())
        
        if order_ok:
            # if it's good assign yourself
            # self.facility.setAssignment(self, self.order)
            print("{}: Order is good, contents are: {}".format(self.name, self.order.getContent()))

            # figure out what you need
            self.__calcOrderGap__()

            # and walk on over to storage
            self.__travelStorage__(kernel)
        else:
            # request another one
            print("{}: Order is no-good, contents are: {}".format(self.name, self.order.getContent()))
            self.__requestOrder__(kernel)        


    def __travelStorage__(self, kernel=None):
        ## figure out where you're supposed to go
        self.__setDestination__(kernel, xfer_type="INITIAL")
        print("{}: I'm headed to first: {}".format(self.name, self.destination))


        eta = kernel.clock + cs.STOWER_PICKUP_TIME
        self.__addWorkerEvent__(kernel, eta, self.name+"_CheckArea")


    def __checkArea__(self, kernel=None):
        ## this function checks if the area has any of the items in the order

        # check if the order is done
        self.__isOrderComplete__()

        # if you have all the items you don't need to be here, go back
        if self.order_completed:
            print("{}: Done with order: {}".format(self.name, self.order.getContent()))

            self.destination = "Picking"
            eta = kernel.clock + cs.PICKER_TO_STORAGE_TIME
            self.__addWorkerEvent__(kernel, eta, self.name+"_DeliverOrder")
            return

        # get the items where you are
        area_inventory = kernel.DATA_STORAGE.storage[self.destination]        
        print("{}: This joint {} has : {}".format(self.name, self.destination, self.gap))
        print("{}: I still need: {}".format(self.name, self.gap))

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
        # Register you have something in your hands
        if self.has_items == False:
            self.has_items = True

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

        print("Gap: ", self.gap)
        if not self.gap:
            print("Hands: ",self.hands)
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

        # flag indicating if worker is carrying items
        self.has_items = False

        # flag indicating if the current order is over
        self.order_completed = False

        # dictionary with contents of the order to be fulfilled
        self.order = None

        # destination
        self.destination = 'Picking'

        # reset the present task
        self.present_task = {}