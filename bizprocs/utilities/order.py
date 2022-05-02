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

        # total number of items, period
        self.n_items = self.__calcItems__()

        # how much the order is worth when shipped
        self.order_profit = self.__calcProfit__()

        # how much it'll hurt if the order is lost
        self.order_penalty = self.__calcPain__()

    # TODO - might not actually need a UID???   ....Could use order timestamp as ID
    def __createUid__(self, kernel):
        postfix = 0
        uid = str(kernel.clock) + '_' + str(postfix)

        while uid in kernel.orders:
            postfix += 1
            uid = str(kernel.clock) + '_' + str(postfix)

        return uid

    def __calcItems__(self):
        return np.array(list(self.getContent().values())).sum()

    def __calcProfit__(self):
        return cs.P1_PROFIT * self._content['P1'] + \
               cs.P2_PROFIT * self._content['P2'] + \
               cs.P3_PROFIT * self._content['P3'] + \
               cs.P4_PROFIT * self._content['P4']

    def __calcPain__(self):
        return cs.P1_PENALTY * self._content['P1'] + \
               cs.P2_PENALTY * self._content['P2'] + \
               cs.P3_PENALTY * self._content['P3'] + \
               cs.P4_PENALTY * self._content['P4']

    def getContent(self):
        return self._content

    def getOrderItemQty(self, item_id):
        return self._content[item_id]

    def getTotalItems(self):
        return self.n_items

    def getProfit(self):
        return self.order_profit

    def getPenalty(self):
        return self.order_penalty

    def isOrderExpired(self, clock):
        if clock > self._destruction_time:
            self._TOO_LATE = False

        return self._TOO_LATE