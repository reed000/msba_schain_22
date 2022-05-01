"""
Business Process :: Ordering()
Generate Orders
"""
import numpy as np
import pandas as pd
import constants as cs
import math

from bizprocs.process import BusinessProcess
from ..utilities.order import Order

# TODO MODIFY to Full Year Orders
ORDER_FILE = 'strategies/order_sample.csv'

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

            # ADD to Kernal EVENT_QUEUE
            kernel.addEvent(row['OrderTimeInSec'], "OrderUp")

            # Save Master Orders
            self.master_orders[row['OrderTimeInSec']] = order_dict

    def __newOrder__(self, kernel=None):
        # print("ORDERR UPPPP: {} - OrdersClass".format(kernel.clock))

        # Pull From Master Orders
        new_order = self.master_orders[kernel.clock]

        # ADD to Kernal orders queue - CREATE new ORDER()
        kernel.orders.append(Order(kernel.clock, new_order))

        # Poke the picker workers in case they are being lazy
        kernel.addEvent(kernel.clock + 1e-3, "PokeWorkersPicking")