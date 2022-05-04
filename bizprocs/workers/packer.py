"""
Worker Super Class (Packer for Packing)
"""
import warnings
import numpy as np
import pandas as pd
import constants as cs

import math

from bizprocs.workers.worker import Worker

class PackageWorker(Worker):
    def __init__(self, facility=None, kernel=None, num=0):
        super().__init__(facility, kernel, num)

        # define the default first task
        self.__startUpTask__ = self.__idling__

        # dictionary with contents of the order to be fulfilled
        self.order = None

        # flag indicating the worker is sitting around doing nothing
        self.idle = False

        # object of packing station
        self.station = None
        self.station_slot = -999

        # populate LOCAL methods
        # TODO - repopulate with picker methods
        self.__addEvent__(self.name+"_PackOrder"  ,self.__packOrder__)
        self.__addEvent__(self.name+"_OrderOut"   ,self.__orderOut__)


        # post up at the first station you can
        self.__occupyFirstStation__(kernel)

        # add self to the kernel's registers
        self.__clockIn__(facility, kernel)

    def poke(self, kernel=None):
        # call base worker poke for logging
        super().poke(kernel)

        # DON'T JUST STAND THERE ROOKIE GET TO A PACKING STATION
        if self.station is None:
            self.__occupyFirstStation__(kernel)

        # DON'T JUST STAND THERE SLACKER START PACKING THAT ORDER
        elif self.station.getNumOrders() > 0:
            self.__packOrder__(kernel)

    def __occupyFirstStation__(self, kernel):
        goto_index = self.facility.getFirstUnoccupiedStation()

        # return of None means no stations are available. Standby.
        if goto_index is None:
            self.__idling__(kernel)
            return

        # otherwise register that you have now taken place at the packing station
        self.station_slot = goto_index
        self.facility.setStationOccupied(self, goto_index)
        self.station = self.facility.getStationByIndex(goto_index)

    def __packOrder__(self, kernel=None):
        # it takes 30 seconds + 10 seconds per item to pack
        self.order = self.station.getNextOrder()

        # nothing on the stack, time to idle
        if self.order is None:
            self.__idling__(kernel)
            return
        
        order_time = cs.PACKER_BASE_TIME + \
                     cs.PACKER_TIME_PER_ITEM * self.order.getTotalItems()

        eta = kernel.clock + order_time
        self.__addWorkerEvent__(kernel, eta, self.name+"_OrderOut")

    def __orderOut__(self, kernel=None):
        # I DON'T CARE WHETHER YOU OWE ME OR NOT - YOU NEED TO PAY ME
        kernel.acquireCurrency(self.order)

        # GOT A MANSION, A CABIN, A CONDO, I SLEEP IN MY PHANTOM
        self.order = None

        # IN FOUR MINUTES I TURN THIS INTO FORENSICS IN A FOREIGN CAR
        self.__packOrder__(kernel)


    def __terminate__(self, kernel=None):
        # de-occupy the packing station
        if self.station is not None:
            self.facility.setStationEmpty(kernel, self, self.station_slot)

        # then execute the standard worker termination function
        super().__terminate__(kernel)

"""
H. Mechanics of the order packing operation

Each packer must be stationed at a packing station. If there are more packers than
packing stations, then the packers remain idle (but still get paid). The packing station
stores items that have been sent down from the picking station and each order is
processed on a FIFO basis.
The packing operation takes 30 seconds + 10 seconds per unit of a product. Assume no
variation in packing time. Once packed, the packed order will be sent for outbound
shipping processing.

I. Mechanics of the outbound shipping operation

We assume that outbound shipping takes place instantaneously after packing is
complete. In addition, we will assume no product returns. Therefore, we may book the
gross profit per unit sold from this particular order at this point.
"""