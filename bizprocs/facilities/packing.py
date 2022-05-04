"""
Business Process :: Packing()
"""
import numpy as np
import pandas as pd
import constants as cs
import warnings

from bizprocs.process import BusinessProcess
from bizprocs.workers.packer import PackageWorker
from bizprocs.utilities.station import Station

class Packing(BusinessProcess):

    def __init__(self):
        super().__init__(name="Packing")
        self.__addEvent__("ShiftChangePacking",self.__shiftChange__)
        self.__addEvent__("PokeWorkersPacking",self.__pokeWorkers__)

        self.n_workers  = 0
        self.workers    = {}

        # station keeping variables
        self.n_stations     = 0
        self.stations       = []
        self.station_burden = np.zeros(shape=1) # SOOOOOOOOOOOOOOOOO FAST
        self.station_occup  = np.array(1)


    def startup(self, kernel=None):
        # set number of workers
        self.n_workers = 3 #kernel.options['PACKING_WORKERS']

        # set number of stations
        self.n_stations = kernel.options['PACKING_STATIONS']

        # create packing stations
        self.__createPackingStations__(kernel)

        # allocate all shift changes
        self.__scheduleShiftChanges__(kernel)

        # link to picking
        if 'picking' in kernel.processes:
            self.my_picking = kernel.processes['packing']
        

    def __createPackingStations__(self, kernel=None):

        for i in range(self.n_stations):
            self.stations.append(Station(self, i))

        self.station_burden = np.zeros(shape=self.n_stations)

        self.station_occup = np.zeros(self.n_stations, dtype=bool)


    def getLeastBurdenedStation(self):
        return np.argmin(self.station_burden)


    def getFirstUnoccupiedStation(self):
        first_avail = None
        if any(self.station_occup == False):
            first_avail = np.nonzero(self.station_occup == False)[0][0]
        return first_avail


    def getStationByIndex(self, index_in=0):
        return self.stations[index_in]


    def setStationOccupied(self, worker_in=None, index_in=-99):
        got_station = False
        if self.station_occup[index_in] == False:
            self.stations[index_in].setWorker(worker_in)
            self.station_occup[index_in] = True
            got_station = True
        else:
            warning.warn("attempted to double occupy a packing station")

        return got_station


    def setStationEmpty(self, kernel=None, worker_in=None, index_in=-99):
        if self.station_occup[index_in] == True:
            self.stations[index_in].removeWorker()
            self.station_occup[index_in] = False
        else:
            warning.warn("attempted to double empty a packing station")

        self.__pokeWorkers__(kernel)


    def addOrderToStation(self, kernel=None, station_num=None, order_in=None):
        self.stations[station_num].addOrder(order_in)
        
        # returns worker object if idle, None if occupied
        idle_worker = self.stations[station_num].getWorkerIdle()
        if idle_worker:
            idle_worker.poke(kernel)



    def __scheduleShiftChanges__(self, kernel=None):

        # every 8 hours there is a new shift of workers
        shift_interval = 8 * 60 * 60 
        time_shift_change = 0

        # kernel.addEvent(0, "ShiftChangePicking")
        # kernel.addEvent(shift_interval, "ShiftChangePicking")

        # for the time being, only 2 shift changes

        while time_shift_change < kernel.runtime:           
            kernel.addEvent(time_shift_change, "ShiftChangePacking")
            time_shift_change += shift_interval


    def __shiftChange__(self, kernel=None):
        # create clock out tasks for old workers
        for they_call_me_the_working_man in self.workers:
            self.workers[they_call_me_the_working_man].clockOut(kernel)

        # create new workers
        for i in range(1,self.n_workers+1):
            new_worker = PackageWorker(self, kernel, i)
            self.workers[new_worker.name] = new_worker


    def __pokeWorkers__(self, kernel=None):
        for working_man in self.workers:
            # make them do something if idle
            if self.workers[working_man].idle:
                self.workers[working_man].poke(kernel)


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