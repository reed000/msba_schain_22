"""
Order Object :: Order()
"""
import numpy as np
import pandas as pd
import constants as cs

class Order():
    def __init__(self, order_time, content:dict):
        # TODO Remove Kernel dependency
        # def __init__(self, kernel, content:dict):
        # self.uid = self.__createUid__(kernel)
        # self._creation_time = kernel.clock

        # Order Creation time
        self._creation_time = order_time

        # order exp is by default 72 hours
        self._destruction_time = order_time + cs.ORDER_EXPIRATION

        # flag if the order is past 72 hours
        self._TOO_LATE = False

        # content is a dict containing the item qtys, EXAMPLE:
        # {
        #     'P1' : 0,
        #     'P2' : 0,
        #     'P3' : 0,
        #     'P4' : 0
        # }
        self._content = content

    # TODO - might not actually need a UID???   ....Could use order timestamp as ID
    def __createUid__(self, kernel):
        postfix = 0
        uid = str(kernel.clock) + '_' + str(postfix)

        while uid in kernel.orders:
            postfix += 1
            uid = str(kernel.clock) + '_' + str(postfix)

        return uid

    def getContent(self):
        return self._content

    def getOrderItemQty(self, item_id):
        return self._content[item_id]

    def isOrderExpired(self, clock):
        if clock > self._destruction_time:
            self._TOO_LATE = False

        return self._TOO_LATE