"""
Packing Station Object :: Station()
"""
import numpy as np
import pandas as pd
import constants as cs

class Station():

    def __init__(self, facility=None, my_index=-99):

        # associate with creation facility object
        self.facility = facility

        # slot in facility order count array
        self.slot = my_index

        # queue of Order objects
        self.orders     = []
        self.order_len  = 0

        # worker assigned to station
        self.worker_slot = None

        # dictionary of products on station
        # unsure if we actually need to track this?
        self.inventory = {
            'P1' : 0,
            'P2' : 0,
            'P3' : 0,
            'P4' : 0
        }

    def addOrder(self, order_in):
        self.orders.append(order_in)
        self.order_len += 1
        self.facility.station_burden[self.slot] += 1

    def getNextOrder(self):
        # protect from 0 order draw
        if self.order_len <= 0:
            return None

        self.order_len -= 1
        self.facility.station_burden[self.slot] -= 1
        return self.orders.pop(0)

    def setWorker(self, worker_in=None):
        self.worker_slot = worker_in

    def getWorker(self, worker_in=None):
        return self.worker_slot

    def removeWorker(self):
        self.worker_slot = None

    def getNumOrders(self):
        return self.order_len

    def getWorkerIdle(self):
        return self.worker_slot.idle