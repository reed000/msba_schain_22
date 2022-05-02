"""
Business Process :: Ordering()
Generate Orders
"""
import numpy as np
import pandas as pd
import constants as cs
import math
import warnings

from bizprocs.process import BusinessProcess
from ..utilities.order import Order

# TODO MODIFY to Full Year Orders
# ORDER_FILE = 'strategies/order_sample.csv'

# The big file
ORDER_FILE = 'strategies/final-project-2022m4_orders.csv'

class Orders(BusinessProcess):
    def __init__(self):
        super().__init__(name="Orders")
        self.__addEvent__("OrderUp",self.__newOrder__)
        self.master_orders = {}

    def startup(self, kernel=None):
        # TODO POPULATE SIMULATION: introduce distribution simulated orders

        # READ ORDERS FILE
        order_df = pd.read_csv(ORDER_FILE)

        for index, row in order_df.iterrows():
            order_dict = {
                 'P1' : row['QtyShirt'],
                 'P2' : row['QtyHoodie'],
                 'P3' : row['QtySweatpants'],
                 'P4' : row['QtySneakers']
            }

            # order validity check, if not just move along
            order_valid = Orders.__validateOrder__(order_dict, index)
            if not order_valid:
                continue

            # final paranoia check on the data
            if not order_dict:
                warnings.warn("EMPTY! {}, {}".format(order_dict, index))

            # ADD to Kernal EVENT_QUEUE, get the deconflicted time
            new_time, _ = kernel.addEvent(row['OrderTimeInSec'], "OrderUp")

            # Save Master Orders
            self.master_orders[new_time] = order_dict

    def __newOrder__(self, kernel=None):
        # Pull From Master Orders
        new_order = self.master_orders[kernel.clock]
        if not new_order:
            warnings.warn("EMPTY! {} at {}".format(new_order, kernel.clock))

        # ADD to Kernal orders queue - CREATE new ORDER()
        das_order = Order(kernel.clock, new_order)

        kernel.orders.append(das_order)

        # Poke the picker workers in case they are being lazy
        kernel.addEvent(kernel.clock + 1e-1, "PokeWorkersPicking")

    @staticmethod
    def __validateOrder__(order, order_index):
        contents = np.array(list(order.values()))
        valid = True
        if any(contents < 0) or all(contents == 0):
            warnings.warn("Order {} had non-valid entry at index {}".format(order, order_index))
            valid = False

        return valid
